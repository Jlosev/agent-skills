#!/usr/bin/env python3
"""Facts for a Herdr update review. Reads Herdr's files and GitHub; the only thing it writes is
the state file, and only via `mark`.

  herdr_review.py since              last reviewed version, the installed one, clone bases
  herdr_review.py mark VERSION       record VERSION as reviewed (the only write command)
  herdr_review.py changelog FROM TO  changelog sections with FROM < version <= TO
  herdr_review.py keys FROM TO       default bindings that appeared or changed between FROM and TO
                                     and are missing from keys.json; bindings that were dropped or
                                     changed upstream while keys.json still carries the old one
  herdr_review.py usage              how Herdr is used here: clones, own mods and layouts, keys,
                                     settings, open spaces/tabs/programs (counts, no names)

Home: $HERDR_APP_HOME or ~/.config/herdr-app.
State: ${XDG_STATE_HOME:-~/.local/state}/herdr-update/reviewed (last reviewed version).
Changelog: the app's local cache plus GitHub tag TO. Default keymaps and the shipped layout list:
GitHub tags of herdrdev/herdr-app (defaults/keys.macos.json on macOS, defaults/keys.json elsewhere).
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path(os.environ.get("HERDR_APP_HOME") or Path.home() / ".config" / "herdr-app")
STATE = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "herdr-update" / "reviewed"
RAW = "https://raw.githubusercontent.com/herdrdev/herdr-app/v{ver}/{path}"
API = "https://api.github.com/repos/herdrdev/herdr-app/contents/{path}?ref=v{ver}"
HEAD = re.compile(r"^## \[(\d+(?:\.\d+)*)\]", re.M)
EDITED = re.compile(r"-edited(-\d+)?$")
KEYS_FILE = "defaults/keys.macos.json" if sys.platform == "darwin" else "defaults/keys.json"


class FetchError(Exception):
    pass


def ver(s):
    """Tolerant version: tuple of ints from any digit runs; `unknown` -> ()."""
    return tuple(int(x) for x in re.findall(r"\d+", s or ""))


def valid(s):
    return bool(ver(s))


def http_get(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        raise FetchError(f"{url}: HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError, UnicodeDecodeError) as e:
        raise FetchError(f"{url}: {getattr(e, 'reason', e)}")


def fetch(version, path):
    return http_get(RAW.format(ver=version, path=path))


def run(cmd, timeout=10):
    """(stdout, None) on success, (None, short reason) on any failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None, f"{cmd[0]} not found"
    except subprocess.TimeoutExpired:
        return None, f"{cmd[0]} timed out after {timeout}s"
    if r.returncode != 0:
        first = (r.stderr.strip().splitlines() or [f"exit {r.returncode}"])[0]
        return None, f"{cmd[0]} {cmd[1] if len(cmd) > 1 else ''}: {first}".replace("  ", " ")
    return r.stdout, None


def run_json(cmd):
    out, err = run(cmd)
    if err:
        return None, err
    try:
        return json.loads(out), None
    except ValueError:
        return None, f"{' '.join(cmd)}: output is not JSON"


def installed():
    out, _ = run(["herdr-app", "--version"])
    m = re.search(r"(\d+\.\d+\.\d+\S*)", out or "")
    return m.group(1) if m else None


