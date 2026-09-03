import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict

ACTION_MAP = {
    "command_exec": "exec",
    "file_read": "file_read",
    "file_write": "file_write",
    "tool_use": "tool_use",
    "session_start": "session_start",
    "session_end": "session_end",
    "exec": "exec",
    "read": "file_read",
    "write": "file_write",
}

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

HOOK_INTERNAL_TOOLS = {
    "afterAgentThought",
    "afterAgentResponse",
    "beforeSubmitPrompt",
    "sessionStart",
    "sessionEnd",
    "stop",
    "preCompact",
    "subagentStart",
    "subagentStop",
}

VAULT_MARKERS = ("Obsidian",)

# Align with enforce-obsidian-search.sh: Grep/Glob here is code/skills, not vault KB.
SEARCH_ALLOW_MARKERS = (".cursor/", "Meta/bin/", ".git/", ".agents/", ".tmp/")

# gryph query defaults to --limit 100 --sort asc; without overrides retro sees a tiny oldest slice.
GRYPH_QUERY_LIMIT = 50000

# stuck_session: deduped>10 flagged almost every real session (noise).
STUCK_SESSION_DEDUPED_MIN = 100

SPECULATIVE_READ_NAMES = ("AGENTS.md", "log.md")

RELATIVE_MARKERS_BY_PROJECT = {}


def project_tail_name(project_filter):
    """Extract trailing segment, e.g. 'projects/app' -> 'app'."""
    return project_filter.rstrip("/").rsplit("/", 1)[-1]


# Generic relative markers when session cwd matches --project (unknown tail).
GENERIC_PROJECT_MARKERS = (".agents/skills/", ".agents/", "Meetings/")


def gryph_env():
    """Return (gryph_path, env) or (None, None) if gryph not found."""
    home = os.path.expanduser("~")
    extra_paths = [
        f"{home}/go/bin",
        f"{home}/.cargo/bin",
        f"{home}/.local/bin",
        "/opt/homebrew/bin",
    ]
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join(extra_paths) + os.pathsep + env.get("PATH", "")
    gryph_path = shutil.which("gryph", path=env["PATH"])
    if not gryph_path:
        return None, None
    return gryph_path, env


