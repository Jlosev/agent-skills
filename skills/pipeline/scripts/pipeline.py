#!/usr/bin/env python3
"""Deterministic helpers for the /pipeline skill.

  pipeline.py preflight                    check workspace, create .pipeline/, list verify candidates
  pipeline.py diff-guard [BASE] [--expect-sha SHA]
                                           out-of-scope files, weakened checks, diff fingerprint
  pipeline.py hook                         Claude Code Stop / StopFailure hook (JSON on stdin)

Exit codes: 0 ok, 1 findings (diff-guard), 3 blocked.
"""
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

STATE_DIR = ".pipeline"
LEGACY_STATE = os.path.join(".cursor", "pipeline", "state.json")
MARKERS = (rb"<command-name>/pipeline", rb"skills/pipeline\n", "Using /pipeline –".encode())
SLUG = re.compile(r"[^A-Za-z0-9._-]+")
NO_PROGRESS_BLOCKS = 2      # consecutive blocks without any progress
BLOCKS_PER_PHASE = 6        # hard cap per session and phase
GIT = ["git", "-c", "core.quotePath=false"]


def git(args, cwd, timeout=30):
    try:
        r = subprocess.run([*GIT, *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def toplevel(cwd):
    return git(["rev-parse", "--show-toplevel"], cwd)


def main_root(cwd):
    """Main checkout root, also inside a linked worktree; falls back to toplevel (submodules)."""
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    if common and os.path.basename(common) == ".git":
        return os.path.dirname(common)
    return toplevel(cwd)


def is_tracked(root, path):
    rel = os.path.relpath(path, root)
    return bool(git(["ls-files", "--", rel], root))


def find_state(cwd, legacy=False):
    """State of the run that owns cwd: own worktree first, then the main checkout.
    The 1.0 path (.cursor/pipeline) is read only on request: it may belong to a live 1.0 session."""
    top, root = toplevel(cwd), main_root(cwd)
    if not root:
        return None, None, None
    candidates = []
    for base in dict.fromkeys(p for p in (top, root) if p):
        candidates.append((base, os.path.join(base, STATE_DIR, "state.json")))
    if legacy:
        candidates.append((root, os.path.join(root, LEGACY_STATE)))
    for base, p in candidates:
        if os.path.exists(p) and not is_tracked(base, p):
            try:
                with open(p, encoding="utf-8") as f:
                    return json.load(f), p, root
            except (OSError, ValueError):
                return None, p, root
    return None, os.path.join(root, STATE_DIR, "state.json"), root


# ---------------------------------------------------------------- preflight

def verify_candidates(root):
    out = []
    mk = os.path.join(root, "Makefile")
    if os.path.exists(mk):
        text = open(mk, encoding="utf-8", errors="replace").read()
        targets = re.findall(r"^([A-Za-z0-9_./-]+):(?!=)", text, re.M)
        out += [f"make {t}" for t in targets if re.search(r"ci|check|test|lint|verify|e2e", t)]
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        try:
            scripts = json.load(open(pkg, encoding="utf-8")).get("scripts", {})
            out += [f"npm run {k}" for k in scripts if re.search(r"ci|check|test|lint|typecheck|e2e", k)]
        except ValueError:
            pass
    wf = os.path.join(root, ".github", "workflows")
    if os.path.isdir(wf):
        out += [f"ci: .github/workflows/{n}" for n in sorted(os.listdir(wf)) if n.endswith((".yml", ".yaml"))]
    return out


def preflight(cwd):
    blocked, ok = [], []
    top = toplevel(cwd)
    if not top:
        print(f"BLOCKED not a git repository: {cwd} → cd into the project repo and rerun /pipeline")
        return 3
    root = main_root(cwd) or top
    ok.append(f"root={root}")
    if top != root:
        ok.append(f"worktree={top}")
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
    ok.append(f"session={sid or 'unknown'} (write it to state.session)")

    d = os.path.join(root, STATE_DIR)
    try:
        os.makedirs(d, exist_ok=True)
        gi = os.path.join(d, ".gitignore")
        if not os.path.exists(gi):
            with open(gi, "w") as f:
                f.write("*\n")
        probe = os.path.join(d, ".probe")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        ok.append(f"state_dir={d}")
    except OSError as e:
        blocked.append(f"cannot write {d}: {e.strerror} → allow writes to the project dir (/sandbox or permission prompt)")

    legacy = os.path.join(root, LEGACY_STATE)
    if os.path.exists(legacy) and not os.path.exists(os.path.join(d, "state.json")):
        ok.append(f"legacy_state={legacy} (a /pipeline 1.0 run: do not move or resume it unless the user says so; new task → own worktree and state)")

    ok.append(f"branch={git(['rev-parse', '--abbrev-ref', 'HEAD'], top)}")
    upstream = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], top)
    ok.append(f"upstream={upstream or 'none'}")
    base = git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], root)
    if not base:
        for b in ("origin/main", "origin/master", "main", "master"):
            if git(["rev-parse", "--verify", "--quiet", b], root):
                base = f"{b} (guessed: origin/HEAD not set)"
                break
    ok.append(f"base={base or 'unknown → ruling: pick the branch PRs go to'}")
    ok.append(f"dirty={'yes' if git(['status', '--porcelain'], top) else 'no'}")

    remote = git(["remote", "get-url", "origin"], root)
    if remote:
        reach = git(["ls-remote", "--exit-code", "origin", "HEAD"], root, timeout=15)
        ok.append("remote=ok" if reach is not None else
                  "remote=unreachable (fetch/push will fail: ask for network or auth now if the run must push)")
        if "github.com" in remote:
            if not shutil.which("gh"):
                ok.append("gh=missing (PR step will need it)")
            else:
                r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
                ok.append("gh=ok" if r.returncode == 0 else "gh=not-authenticated (PR step will need `gh auth login`)")
    else:
        ok.append("remote=none")

    for c in verify_candidates(root):
        ok.append(f"verify_candidate={c}")
    for line in ok:
        print("OK", line)
    for line in blocked:
        print("BLOCKED", line)
    return 3 if blocked else 0


