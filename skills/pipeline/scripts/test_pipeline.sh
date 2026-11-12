#!/usr/bin/env bash
# Self-tests for pipeline.py: every gate must fail when it should.
# Run: bash skills/pipeline/scripts/test_pipeline.sh   (macOS and Linux)
set -u
PY="python3 -I $(cd "$(dirname "$0")" && pwd)/pipeline.py"
T=$(cd "$(mktemp -d "${TMPDIR:-/tmp}/pipeline-test.XXXXXX")" && pwd -P)
trap 'rm -rf "$T"' EXIT
fails=0
check() { if [ "$2" -eq 0 ]; then echo "ok   $1"; else echo "FAIL $1"; fails=$((fails + 1)); fi; }
# setst FILE key=json ... : portable in-place edit of a state file
setst() { f=$1; shift; python3 -I - "$f" "$@" <<'EOF'
import json, sys
p = sys.argv[1]; d = json.load(open(p))
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1); d[k] = json.loads(v)
json.dump(d, open(p, "w"))
EOF
}
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
unset CLAUDE_CODE_SESSION_ID

# --- repo fixture
R="$T/repo"; mkdir -p "$R/src/sub" "$R/tests" "$R/docs"
cd "$R" && git init -q -b main
printf 'def f():\n    return 1\n' > src/a.py
printf 'from src.a import f\n\ndef test_f():\n    assert f() == 1\n    assert f() != 2\n' > tests/test_a.py
printf 'from src.a import f\n\ndef test_g():\n    assert f()\n' > tests/test_b.py
printf '#[test]\nfn t() {\n    assert_eq!(1, 1);\n}\n' > tests/lib_test.rs
printf 'class ATest {\n  void t() { assertThat(1).isEqualTo(1); }\n}\n' > tests/ATest.java
printf 'ci:\n\techo ci\nlint:\n\techo lint\n' > Makefile
echo keep > docs/readme.md
git add -A && git commit -qm init

# --- preflight
out=$(cd "$T" && $PY preflight); rc=$?
check "preflight outside git → blocked (3)" $([ $rc -eq 3 ] && echo "$out" | grep -q '^BLOCKED not a git'; echo $?)
out=$(cd "$R" && CLAUDE_CODE_SESSION_ID=s1 $PY preflight); rc=$?
check "preflight in repo → 0" $([ $rc -eq 0 ]; echo $?)
check "preflight creates self-ignored .pipeline" $([ -f "$R/.pipeline/.gitignore" ] && [ -z "$(git -C "$R" status --porcelain)" ]; echo $?)
check "preflight lists make ci" $(echo "$out" | grep -q 'verify_candidate=make ci'; echo $?)
check "preflight reports session id" $(echo "$out" | grep -q 'session=s1'; echo $?)
check "preflight reports remote=none" $(echo "$out" | grep -q 'remote=none'; echo $?)
check "preflight guesses base without origin/HEAD" $(echo "$out" | grep -q 'base=main (guessed'; echo $?)
git -C "$R" worktree add -q "$R/.pipeline/worktrees/x" -b feat/x
W="$R/.pipeline/worktrees/x"
check "worktree under .pipeline/ → main status clean, no exclude needed" $([ -z "$(git -C "$R" status --porcelain)" ] && ! grep -q worktrees "$R/.git/info/exclude"; echo $?)
out=$(cd "$W" && $PY preflight)
check "preflight in worktree → state in main root" $(echo "$out" | grep -q "^OK state_dir=$R/.pipeline"; echo $?)

