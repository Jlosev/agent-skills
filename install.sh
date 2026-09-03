#!/usr/bin/env bash
# Install owned skills (copy) and community skills from skills-lock.json (npx skills add -g).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SCOPE="user"
INSTALL_COMMUNITY=1

usage() {
  cat <<'EOF'
Usage: ./install.sh [--user|--project] [--no-community]

  --user         copy owned skills to ~/.agents/skills (default)
  --project      copy owned skills to ./.agents/skills of the current directory
  --no-community skip npx skills add for skills-lock.json
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) SCOPE="user" ;;
    --project) SCOPE="project" ;;
    --no-community) INSTALL_COMMUNITY=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

copy_skill() {
  local name="$1"
  local dest="$2"
  mkdir -p "$dest"
  if [[ -L "$dest/$name" ]]; then
    echo "skip $name – destination is a symlink: $dest/$name"
    return 0
  fi
  rm -rf "$dest/$name"
  cp -R "$ROOT/skills/$name" "$dest/$name"
  echo "installed $name -> $dest/$name"
}

if [[ "$SCOPE" == "user" ]]; then
  DEST="${HOME}/.agents/skills"
else
  DEST="$(pwd)/.agents/skills"
fi
for name in human-doc-voice critic canvas-to-html tool-market-scout prompt-engineer; do
  copy_skill "$name" "$DEST"
done

if [[ "$INSTALL_COMMUNITY" -eq 1 && -f "$ROOT/skills-lock.json" ]]; then
  if ! command -v npx >/dev/null 2>&1; then
    echo "npx not found – skip community install. Run later: npx skills experimental_install" >&2
  else
    echo "Installing community skills from skills-lock.json (global)…"
    python3 - "$ROOT/skills-lock.json" <<'PY'
import json, subprocess, sys
from collections import defaultdict
lock = json.load(open(sys.argv[1], encoding="utf-8"))
by_source = defaultdict(list)
for name, entry in lock.get("skills", {}).items():
    src = entry.get("sourceUrl") or entry.get("source")
    if not src:
        print(f"skip {name}: no source", file=sys.stderr)
        continue
    by_source[src].append(name)
for src, names in by_source.items():
    cmd = ["npx", "--yes", "skills", "add", src, "-g", "-y", "--agent", "cursor"]
    for n in names:
        cmd.extend(["-s", n])
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)
PY
  fi
fi

echo "done"
