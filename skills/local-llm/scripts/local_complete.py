#!/usr/bin/env python3
"""Fail-closed LM Studio complete. Stdout = JSON only. Diagnostics → stderr.

Exit codes (SoT):
  0  ok
  2  server down / timeout / transport
  3  no instruct / default not downloaded / target not loaded
  4  response is not JSON or missing required keys
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_SERVER = 2
EXIT_UNAVAILABLE = 3
EXIT_BAD_JSON = 4

DEFAULT_MODEL = "google/gemma-3-12b"
DEFAULT_BASE = "http://127.0.0.1:1234/v1"
HEALTH_TIMEOUT = 5
COMPLETE_TIMEOUT = 180
LOAD_TIMEOUT = 300
DEFAULT_TTL_SEC = 900
DEFAULT_CONTEXT = 8192
DEFAULT_PARALLEL = 1
DEFAULT_GPU = "max"
EMBED_MARKERS = ("embed", "embedding")


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def base_url() -> str:
    raw = os.environ.get("LOCAL_LLM_BASE_URL", DEFAULT_BASE).rstrip("/")
    return raw


def default_model() -> str:
    return os.environ.get("LOCAL_LLM_MODEL", DEFAULT_MODEL)


def http_json(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    timeout: float = HEALTH_TIMEOUT,
    origin: str | None = None,
) -> Any:
    root = (origin or base_url()).rstrip("/")
    if path.startswith("http"):
        url = path
    elif path.startswith("/api/"):
        # /v1 → host root for native REST
        host = root[: -3] if root.endswith("/v1") else root
        url = host + path
    else:
        url = root + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Authorization": "Bearer lm-studio"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise ConnectionError(f"HTTP {exc.code} {url}") from exc
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise ConnectionError(str(exc)) from exc
    if not raw.strip():
        return {}
    return json.loads(raw)


def _is_embed(model_id: str, typ: str) -> bool:
    blob = f"{model_id} {typ}".lower()
    return any(m in blob for m in EMBED_MARKERS) or typ in {"embeddings", "embedding"}


def list_models() -> list[dict[str, Any]]:
    try:
        payload = http_json("GET", "/api/v0/models", timeout=HEALTH_TIMEOUT)
    except (ConnectionError, json.JSONDecodeError):
        payload = http_json("GET", "/models", timeout=HEALTH_TIMEOUT)
    rows = payload.get("data") or payload.get("models") or []
    if not isinstance(rows, list):
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        mid = str(row.get("id") or row.get("key") or "")
        typ = str(row.get("type") or "")
        state = str(row.get("state") or "")
        if not state:
            loaded = row.get("loaded_instances")
            state = "loaded" if loaded else "not-loaded"
        out.append({"id": mid, "type": typ, "state": state})
    return out


def instruct_models(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("id") and not _is_embed(str(r["id"]), str(r.get("type") or ""))]


def unwrap_schema(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("schema must be a JSON object")
    if raw.get("type") == "json_schema" and isinstance(raw.get("json_schema"), dict):
        inner = raw["json_schema"].get("schema")
        if isinstance(inner, dict):
            return inner
    if "schema" in raw and isinstance(raw["schema"], dict) and "properties" in raw["schema"]:
        return raw["schema"]
    return raw


def required_keys(schema: dict[str, Any]) -> list[str]:
    req = schema.get("required") or []
    return [k for k in req if isinstance(k, str)]


def parse_content(content: str, schema: dict[str, Any]) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"not JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("JSON root must be an object")
    missing = [k for k in required_keys(schema) if k not in parsed]
    if missing:
        raise ValueError(f"missing required keys: {missing}")
    return parsed


def parse_message(message: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Parse model message; fallback to reasoning_content (LM Studio bug #1971)."""
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        try:
            return parse_content(content, schema)
        except ValueError:
            pass
    reasoning = message.get("reasoning_content")
    if isinstance(reasoning, str) and reasoning.strip():
        return parse_content(reasoning, schema)
    raise ValueError("empty content")


def cmd_health() -> int:
    try:
        rows = list_models()
    except (ConnectionError, json.JSONDecodeError) as exc:
        eprint(f"health: server down ({exc})")
        return EXIT_SERVER
    instruct = instruct_models(rows)
    if not instruct:
        eprint("health: no instruct model in catalog")
        return EXIT_UNAVAILABLE
    loaded = [r["id"] for r in instruct if r.get("state") == "loaded"]
    print(
        json.dumps(
            {
                "ok": True,
                "base_url": base_url(),
                "default_model": default_model(),
                "instruct": [r["id"] for r in instruct],
                "loaded": loaded,
            },
            ensure_ascii=False,
        )
    )
    return EXIT_OK