# --------------------------------------------------------------- diff-guard

TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec|specs|e2e|testing)(/|$)|"
                       r"(_test|\.test|\.spec|_spec|Test|Tests|IT)\.[A-Za-z]+$|(^|/)test_[^/]+$")
SKIP_IN_TESTS = re.compile(
    r"\.skip\(|\.only\(|\bxit\(|\bxdescribe\(|\bit\.todo\(|@pytest\.mark\.(skip|xfail)|pytest\.skip\(|"
    r"\bt\.Skip\(|@Disabled|@Ignore\b|unittest\.skip|#\[ignore\]|\bskip\s*\(\s*\)")
SUPPRESS_ANY = re.compile(
    r"eslint-disable|@ts-ignore|@ts-expect-error|#\s*noqa|type:\s*ignore|//\s*nolint|#\[allow\(|"
    r"@SuppressWarnings|--passWithNoTests|continue-on-error:\s*true|\|\|\s*true\b")
ASSERT = re.compile(r"\bassert\w*!?\s*\(|\bassert\b|self\.assert\w+|\bexpect\s*\(|\.should\b|"
                    r"\bassertThat\b|\bt\.(Error|Fatal)\w*\(|\brequire\.\w+\(|\bXCTAssert\w*")
SNAPSHOT = re.compile(r"__snapshots__/|\.snap$|(^|/)golden/|\.golden$")
CI_PATH = re.compile(r"(^|/)\.github/workflows/|(^|/)\.gitlab-ci|(^|/)\.circleci/|(^|/)Makefile$|"
                     r"(^|/)(pytest\.ini|tox\.ini|setup\.cfg|pyproject\.toml|package\.json|tsconfig[^/]*\.json|"
                     r"jest\.config[^/]*|vitest\.config[^/]*|playwright\.config[^/]*|\.eslintrc[^/]*|eslint\.config[^/]*|"
                     r"ruff\.toml|\.pre-commit-config\.yaml)$")


def norm_glob(g, top):
    g = g.strip()
    if os.path.isabs(g):
        g = os.path.relpath(g, top)
    while g.startswith("./"):
        g = g[2:]
    return g