# --- diff-guard
S="$R/.pipeline/state.json"
echo '{"task":"t","phase":"execute","base":"main","worktree":".pipeline/worktrees/x","scope":["src/**/*.py","./tests/test_a.py","tests/lib_test.rs","tests/ATest.java","tests/test_b.py"],"blocked":null,"updated":"1"}' > "$S"
printf 'def f():\n    return 1  # same\n' > "$W/src/a.py"
mkdir -p "$W/src/sub" && printf 'def g():\n    return [1,2].skip(1) if False else 2\n' > "$W/src/sub/c.py"
out=$(cd "$W" && $PY diff-guard); rc=$?
check "diff-guard in-scope (**/ zero dirs, ./ prefix) → 0" $([ $rc -eq 0 ]; echo $?)
check "diff-guard .skip( in product code → no finding" $(! echo "$out" | grep -q weakened_check; echo $?)
out=$(cd "$R" && $PY diff-guard)
check "diff-guard from main root checks run worktree" $(echo "$out" | grep -q "^TREE $W"; echo $?)
mkdir -p "$W/docs/заметки" && echo x > "$W/docs/заметки/план.md"
out=$(cd "$W" && $PY diff-guard); rc=$?
check "diff-guard out-of-scope cyrillic path → 1, readable" $([ $rc -eq 1 ] && echo "$out" | grep -q 'out_of_scope docs/заметки/план.md'; echo $?)
rm -rf "$W/docs/заметки"
printf 'import pytest\nfrom src.a import f\n\n@pytest.mark.skip\ndef test_f():\n    pass\n' > "$W/tests/test_a.py"
out=$(cd "$W" && $PY diff-guard)
check "diff-guard skip marker in test → finding" $(echo "$out" | grep -q 'weakened_check tests/test_a.py'; echo $?)
check "diff-guard removed asserts → finding" $(echo "$out" | grep -q 'assertions_removed tests/test_a.py'; echo $?)
git -C "$W" checkout -q -- tests/test_a.py
git -C "$W" rm -q tests/test_b.py
out=$(cd "$W" && $PY diff-guard)
check "diff-guard deleted test file → assertions_removed" $(echo "$out" | grep -q 'assertions_removed tests/test_b.py'; echo $?)
git -C "$W" checkout -q HEAD -- tests/test_b.py
printf '#[test]\nfn t() {\n}\n' > "$W/tests/lib_test.rs"
printf 'class ATest {\n  void t() { }\n}\n' > "$W/tests/ATest.java"
out=$(cd "$W" && $PY diff-guard)
check "diff-guard Rust assert_eq! removed → finding" $(echo "$out" | grep -q 'assertions_removed tests/lib_test.rs'; echo $?)
check "diff-guard Java assertThat removed → finding" $(echo "$out" | grep -q 'assertions_removed tests/ATest.java'; echo $?)
git -C "$W" checkout -q -- tests/lib_test.rs tests/ATest.java
printf 'def f():  # noqa\n    return 1\n' > "$W/src/a.py"
out=$(cd "$W" && $PY diff-guard)
check "diff-guard linter suppression → finding" $(echo "$out" | grep -q 'weakened_check src/a.py'; echo $?)
printf 'def f():\n    return 1  # same\n' > "$W/src/a.py"
echo 'x' >> "$W/Makefile"
out=$(cd "$W" && $PY diff-guard)
check "diff-guard CI config change → finding" $(echo "$out" | grep -q 'ci_config_changed Makefile'; echo $?)
git -C "$W" checkout -q -- Makefile
mkdir -p "$W/src/__pycache__" "$W/node_modules/x" && echo b > "$W/src/__pycache__/a.cpython-314.pyc" && echo j > "$W/node_modules/x/i.js"
out=$(cd "$W" && $PY diff-guard); rc=$?
check "diff-guard ignores build artefacts (__pycache__, node_modules)" $([ $rc -eq 0 ]; echo $?)
out=$(cd "$W" && $PY diff-guard nope-ref); rc=$?
check "diff-guard unknown base → blocked (3)" $([ $rc -eq 3 ]; echo $?)
sha1=$(cd "$W" && $PY diff-guard | awk '/^DIFF_SHA/{print $2}')
printf 'def g():\n    return 3\n' > "$W/src/sub/c.py"
sha2=$(cd "$W" && $PY diff-guard | awk '/^DIFF_SHA/{print $2}')
check "diff sha changes with untracked file content" $([ -n "$sha1" ] && [ "$sha1" != "$sha2" ]; echo $?)
out=$(cd "$W" && $PY diff-guard --expect-sha "$sha1"); rc=$?
check "diff-guard --expect-sha stale → blocked (3)" $([ $rc -eq 3 ] && echo "$out" | grep -q 'stale verify'; echo $?)
out=$(cd "$W" && $PY diff-guard --expect-sha "$sha2"); rc=$?
check "diff-guard --expect-sha fresh → 0" $([ $rc -eq 0 ]; echo $?)
echo 'x' >> "$W/Makefile"; sha3=$(cd "$W" && $PY diff-guard | awk '/^DIFF_SHA/{print $2}')
out=$(cd "$W" && $PY diff-guard --expect-sha "$sha3"); rc=$?
check "diff-guard --expect-sha fresh with accepted finding → 0" $([ $rc -eq 0 ] && echo "$out" | grep -q 'FINDING ci_config_changed'; echo $?)
git -C "$W" checkout -q -- Makefile

# --- hook
TR="$T/transcript.jsonl"; printf '%s\n' '{"x":"Base directory for this skill: /u/.claude/skills/pipeline\n\n# /pipeline"}' > "$TR"
TR0="$T/other.jsonl"; echo '{"x":"hello"}' > "$TR0"
LOG="$T/notify.log"; printf '#!/bin/sh\necho "$@" >> %s\n' "$LOG" > "$T/notify"; chmod +x "$T/notify"
export PIPELINE_NOTIFY_CMD="$T/notify"
ev() { printf '{"hook_event_name":"%s","cwd":"%s","session_id":"%s","transcript_path":"%s","stop_hook_active":true,"background_tasks":%s}' "$1" "${CWD:-$W}" "${SID:-s1}" "$2" "${3:-[]}"; }
reset_guard() { rm -f "$R/.pipeline/.stop-guard.json" "$W/.pipeline/.stop-guard.json"; }

