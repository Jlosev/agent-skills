#!/usr/bin/env python3
"""Unit tests for local_complete.py (mocked HTTP)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from local_complete import (
    DEFAULT_MODEL,
    EXIT_BAD_JSON,
    EXIT_OK,
    EXIT_SERVER,
    EXIT_UNAVAILABLE,
    load_model,
    main,
)


def _ok_models_payload(*, loaded_ids: list[str] | None = None) -> dict:
    loaded_ids = loaded_ids or []
    return {
        "data": [
            {
                "id": "text-embedding-qwen3-embedding-0.6b",
                "type": "embeddings",
                "state": "loaded" if "text-embedding-qwen3-embedding-0.6b" in loaded_ids else "not-loaded",
            },
            {
                "id": "google/gemma-3-12b",
                "type": "llm",
                "state": "loaded" if "google/gemma-3-12b" in loaded_ids else "not-loaded",
            },
            {
                "id": "google/gemma-4-26b-a4b-qat",
                "type": "llm",
                "state": "loaded" if "google/gemma-4-26b-a4b-qat" in loaded_ids else "not-loaded",
            },
        ]
    }


class LocalCompleteTests(unittest.TestCase):
    def test_health_server_down(self) -> None:
        with patch("local_complete.http_json", side_effect=ConnectionRefusedError("down")):
            rc = main(["--health"])
        self.assertEqual(rc, EXIT_SERVER)

    def test_health_only_embedding(self) -> None:
        payload = {
            "data": [
                {
                    "id": "text-embedding-qwen3-embedding-0.6b",
                    "type": "embeddings",
                    "state": "loaded",
                }
            ]
        }
        with patch("local_complete.http_json", return_value=payload):
            rc = main(["--health"])
        self.assertEqual(rc, EXIT_UNAVAILABLE)

    def test_health_ok(self) -> None:
        with patch("local_complete.http_json", return_value=_ok_models_payload()):
            rc = main(["--health"])
        self.assertEqual(rc, EXIT_OK)

    def test_complete_ok(self) -> None:
        schema = {"type": "object", "properties": {"joke": {"type": "string"}}, "required": ["joke"]}
        models = _ok_models_payload(loaded_ids=[DEFAULT_MODEL])
        chat = {"choices": [{"message": {"content": json.dumps({"joke": "x"}, ensure_ascii=False)}}]}

        def fake_http(method: str, path: str, **kwargs):
            if path.endswith("/models"):
                return models
            self.assertEqual(method, "POST")
            return chat

        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "p.txt"
            schema_path = Path(tmp) / "s.json"
            out = Path(tmp) / "out.json"
            prompt.write_text("tell a joke", encoding="utf-8")
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            with patch("local_complete.http_json", side_effect=fake_http):
                rc = main(["--prompt", str(prompt), "--schema", str(schema_path), "--out", str(out)])
            self.assertEqual(rc, EXIT_OK)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8")), {"joke": "x"})

    def test_complete_bad_json(self) -> None:
        schema = {"type": "object", "properties": {"joke": {"type": "string"}}, "required": ["joke"]}
        models = _ok_models_payload(loaded_ids=[DEFAULT_MODEL])
        chat = {"choices": [{"message": {"content": "not-json"}}]}

        def fake_http(method: str, path: str, **kwargs):
            if path.endswith("/models"):
                return models
            return chat

        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "p.txt"
            schema_path = Path(tmp) / "s.json"
            out = Path(tmp) / "out.json"
            prompt.write_text("tell a joke", encoding="utf-8")
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            with patch("local_complete.http_json", side_effect=fake_http):
                rc = main(["--prompt", str(prompt), "--schema", str(schema_path), "--out", str(out)])
            self.assertEqual(rc, EXIT_BAD_JSON)
            self.assertFalse(out.exists())

    def test_complete_reasoning_content_fallback(self) -> None:
        schema = {"type": "object", "properties": {"joke": {"type": "string"}}, "required": ["joke"]}
        models = _ok_models_payload(loaded_ids=[DEFAULT_MODEL])
        chat = {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "reasoning_content": json.dumps({"joke": "from-reasoning"}, ensure_ascii=False),
                    }
                }
            ]
        }

        def fake_http(method: str, path: str, **kwargs):
            if path.endswith("/models"):
                return models
            return chat

        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "p.txt"
            schema_path = Path(tmp) / "s.json"
            out = Path(tmp) / "out.json"
            prompt.write_text("tell a joke", encoding="utf-8")
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            with patch("local_complete.http_json", side_effect=fake_http):
                rc = main(["--prompt", str(prompt), "--schema", str(schema_path), "--out", str(out)])
            self.assertEqual(rc, EXIT_OK)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8")), {"joke": "from-reasoning"})

    def test_complete_autoload(self) -> None:
        schema = {"type": "object", "properties": {"joke": {"type": "string"}}, "required": ["joke"]}
        unloaded = _ok_models_payload(loaded_ids=[])
        loaded = _ok_models_payload(loaded_ids=[DEFAULT_MODEL])
        chat = {"choices": [{"message": {"content": json.dumps({"joke": "x"})}}]}
        calls = {"models": 0}

        def fake_http(method: str, path: str, **kwargs):
            if path.endswith("/models"):
                calls["models"] += 1
                return unloaded if calls["models"] == 1 else loaded
            return chat

        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "p.txt"
            schema_path = Path(tmp) / "s.json"
            out = Path(tmp) / "out.json"
            prompt.write_text("tell a joke", encoding="utf-8")
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            with patch("local_complete.http_json", side_effect=fake_http):
                with patch("local_complete.load_model", return_value=EXIT_OK) as load:
                    rc = main(["--prompt", str(prompt), "--schema", str(schema_path), "--out", str(out)])
            load.assert_called_once_with(DEFAULT_MODEL)
            self.assertEqual(rc, EXIT_OK)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8")), {"joke": "x"})

    def test_load_model_passes_ttl(self) -> None:
        with patch("local_complete.subprocess.run") as run:
            run.return_value.returncode = 0
            run.return_value.stderr = ""
            run.return_value.stdout = ""
            with patch.dict("os.environ", {"LOCAL_LLM_TTL": "120"}, clear=False):
                rc = load_model(DEFAULT_MODEL)
        self.assertEqual(rc, EXIT_OK)
        cmd = run.call_args.args[0]
        self.assertIn("--ttl", cmd)
        self.assertIn("120", cmd)
        self.assertIn("--gpu", cmd)
        self.assertIn("max", cmd)
        self.assertIn("-c", cmd)
        self.assertIn("8192", cmd)
        self.assertIn("--parallel", cmd)
        self.assertIn("1", cmd)

    def test_complete_load_fails(self) -> None:
        schema = {"type": "object", "properties": {"joke": {"type": "string"}}, "required": ["joke"]}
        models = _ok_models_payload(loaded_ids=[])

        with tempfile.TemporaryDirectory() as tmp:
            prompt = Path(tmp) / "p.txt"
            schema_path = Path(tmp) / "s.json"
            out = Path(tmp) / "out.json"
            prompt.write_text("tell a joke", encoding="utf-8")
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            with patch("local_complete.http_json", return_value=models):
                with patch("local_complete.load_model", return_value=EXIT_UNAVAILABLE):
                    rc = main(["--prompt", str(prompt), "--schema", str(schema_path), "--out", str(out)])
            self.assertEqual(rc, EXIT_UNAVAILABLE)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