def in_scope(path, globs):
    for g in globs:
        if not g:
            continue
        if path == g or path.startswith(g.rstrip("/") + "/"):
            return True
        variants = {g, g.replace("**/", ""), g.replace("/**", "")}
        if any(fnmatch.fnmatchcase(path, v) for v in variants):
            return True
        if g.endswith("/**") and path.startswith(g[:-3] + "/"):
            return True
    return False


ARTIFACT = re.compile(r"(^|/)(__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|node_modules|\.tox|\.venv|"
                      r"\.DS_Store|htmlcov|\.coverage|\.next|\.turbo|\.pipeline)(/|$)|\.py[co]$")


def untracked(top):
    """Untracked files without build artefacts (a run of tests must not look like a scope breach)."""
    out = (git(["ls-files", "--others", "--exclude-standard"], top) or "").splitlines()
    return [n for n in out if n and not ARTIFACT.search(n)]


def diff_fingerprint(top, mb, names):
    h = hashlib.sha256()
    h.update((git(["diff", "--no-renames", "--binary", mb], top) or "").encode())
    for n in sorted(untracked(top)):
        h.update(n.encode())
        h.update((git(["hash-object", "--", n], top) or "missing").encode())
    return h.hexdigest()[:16]


def diff_guard(cwd, base, expect_sha):
    st, _, root = find_state(cwd)
    st = st or {}
    top = toplevel(cwd)
    if not top:
        print("BLOCKED not a git repository")
        return 3
    wt = st.get("worktree")
    if wt and top == root:  # run from the main checkout → check the run's worktree
        cand = wt if os.path.isabs(wt) else os.path.join(root, wt)
        if os.path.isdir(cand):
            top = toplevel(cand) or top
    base = base or (st.get("base") or "origin/main").split(" ")[0]
    mb = git(["merge-base", base, "HEAD"], top)
    if not mb:
        print(f"BLOCKED unknown base {base} → git fetch, or pass BASE")
        return 3

    names = set((git(["diff", "--no-renames", "--name-only", mb], top) or "").splitlines())
    names |= set(untracked(top))
    names.discard("")
    patch = git(["diff", "--no-renames", "-U0", mb], top) or ""

    findings = []
    scope = [norm_glob(g, top) for g in (st.get("scope") or [])]
    if scope:
        arts = st.get("artifacts") or {}
        allowed = scope + [norm_glob(arts.get(k) or "", top) for k in ("plan", "spec")]
        findings += [f"out_of_scope {n}" for n in sorted(names) if not in_scope(n, allowed)]
    else:
        findings.append("no_scope state.scope is empty → copy file paths from the plan into state.scope")

    cur, added, removed = None, {}, {}
    for line in patch.splitlines():
        if line.startswith("diff --git"):
            cur = None
            continue
        if line.startswith("--- "):
            cur = line[6:] if line.startswith("--- a/") else cur
            continue
        if line.startswith("+++ "):
            if line.startswith("+++ b/"):
                cur = line[6:]
            continue
        if cur is None or not line[:1] in "+-":
            continue
        body = line[1:]
        is_test = bool(TEST_PATH.search(cur))
        if line.startswith("+"):
            if (is_test and SKIP_IN_TESTS.search(body)) or SUPPRESS_ANY.search(body):
                findings.append(f"weakened_check {cur}: {body.strip()[:120]}")
        if is_test and ASSERT.search(body):
            bucket = added if line.startswith("+") else removed
            bucket[cur] = bucket.get(cur, 0) + 1
    for f, n in sorted(removed.items()):
        if n > added.get(f, 0):
            findings.append(f"assertions_removed {f}: -{n} +{added.get(f, 0)}")
    for n in sorted(names):
        if SNAPSHOT.search(n):
            findings.append(f"snapshot_changed {n}")
        if CI_PATH.search(n):
            findings.append(f"ci_config_changed {n}")

    sha = diff_fingerprint(top, mb, names)
    print(f"BASE {base} {mb[:12]}")
    print(f"TREE {top}")
    print(f"DIFF_SHA {sha} files={len(names)}")
    if expect_sha and expect_sha != sha:
        print(f"BLOCKED stale verify: state.verify.diff_sha={expect_sha} ≠ {sha} → rerun verify.cmd and record the new sha")
        return 3
    for f in findings:
        print("FINDING", f)
    if not findings:
        print("OK no findings")
    if expect_sha:  # freshness mode: findings were already judged at verify time
        print("OK fresh: code unchanged since verify")
        return 0
    return 1 if findings else 0