def load(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def clones():
    """[{kind: mod|layout, name, base, version}] for everything with cloned_from; fields may be None."""
    found = []
    files = [("mod", f) for f in sorted(HOME.glob("mods/*/mod.json"))] + [("layout", f) for f in sorted(HOME.glob("layouts/*.json"))]
    for kind, f in files:
        data = load(f)
        c = data.get("cloned_from") if isinstance(data, dict) else None
        if isinstance(c, dict):
            found.append({"kind": kind, "name": f.parent.name if kind == "mod" else f.stem,
                          "base": c.get("name"), "version": c.get("version")})
    return found


def reviewed_state():
    try:
        v = STATE.read_text().strip()
    except OSError:
        return None
    return v if valid(v) else None


def cmd_since():
    cs = clones()
    for c in cs:
        print(f"clone {c['name']} ({c['kind']}, from {c['base'] or '?'}) {c['version'] or '?'}")
    state = reviewed_state()
    if state:
        print(f"reviewed {state}")
    else:
        vs = [c["version"] for c in cs if valid(c["version"])]
        print(f"reviewed {min(vs, key=ver)} (from clones)" if vs else "reviewed unknown")
    print(f"installed {installed() or 'unknown'}")
    return 0


def cmd_mark(version):
    if not valid(version):
        print(f"not a version: {version!r}", file=sys.stderr)
        return 2
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(version + "\n")
    except OSError as e:
        print(f"cannot write {STATE}: {e}", file=sys.stderr)
        return 1
    print(f"reviewed {version} -> {STATE}")
    return 0


def sections(text):
    marks = list(HEAD.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        yield m.group(1), text[m.start():end].rstrip() + "\n"


def cmd_changelog(lo, hi):
    if not (valid(lo) and valid(hi)):
        print(f"bad version range: {lo!r} {hi!r}", file=sys.stderr)
        return 2
    cache = HOME / "update-notes-cache.md"
    try:
        have = dict(sections(cache.read_text())) if cache.exists() else {}
    except OSError:
        have = {}
    in_range = lambda d: {v: s for v, s in d.items() if ver(lo) < ver(v) <= ver(hi)}
    try:
        remote = dict(sections(fetch(hi, "CHANGELOG.md")))
    except FetchError as e:
        if not any(ver(v) == ver(hi) for v in have):
            print(f"cannot get the changelog for {hi}: not in the local cache and GitHub failed ({e})", file=sys.stderr)
            return 1
        print(f"warning: GitHub unreachable ({e}); the local cache may be missing versions in the range", file=sys.stderr)
        remote = {}
    merged = {**in_range(remote), **in_range(have)}  # the local cache wins on a shared version
    if not merged:
        print(f"no changelog sections between {lo} and {hi}", file=sys.stderr)
        return 1
    print("\n".join(s for v, s in sorted(merged.items(), key=lambda kv: ver(kv[0]), reverse=True)))
    return 0


def keymap(version):
    """The platform's full default keymap at tag v<version>: {context: {key: action}}."""
    try:
        data = json.loads(fetch(version, KEYS_FILE))
    except ValueError:
        raise FetchError(f"{KEYS_FILE} at v{version} is not valid JSON")
    if not isinstance(data, dict):
        raise FetchError(f"{KEYS_FILE} at v{version} has an unexpected shape")
    return {ctx: binds for ctx, binds in data.items() if isinstance(binds, dict)}


def dumps(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def cmd_keys(lo, hi):
    if not (valid(lo) and valid(hi)):
        print(f"bad version range: {lo!r} {hi!r}", file=sys.stderr)
        return 2
    try:
        old, new = keymap(lo), keymap(hi)
    except FetchError as e:
        print(f"cannot get default keymaps: {e}", file=sys.stderr)
        return 1
    ours = load(HOME / "keys.json")
    if not isinstance(ours, dict):
        print("no keys.json of ours: Herdr uses its defaults, nothing to add")
        return 0
    ours_binds = {c: b for c, b in ours.items() if isinstance(b, dict)}
    old_actions = {dumps(a) for b in old.values() for a in b.values()}
    n = 0
    for ctx, binds in new.items():
        for key, action in binds.items():
            if old.get(ctx, {}).get(key) == action:
                continue
            mine = ours_binds.get(ctx, {}).get(key)
            if mine == action:
                continue
            kind = "restored default" if dumps(action) in old_actions else "new action"
            # The same action on another key of ours is a deliberate rebinding, not a gap.
            elsewhere = [k for b in ours_binds.values() for k, a in b.items() if a == action]
            if elsewhere:
                state = f"action already on {', '.join(elsewhere)}"
            else:
                state = "free" if mine is None else f"key taken by ours: {dumps(mine)}"
            print(f"{ctx}  {json.dumps(key)}: {json.dumps(action, ensure_ascii=False)}  [{kind}] ({state})")
            n += 1
    for ctx, binds in old.items():
        for key, action in binds.items():
            if new.get(ctx, {}).get(key) == action:
                continue
            if ours_binds.get(ctx, {}).get(key) != action:
                continue
            if key in new.get(ctx, {}):
                state = f"changed upstream: now {json.dumps(new[ctx][key], ensure_ascii=False)}"
            else:
                state = "dropped"
            print(f"{ctx}  {json.dumps(key)}: {json.dumps(action, ensure_ascii=False)}  [{state}] (keys.json still has the old binding)")
            n += 1
    if not n:
        print(f"no default binding changes between {lo} and {hi} that affect keys.json")
    return 0


def shipped_layouts(version):
    """Names of shipped layouts at tag v<version>, or None when it cannot be determined."""
    try:
        items = json.loads(http_get(API.format(path="defaults/layouts", ver=version)))
        return {i["name"][:-5] for i in items if i.get("name", "").endswith(".json")}
    except (FetchError, ValueError, TypeError, KeyError):
        return None


def walk_mods(node):
    if isinstance(node, dict):
        if isinstance(node.get("mod"), str):
            yield node["mod"]
        for v in node.values():
            yield from walk_mods(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_mods(v)


def join(names):
    return ", ".join(names) or "-"


def cmd_usage():
    """How this person uses Herdr: counts and program kinds only, no paths."""
    cs = clones()
    clone_names = {c["name"] for c in cs}
    mod_clones = sorted(c["name"] for c in cs if c["kind"] == "mod")
    layout_clones = sorted(c["name"] for c in cs if c["kind"] == "layout")
    shipped_mods = set((load(HOME / "installed.json") or {}).keys())
    mod_dirs = sorted(p.name for p in HOME.glob("mods/*") if p.is_dir() and not p.name.startswith("."))
    layout_files = sorted(p.stem for p in HOME.glob("layouts/*.json"))
    version = installed()
    shipped_l = shipped_layouts(version) if version else None

    def is_edited(n):
        return bool(EDITED.search(n))

    edited = sorted(n for n in mod_dirs + layout_files if is_edited(n) and n not in clone_names)
    own_mods = [n for n in mod_dirs if n not in shipped_mods and n not in clone_names and not is_edited(n)]
    print(f"mods: {len(mod_clones)} clones ({join(mod_clones)}), {len(own_mods)} own ({join(own_mods)})")
    cand = [n for n in layout_files if n not in clone_names and not is_edited(n)]
    print(f"layout clones: {join(layout_clones)}")
    if shipped_l is None:
        print(f"layouts not clones (shipped list of {version or '?'} unavailable offline, cannot tell own from shipped): {join(cand)}")
    else:
        print(f"own layouts: {join([n for n in cand if n not in shipped_l])}")
    print(f"edited copies of shipped (compare with shipped): {join(edited)}")

    status, serr = run_json(["herdr-app", "status"])
    ls, lerr = run_json(["herdr-app", "ls"])
    active = status.get("layout") if isinstance(status, dict) else None
    layout = load(HOME / "layouts" / f"{active}.json") if active else None
    used = sorted(set(walk_mods(layout))) if layout else []
    print(f"layout: {active or 'unknown'}; mods in it: {join(used)}")

    keys = load(HOME / "keys.json")
    if not isinstance(keys, dict):
        print("keys.json: defaults")
    else:
        nb = sum(len(b) for b in keys.values() if isinstance(b, dict))
        try:
            defaults = json.loads(fetch(version, KEYS_FILE)) if version else None
            if defaults is None:
                raise FetchError("installed version unknown")
            verdict = f"same as defaults of {version}" if defaults == keys else f"own (differs from defaults of {version})"
        except (FetchError, ValueError) as e:
            verdict = f"own, defaults of {version or '?'} unavailable ({e})"
        print(f"keys.json: {verdict}, {nb} bindings (replaces defaults)")
    print(f"settings.json keys set: {join(sorted((load(HOME / 'settings.json') or {}).keys()))}")

    if serr or lerr or not isinstance(ls, dict):
        print(f"window not reachable: {serr or lerr or 'herdr-app ls returned an unexpected shape'}")
        return 0
    sp = ls.get("spaces", [])
    remote = {s.get("machine") for s in sp if s.get("machine")}
    terms = [t for s in sp for tab in s.get("tabs", []) for t in tab.get("terminals", [])]
    apps = {}
    for t in terms:
        apps[t.get("app") or "shell"] = apps.get(t.get("app") or "shell", 0) + 1
    subs = sum(len(t.get("sub_agents") or []) for t in terms)
    tabs = sum(len(s.get("tabs", [])) for s in sp)
    print(f"open now: {len(sp)} spaces ({len(remote)} remote machines), {tabs} tabs, {len(terms)} terminals, {subs} sub-agents")
    print("programs: " + ", ".join(f"{k} {v}" for k, v in sorted(apps.items(), key=lambda x: -x[1])))
    return 0


def main(argv):
    if argv[:1] == ["since"]:
        return cmd_since()
    if argv[:1] == ["usage"]:
        return cmd_usage()
    if len(argv) == 2 and argv[0] == "mark":
        return cmd_mark(argv[1])
    if len(argv) == 3 and argv[0] in ("changelog", "keys"):
        return (cmd_changelog if argv[0] == "changelog" else cmd_keys)(argv[1], argv[2])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