out=$(ev Stop "$TR" | $PY hook)
check "hook active run (real marker) → block" $(echo "$out" | grep -q '"decision": "block"'; echo $?)
out=$(ev Stop "$TR0" | $PY hook)
check "hook session without /pipeline → allow" $([ -z "$out" ]; echo $?)
out=$(ev Stop "$TR" '[{"type":"subagent"}]' | $PY hook)
check "hook background task running → allow" $([ -z "$out" ]; echo $?)
reset_guard; ev Stop "$TR" | $PY hook >/dev/null; ev Stop "$TR" | $PY hook >/dev/null
out=$(ev Stop "$TR" | $PY hook)
check "hook 3rd block without progress → allow + notify" $([ -z "$out" ] && grep -q 'стоит' "$LOG"; echo $?)
reset_guard; n=0
for i in 1 2 3 4 5 6 7 8; do setst "$S" "updated=\"u$i\""; o=$(ev Stop "$TR" | $PY hook); [ -n "$o" ] && n=$((n + 1)); done
check "hook touching state each time → capped at 6 blocks" $([ $n -eq 6 ]; echo $?)
reset_guard; setst "$S" 'session="s1"'
out=$(SID=s2 ev Stop "$TR" | $PY hook)
check "hook other session id (state.session) → allow" $([ -z "$out" ]; echo $?)
out=$(SID=s1 ev Stop "$TR0" | $PY hook)
check "hook state.session match → block without marker" $(echo "$out" | grep -q '"decision": "block"'; echo $?)
setst "$S" 'session=null'
mkdir -p "$W/.pipeline" && echo '*' > "$W/.pipeline/.gitignore"
echo '{"task":"own","phase":"done","blocked":null}' > "$W/.pipeline/state.json"
reset_guard; out=$(ev Stop "$TR" | $PY hook)
check "hook worktree with own done state → allow" $([ -z "$out" ]; echo $?)
rm -rf "$W/.pipeline"
setst "$S" 'blocked="need token"'
out=$(ev Stop "$TR" | $PY hook)
check "hook blocked set → allow" $([ -z "$out" ]; echo $?)
setst "$S" 'blocked=null' 'phase="clarify"'
out=$(ev Stop "$TR" | $PY hook)
check "hook clarify (dialogue) → allow" $([ -z "$out" ]; echo $?)
setst "$S" 'phase="done"'
out=$(ev Stop "$TR" | $PY hook)
check "hook phase done → allow" $([ -z "$out" ]; echo $?)
setst "$S" 'phase="verify"' 'task="x\"; echo pwned #"'
reset_guard; out=$(ev Stop "$TR" | $PY hook)
check "hook sanitizes task text" $(echo "$out" | grep -q '«x-echo-pwned-' && ! echo "$out" | grep -q 'echo pwned'; echo $?)
setst "$S" 'task="t"'
: > "$LOG"; out=$(ev StopFailure "$TR" | $PY hook)
check "hook StopFailure → no block, notifies" $([ -z "$out" ] && grep -q 'обрыв' "$LOG"; echo $?)
out=$(echo 'not json' | $PY hook); rc=$?
check "hook malformed input → silent 0" $([ $rc -eq 0 ] && [ -z "$out" ]; echo $?)
out=$(CWD="$T" ev Stop "$TR" | $PY hook)
check "hook outside git → allow" $([ -z "$out" ]; echo $?)

# tracked state is ignored (repo cannot inject a run)
Q="$T/q"; mkdir -p "$Q/.pipeline" && cd "$Q" && git init -q -b main
echo '{"task":"evil","phase":"execute","blocked":null}' > .pipeline/state.json && git add -f .pipeline/state.json && git commit -qm s
out=$(CWD="$Q" ev Stop "$TR" | $PY hook)
check "hook ignores tracked state.json" $([ -z "$out" ]; echo $?)
# legacy path is read
L="$T/l"; mkdir -p "$L/.cursor/pipeline" && cd "$L" && git init -q -b main && echo '.cursor/' > .git/info/exclude
echo '{"task":"old","phase":"execute","blocked":null}' > .cursor/pipeline/state.json
out=$(CWD="$L" ev Stop "$TR" | $PY hook)
check "hook ignores legacy .cursor/pipeline state (live 1.0 run)" $([ -z "$out" ]; echo $?)
out=$(cd "$L" && $PY preflight)
check "preflight warns about legacy run, does not move it" $(echo "$out" | grep -q 'legacy_state=.*do not move' && [ -f "$L/.cursor/pipeline/state.json" ]; echo $?)

echo "---"; [ $fails -eq 0 ] && echo "all passed" || { echo "$fails failed"; exit 1; }