def _env_int(name: str, default: int, *, minimum: int = 0) -> int:
    raw = os.environ.get(name, str(default))
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


def ttl_seconds() -> int:
    return _env_int("LOCAL_LLM_TTL", DEFAULT_TTL_SEC)


def load_model(model: str) -> int:
    ttl = ttl_seconds()
    ctx = _env_int("LOCAL_LLM_CONTEXT", DEFAULT_CONTEXT, minimum=512)
    parallel = _env_int("LOCAL_LLM_PARALLEL", DEFAULT_PARALLEL, minimum=1)
    gpu = os.environ.get("LOCAL_LLM_GPU", DEFAULT_GPU) or DEFAULT_GPU
    cmd = [
        "lms",
        "load",
        model,
        "--yes",
        "--gpu",
        gpu,
        "-c",
        str(ctx),
        "--parallel",
        str(parallel),
    ]
    if ttl > 0:
        cmd.extend(["--ttl", str(ttl)])
    eprint(f"complete: loading {model} gpu={gpu} ctx={ctx} parallel={parallel}" + (f" ttl={ttl}s" if ttl else ""))
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=LOAD_TIMEOUT,
        )
    except FileNotFoundError:
        eprint("complete: lms CLI not found")
        return EXIT_UNAVAILABLE
    except subprocess.TimeoutExpired:
        eprint(f"complete: lms load timeout ({LOAD_TIMEOUT}s)")
        return EXIT_UNAVAILABLE
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        eprint(f"complete: lms load failed ({proc.returncode}) {err}")
        return EXIT_UNAVAILABLE
    return EXIT_OK


def cmd_complete(prompt_path: Path, schema_path: Path, out_path: Path, model: str) -> int:
    try:
        rows = list_models()
    except (ConnectionError, json.JSONDecodeError) as exc:
        eprint(f"complete: server down ({exc})")
        return EXIT_SERVER

    instruct = {r["id"]: r for r in instruct_models(rows)}
    if model not in instruct:
        eprint(f"complete: model not in catalog: {model}")
        return EXIT_UNAVAILABLE
    if instruct[model].get("state") != "loaded":
        rc = load_model(model)
        if rc != EXIT_OK:
            return rc
        try:
            rows = list_models()
        except (ConnectionError, json.JSONDecodeError) as exc:
            eprint(f"complete: server down after load ({exc})")
            return EXIT_SERVER
        instruct = {r["id"]: r for r in instruct_models(rows)}
        if instruct.get(model, {}).get("state") != "loaded":
            eprint(f"complete: model still not loaded after lms load: {model}")
            return EXIT_UNAVAILABLE

    try:
        schema = unwrap_schema(json.loads(schema_path.read_text(encoding="utf-8")))
        prompt = prompt_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        eprint(f"complete: bad prompt/schema ({exc})")
        return EXIT_BAD_JSON

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Ответь только JSON по заданной схеме. Без markdown."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "reasoning": {"effort": "low"},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "local_complete",
                "strict": True,
                "schema": schema,
            },
        },
    }
    try:
        resp = http_json("POST", "/chat/completions", body=body, timeout=COMPLETE_TIMEOUT)
    except (ConnectionError, json.JSONDecodeError) as exc:
        eprint(f"complete: transport ({exc})")
        return EXIT_SERVER

    try:
        message = resp["choices"][0]["message"]
        if not isinstance(message, dict):
            raise ValueError("empty content")
        parsed = parse_message(message, schema)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        eprint(f"complete: bad model output ({exc})")
        return EXIT_BAD_JSON

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(parsed, ensure_ascii=False))
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LM Studio structured complete (fail-closed)")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--prompt", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--model", default=None)
    args = parser.parse_args(argv)

    if args.health:
        return cmd_health()
    if not (args.prompt and args.schema and args.out):
        eprint("need --health or --prompt --schema --out")
        return EXIT_BAD_JSON
    model = args.model or default_model()
    return cmd_complete(args.prompt, args.schema, args.out, model)


if __name__ == "__main__":
    raise SystemExit(main())
