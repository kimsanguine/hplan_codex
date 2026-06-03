#!/usr/bin/env bash
# track-probe.sh — sprint tracking probe
# Run manually or via Codex automation — file-based PostToolUse hooks are
# not supported in Codex CLI 0.130.0.
# Reads a tool-call JSON payload on stdin and appends a write event to
# .track/actual_log.jsonl. No forbidden brand references.

set -euo pipefail

TRACK_DIR=".track"
LOG="$TRACK_DIR/actual_log.jsonl"

[ -d "$TRACK_DIR" ] || exit 0

INPUT="$(cat)"

echo "$INPUT" | python3 -c '
import json, sys, datetime, os

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = d.get("tool_name", "")
if tool not in ("write_file", "apply_patch"):
    sys.exit(0)

inp = d.get("tool_input", {}) or {}
file_path = inp.get("file_path", "") or inp.get("path", "")

def nlines(s):
    return len(s.splitlines()) if s else 0

if tool == "write_file":
    loc_delta = nlines(inp.get("content", ""))
else:
    loc_delta = nlines(inp.get("new_content", ""))

task = "unassigned"
ct = os.path.join(".track", "current_task")
if os.path.exists(ct):
    task = open(ct).read().strip() or "unassigned"

entry = {
    "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "task": task,
    "event": "tool_call",
    "tool": tool,
    "file": file_path,
    "loc_delta": loc_delta,
    "source": "probe",
}
with open(os.path.join(".track", "actual_log.jsonl"), "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
' 2>>".track/probe-errors.log" || true

exit 0