# --------------------------------------------------------------------- hook

def transcript_runs_pipeline(path):
    if not path:
        return False
    try:
        with open(os.path.expanduser(path), "rb") as f:
            data = f.read()
    except OSError:
        return False
    return any(m in data for m in MARKERS)


def owns_run(st, ev):
    """Session binding: state.session if recorded, else the transcript shows a /pipeline invocation."""
    if st.get("session"):
        return st["session"] == ev.get("session_id")
    return transcript_runs_pipeline(ev.get("transcript_path"))


def notify(title, text, level="warn"):
    cmd = os.environ.get("PIPELINE_NOTIFY_CMD") or shutil.which("lan-notify")
    if not cmd:
        return
    try:
        subprocess.run([cmd, "-s", "agent-pipeline", "-l", level, "-t", title, text],
                       capture_output=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        pass


def hook(raw):
    try:
        ev = json.loads(raw or "{}")
    except ValueError:
        return 0
    name = ev.get("hook_event_name")
    if name not in ("Stop", "StopFailure"):
        return 0
    cwd = ev.get("cwd") or os.getcwd()
    st, path, root = find_state(cwd)
    if not st or st.get("phase") in (None, "done") or st.get("blocked"):
        return 0
    if not owns_run(st, ev):
        return 0
    task = SLUG.sub("-", str(st.get("task", "run")))[:60] or "run"
    phase = SLUG.sub("-", str(st.get("phase")))[:20]

    if name == "StopFailure":
        notify(f"/pipeline {task}: обрыв",
               f"Ход упал на ошибке API ({SLUG.sub('-', str(ev.get('error', 'unknown')))}), фаза {phase}. "
               f"Напиши в сессии «продолжай» — прогон продолжит по state.")
        return 0
    if ev.get("background_tasks") or phase == "clarify":
        return 0  # waiting for background work / brainstorming dialogue with the user

    guard_path = os.path.join(os.path.dirname(path), ".stop-guard.json")
    try:
        guards = json.load(open(guard_path))
    except (OSError, ValueError):
        guards = {}
    sid = str(ev.get("session_id"))
    g = guards.get(sid, {})
    head = git(["rev-parse", "HEAD"], cwd)
    mark = [st.get("updated"), head]
    if g.get("phase") != phase:
        g = {"phase": phase, "in_phase": 0, "noprog": 0, "mark": None}
    g["noprog"] = g["noprog"] + 1 if g.get("mark") == mark else 1
    g["in_phase"] += 1
    g["mark"], g["at"] = mark, int(time.time())
    guards[sid] = g
    try:
        with open(guard_path, "w") as f:
            json.dump(guards, f)
    except OSError:
        pass
    if g["noprog"] > NO_PROGRESS_BLOCKS or g["in_phase"] > BLOCKS_PER_PHASE:
        notify(f"/pipeline {task}: стоит",
               f"Агент остановился на фазе {phase} без blocked. Загляни в сессию.")
        return 0
    print(json.dumps({
        "decision": "block",
        "reason": (f"/pipeline «{task}» не закончен, фаза {phase}. Продолжай по {path}. "
                   f"Ждёшь ответа пользователя или он просил паузу — запиши причину в state.blocked и закончи ход. "
                   f"Ждёшь долгую команду — запусти её фоново."),
    }, ensure_ascii=False))
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd, rest = argv[1], argv[2:]
    if cmd == "preflight":
        return preflight(os.getcwd())
    if cmd == "diff-guard":
        expect = None
        if "--expect-sha" in rest:
            i = rest.index("--expect-sha")
            expect = rest[i + 1] if i + 1 < len(rest) else ""
            rest = rest[:i] + rest[i + 2:]
        return diff_guard(os.getcwd(), rest[0] if rest else None, expect)
    if cmd == "hook":
        try:
            return hook(sys.stdin.read())
        except Exception:  # a hook must never break the session
            return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