def resolve_session_working_dirs(session_ids):
    """Resolve session WorkingDirectory via gryph session --format json."""
    gryph_path, env = gryph_env()
    if not gryph_path:
        return {}

    cwd_map = {}
    for sid in session_ids:
        if not sid or sid == "unknown":
            continue
        short_id = sid[:8] if len(sid) >= 8 else sid
        try:
            result = subprocess.run(
                [gryph_path, "session", short_id, "--format", "json"],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            data = json.loads(result.stdout)
            session = data.get("session") or {}
            cwd = session.get("WorkingDirectory") or session.get("working_directory") or ""
            if cwd:
                cwd_map[sid] = cwd
        except (subprocess.CalledProcessError, json.JSONDecodeError, OSError):
            continue
    return cwd_map


def normalize_event(event):
    """Map gryph v0.7 PascalCase schema (and legacy lowercase) to a common shape."""
    raw_action = event.get("ActionType") or event.get("action") or ""
    action = ACTION_MAP.get(str(raw_action).lower(), str(raw_action).lower())

    session_id = (
        event.get("SessionID")
        or event.get("ShortSessionID")
        or event.get("session_id")
        or "unknown"
    )

    path = event.get("Path") or event.get("file") or event.get("path") or ""
    command = event.get("Command") or event.get("command") or ""
    tool = event.get("ToolName") or event.get("tool") or ""
    exit_code = event.get("ExitCode", event.get("exit_code", 0))
    error = event.get("ErrorMessage") or event.get("error") or ""
    result_status = event.get("ResultStatus") or event.get("result_status") or ""
    timestamp = event.get("Timestamp") or event.get("timestamp") or ""
    working_dir = event.get("WorkingDir") or event.get("working_dir") or ""

    return {
        "session_id": session_id,
        "action": action,
        "path": path,
        "command": command,
        "tool": tool,
        "exit_code": exit_code,
        "error": error,
        "result_status": result_status,
        "timestamp": timestamp,
        "working_dir": working_dir,
    }


def hook_fanout_dedupe_key(norm):
    """
    Gryph logs one event per Cursor hook (beforeShell + afterShell + postToolUse).
    Collapse identical targets within the same second into one logical action.
    """
    ts_sec = norm["timestamp"][:19] if len(norm["timestamp"]) >= 19 else norm["timestamp"]
    target = norm["command"] or norm["path"] or norm["tool"]
    return (norm["session_id"], norm["action"], target, ts_sec)


def gryph_db_access_hint(stderr_text=""):
    """Return actionable hint when gryph cannot open its SQLite DB."""
    msg = stderr_text or ""
    sandbox_markers = (
        "unable to open database file (14)",
        "unable to open database file",
        "SQLITE_CANTOPEN",
    )
    if any(marker in msg for marker in sandbox_markers):
        return (
            "Gryph DB is outside the Cursor workspace sandbox "
            "(~/Library/Application Support/gryph/audit.db). "
            "Re-run the Shell tool with required_permissions: [\"all\"]. "
            "Do not treat this as a missing gryph install."
        )
    return "Please ensure gryph is installed and initialized."


def run_gryph_query(days):
    """Runs gryph query to fetch logs for the last N days."""
    gryph_path, env = gryph_env()
    if not gryph_path:
        print(
            "Error: 'gryph' command not found. Please ensure it is installed (e.g. in ~/go/bin).",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = [
        gryph_path,
        "query",
        "--since",
        f"{days}d",
        "--limit",
        str(GRYPH_QUERY_LIMIT),
        "--sort",
        "desc",
        "--format",
        "jsonl",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        print(f"Error running gryph: {stderr}", file=sys.stderr)
        print(gryph_db_access_hint(stderr), file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'gryph' command not found. Please install gryph first.", file=sys.stderr)
        sys.exit(1)


def parse_events(log_lines):
    """Parse raw JSONL into (raw_event, norm) pairs."""
    parsed = []
    for line in log_lines:
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("message") and not (event.get("action") or event.get("ActionType")):
            continue
        parsed.append((event, normalize_event(event)))
    return parsed


def event_matches_project(raw_event, norm, project_filter):
    """True if event belongs to project by Path, Command, WorkingDir, tail name, or relative markers."""
    for field in (norm["path"], norm["command"], norm["working_dir"]):
        if field and project_filter in field:
            return True

    tail = project_tail_name(project_filter)
    if tail:
        for field in (norm["path"], norm["command"], norm["working_dir"]):
            if not field:
                continue
            if f"/{tail}/" in field or field.startswith(f"{tail}/"):
                return True

        markers = RELATIVE_MARKERS_BY_PROJECT.get(tail, ())
        if not markers and norm["working_dir"] and project_filter in norm["working_dir"]:
            markers = GENERIC_PROJECT_MARKERS
        for field in (norm["path"], norm["command"]):
            if field and any(marker in field for marker in markers):
                return True

    return False


def filter_by_project(parsed_events, project_filter):
    """Two-pass project filter: collect session IDs, then include all their events."""
    if not project_filter:
        return parsed_events

    session_ids = {
        norm["session_id"]
        for _, norm in parsed_events
        if norm["session_id"] and norm["session_id"] != "unknown"
    }
    session_cwd_map = resolve_session_working_dirs(session_ids)

    matching_sessions = {
        sid for sid, cwd in session_cwd_map.items() if cwd and project_filter in cwd
    }

    for raw_event, norm in parsed_events:
        sid = norm["session_id"]
        if not sid or sid == "unknown":
            continue
        cwd = session_cwd_map.get(sid, "")
        enriched = {**norm, "working_dir": norm["working_dir"] or cwd}
        if event_matches_project(raw_event, enriched, project_filter):
            matching_sessions.add(sid)

    return [
        (raw_event, norm)
        for raw_event, norm in parsed_events
        if norm["session_id"] in matching_sessions
    ]


def is_directory_path(path):
    """Heuristic: path points to a directory, not a file."""
    if not path:
        return False
    if path.endswith("/"):
        return True
    basename = path.rsplit("/", 1)[-1]
    return "." not in basename


def is_vault_context(text):
    """True if path/command references Obsidian vault."""
    if not text:
        return False
    return any(marker in text for marker in VAULT_MARKERS)


def is_search_allow_zone(text):
    """True if Grep/Glob path is in hook-allowed code/skills zones (not vault KB)."""
    if not text:
        return False
    if any(marker in text for marker in SEARCH_ALLOW_MARKERS):
        return True
    # directory path …/.tmp without trailing slash (marker is ".tmp/")
    return text.rstrip("/").endswith("/.tmp")


def normalize_command_base(command):
    """Strip rtk prefix and whitespace for duplicate detection."""
    if not command:
        return ""
    cmd = command.strip()
    if cmd.startswith("rtk "):
        cmd = cmd[4:].strip()
    return cmd


def is_meaningful_side_effect(norm):
    """Write or shell command that likely changes state."""
    if norm["action"] == "file_write":
        return True
    if norm["action"] == "exec":
        cmd = norm["command"]
        if not cmd:
            return False
        destructive_or_mutating = ("rm ", "mv ", "git commit", "git add", "write", "tee ", "mkdir ")
        return any(marker in cmd for marker in destructive_or_mutating) or ">" in cmd
    return False


def detect_anti_patterns(session_id, raw_events, deduped_events):
    """Run all anti-pattern detectors for a single session."""
    patterns = []

    read_counts = defaultdict(int)
    command_counts = defaultdict(int)
    command_base_seconds = defaultdict(lambda: defaultdict(set))
    tool_mix = defaultdict(int)
    failed_commands = []
    mcp_errors = []

    chronological = sorted(deduped_events, key=lambda pair: pair[0]["timestamp"])
    reads_before_side_effect = 0
    speculative_targets = defaultdict(int)
    side_effect_seen = False

    for norm, raw_event in chronological:
        tool = norm["tool"]
        if tool and tool not in HOOK_INTERNAL_TOOLS:
            tool_mix[tool] += 1

        if norm["action"] == "file_read" and norm["path"]:
            read_counts[norm["path"]] += 1
            if not side_effect_seen:
                reads_before_side_effect += 1
                basename = norm["path"].rsplit("/", 1)[-1]
                if basename in SPECULATIVE_READ_NAMES:
                    speculative_targets[basename] += 1
            if is_directory_path(norm["path"]):
                pass  # handled in aggregate below

        if norm["action"] == "exec" and norm["command"]:
            base = normalize_command_base(norm["command"])
            ts_sec = norm["timestamp"][:19] if len(norm["timestamp"]) >= 19 else norm["timestamp"]
            form = "rtk" if norm["command"].strip().startswith("rtk ") else "raw"
            command_base_seconds[base][ts_sec].add(form)
            command_counts[norm["command"]] += 1
            if norm["exit_code"] not in (0, None, "0", "success"):
                failed_commands.append({"command": norm["command"], "exit_code": norm["exit_code"]})

            if "rm -rf" in norm["command"] or "rm -r " in norm["command"]:
                patterns.append({
                    "id": "destructive_shell",
                    "severity": "P0",
                    "evidence": {"command": norm["command"][:120]},
                })

        if norm["action"] == "tool_use":
            if norm["error"] or norm["result_status"] not in ("", "success", None) or raw_event.get("isError"):
                mcp_errors.append({
                    "tool": norm["tool"],
                    "error": norm["error"] or f"status={norm['result_status']}",
                })

        tool_name = norm["tool"]
        search_context = norm["path"] or norm["command"]
        if (
            tool_name in ("Grep", "Glob", "SemanticSearch")
            and is_vault_context(search_context)
            and not is_search_allow_zone(search_context)
        ):
            patterns.append({
                "id": "search_misuse",
                "severity": "P1",
                "evidence": {"tool": tool_name, "context": search_context[:120]},
            })

        if is_meaningful_side_effect(norm):
            side_effect_seen = True

    raw_count = len(raw_events)
    deduped_count = len(deduped_events)

    # re_read
    for path, count in read_counts.items():
        if count >= 2:
            patterns.append({
                "id": "re_read",
                "severity": "P1" if count >= 3 else "P2",
                "evidence": {"path": path, "count": count},
            })

    # directory_read
    dir_reads = {p: c for p, c in read_counts.items() if is_directory_path(p)}
    for path, count in dir_reads.items():
        patterns.append({
            "id": "directory_read",
            "severity": "P2",
            "evidence": {"path": path, "count": count},
        })

    # rtk_dup – ignore same-second raw+rtk pairs (RTK hook rewrite)
    for base, seconds in command_base_seconds.items():
        raw_only_seconds = []
        rtk_only_seconds = []
        for ts_sec, forms in seconds.items():
            if forms == {"raw"}:
                raw_only_seconds.append(ts_sec)
            elif forms == {"rtk"}:
                rtk_only_seconds.append(ts_sec)
        if (
            len(raw_only_seconds) >= 2
            or len(rtk_only_seconds) >= 2
            or (raw_only_seconds and rtk_only_seconds)
        ):
            patterns.append({
                "id": "rtk_dup",
                "severity": "P2",
                "evidence": {
                    "base": base[:80],
                    "raw_only_seconds": len(raw_only_seconds),
                    "rtk_only_seconds": len(rtk_only_seconds),
                },
            })

    # stuck_session – deduped count only (raw inflates via hook fan-out)
    if deduped_count >= STUCK_SESSION_DEDUPED_MIN:
        patterns.append({
            "id": "stuck_session",
            "severity": "P1",
            "evidence": {
                "raw_events": raw_count,
                "deduped_events": deduped_count,
                "threshold": STUCK_SESSION_DEDUPED_MIN,
            },
        })

    # thrash_command
    for cmd, count in command_counts.items():
        if count >= 3:
            patterns.append({
                "id": "thrash_command",
                "severity": "P1",
                "evidence": {"command": cmd[:120], "count": count},
            })

    # speculative_read
    if reads_before_side_effect > 5 and speculative_targets:
        patterns.append({
            "id": "speculative_read",
            "severity": "P2",
            "evidence": {
                "reads_before_side_effect": reads_before_side_effect,
                "targets": dict(speculative_targets),
            },
        })

    # failed_command
    for fc in failed_commands:
        patterns.append({
            "id": "failed_command",
            "severity": "P1",
            "evidence": fc,
        })

    # mcp_error
    for err in mcp_errors:
        patterns.append({
            "id": "mcp_error",
            "severity": "P1",
            "evidence": err,
        })

    return dedupe_patterns(patterns), dict(tool_mix)


def dedupe_patterns(patterns):
    """Collapse duplicate pattern IDs keeping highest severity and merged evidence."""
    by_id = {}
    for p in patterns:
        pid = p["id"]
        if pid not in by_id:
            by_id[pid] = p
            continue
        existing = by_id[pid]
        if SEVERITY_ORDER[p["severity"]] < SEVERITY_ORDER[existing["severity"]]:
            existing["severity"] = p["severity"]
        if pid in ("re_read", "directory_read", "search_misuse", "thrash_command"):
            if "items" not in existing["evidence"]:
                existing["evidence"] = {"items": [existing["evidence"]]}
            existing["evidence"]["items"].append(p["evidence"])
    return list(by_id.values())


def session_is_flagged(anti_patterns, min_severity="P2"):
    """Flag if >=1 P0/P1 or >=2 P2 patterns at or above min_severity."""
    min_rank = SEVERITY_ORDER[min_severity]
    relevant = [p for p in anti_patterns if SEVERITY_ORDER[p["severity"]] <= min_rank]
    if not relevant:
        return False
    p1_or_better = sum(1 for p in relevant if SEVERITY_ORDER[p["severity"]] <= 1)
    p2_count = sum(1 for p in relevant if p["severity"] == "P2")
    return p1_or_better >= 1 or p2_count >= 2


def process_logs(log_lines, project_filter=None, min_severity="P2"):
    """
    Process raw JSONL logs into per-session anti-pattern analysis
    plus legacy aggregate friction_points.
    """
    parsed = parse_events(log_lines)
    parsed = filter_by_project(parsed, project_filter)

    session_raw = defaultdict(list)
    session_deduped = defaultdict(list)
    seen_dedupe_keys = set()

    global_reads = defaultdict(int)
    global_writes = defaultdict(int)
    global_commands = defaultdict(int)
    global_mcp = defaultdict(int)
    global_failed = []
    global_mcp_errors = []

    for raw_event, norm in parsed:
        sid = norm["session_id"]
        if not sid or sid == "unknown":
            continue

        session_raw[sid].append((raw_event, norm))

        dedupe_key = hook_fanout_dedupe_key(norm)
        is_new_logical = dedupe_key not in seen_dedupe_keys
        if is_new_logical:
            seen_dedupe_keys.add(dedupe_key)
            session_deduped[sid].append((norm, raw_event))

        if not is_new_logical:
            continue

        if norm["action"] == "file_read" and norm["path"]:
            global_reads[norm["path"]] += 1
        elif norm["action"] == "file_write" and norm["path"]:
            global_writes[norm["path"]] += 1
        elif norm["action"] == "exec" and norm["command"]:
            global_commands[norm["command"]] += 1
            if norm["exit_code"] not in (0, None, "0", "success"):
                global_failed.append({"command": norm["command"], "exit_code": norm["exit_code"]})
        elif norm["action"] == "tool_use":
            if (
                norm["error"]
                or norm["result_status"] not in ("", "success", None)
                or raw_event.get("isError")
            ):
                global_mcp_errors.append({
                    "tool": norm["tool"],
                    "error": norm["error"] or f"status={norm['result_status']}",
                })

        if norm["tool"] and norm["tool"] not in HOOK_INTERNAL_TOOLS:
            global_mcp[norm["tool"]] += 1

    sessions_out = {}
    flagged_sessions = []

    for sid in session_raw:
        raw_list = session_raw[sid]
        deduped_list = session_deduped.get(sid, [])
        anti_patterns, tool_mix = detect_anti_patterns(sid, raw_list, deduped_list)

        sessions_out[sid] = {
            "raw_events": len(raw_list),
            "deduped_events": len(deduped_list),
            "tool_mix": tool_mix,
            "anti_patterns": anti_patterns,
        }

        if session_is_flagged(anti_patterns, min_severity):
            flagged_sessions.append(sid)

    total_raw = sum(s["raw_events"] for s in sessions_out.values())
    total_deduped = sum(s["deduped_events"] for s in sessions_out.values())
    long_sessions = {
        sid: d["deduped_events"]
        for sid, d in sessions_out.items()
        if d["deduped_events"] >= STUCK_SESSION_DEDUPED_MIN
    }
    thrashing_commands = {k: v for k, v in global_commands.items() if v > 3}

    flagged_sessions.sort(key=lambda sid: sessions_out[sid]["raw_events"], reverse=True)

    return {
        "metrics": {
            "total_events_analyzed": total_raw,
            "deduped_logical_events": total_deduped,
            "unique_sessions": len(sessions_out),
            "flagged_sessions_count": len(flagged_sessions),
            "long_stuck_sessions_count": len(long_sessions),
        },
        "flagged_sessions": flagged_sessions,
        "sessions": sessions_out,
        "friction_points": {
            "failed_commands": global_failed[:20],
            "mcp_errors": global_mcp_errors[:20],
            "thrashing_commands": thrashing_commands,
            "long_stuck_sessions": long_sessions,
            "highly_read_files": {k: v for k, v in global_reads.items() if v > 4},
            "highly_written_files": {k: v for k, v in global_writes.items() if v > 4},
        },
        "tool_usage": dict(global_mcp),
    }


def main():
    parser = argparse.ArgumentParser(description="Extract and condense Gryph logs for AI Retro analysis.")
    parser.add_argument("--days", type=int, default=3, help="Number of days to look back (default: 3)")
    parser.add_argument("--project", type=str, help="Optional path filter (e.g., 'projects/my-app')")
    parser.add_argument(
        "--min-severity",
        type=str,
        default="P2",
        choices=["P0", "P1", "P2", "P3"],
        help="Minimum severity for flagging sessions (default: P2)",
    )

    args = parser.parse_args()

    log_lines = run_gryph_query(args.days)
    condensed_summary = process_logs(log_lines, args.project, args.min_severity)

    if condensed_summary["metrics"]["total_events_analyzed"] == 0:
        condensed_summary["status"] = "empty"
        condensed_summary["hint"] = (
            "No events in the selected window. First retry gryph commands with "
            "required_permissions: [\"all\"] — Cursor sandbox shows false zeroes in "
            "gryph status and blocks ~/Library/Application Support/gryph/audit.db. "
            "If query is still empty with full permissions and hooks are active, "
            "check workspace .cursor/hooks.json — it replaces ~/.cursor/hooks.json; "
            "merge gryph via .cursor/hooks/gryph-audit.sh and restart Cursor."
        )

    print(json.dumps(condensed_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
