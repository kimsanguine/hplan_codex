#!/usr/bin/env bash
# setup.sh — hplan_codex harness installer
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
# Or:    bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh) --dir=./myproject
# Local pre-release test:
#        HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex bash scripts/setup.sh --dir=./myproject
#
# This copies the harness templates, AGENTS.md, and helper scripts into your
# project. To install the SKILLS, run the following inside a Codex session
# (recommended):
#
#     $skill-installer https://github.com/kimsanguine/hplan_codex
#
# Prerequisite: install Codex CLI first — `npm install -g @openai/codex`
# (docs: https://developers.openai.com/codex)

set -euo pipefail

RAW_BASE="https://raw.githubusercontent.com/kimsanguine/hplan_codex/main"
SOURCE_DIR="${HPLAN_CODEX_SOURCE_DIR:-}"
TARGET_DIR="."

for arg in "$@"; do
  case "$arg" in
    --dir=*) TARGET_DIR="${arg#--dir=}" ;;
    --help|-h)
      echo "Usage: bash setup.sh [--dir=<target-project-dir>]"
      echo "  --dir  Target project directory (default: current directory)"
      echo "  HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex  Copy from a local checkout instead of GitHub raw"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Run with --help for usage." >&2
      exit 1
      ;;
  esac
done

echo "hplan_codex harness installer"
echo "Target: $TARGET_DIR"
if [ -n "$SOURCE_DIR" ]; then
  echo "Source: $SOURCE_DIR"
fi
echo ""

# 1) Check dependencies
if ! command -v curl &>/dev/null; then
  echo "Error: 'curl' is required but not found." >&2
  exit 1
fi
if [ -n "$SOURCE_DIR" ] && [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: HPLAN_CODEX_SOURCE_DIR does not exist: $SOURCE_DIR" >&2
  exit 1
fi

# 2) Create target directory if needed
mkdir -p "$TARGET_DIR"

# Track failures. Required-file failures are fatal; optional ones only warn.
FAILED_REQUIRED=()
FAILED_OPTIONAL=()

# fetch <url-suffix> <dest> <required|optional>
fetch() {
  local suffix="$1" dest="$2" level="$3"
  if [ -n "$SOURCE_DIR" ] && [ -f "$SOURCE_DIR/$suffix" ]; then
    cp "$SOURCE_DIR/$suffix" "$dest"
    echo "  ok  $suffix"
  elif [ -n "$SOURCE_DIR" ]; then
    if [ "$level" = "required" ]; then
      echo "  FAIL (required) $suffix" >&2
      FAILED_REQUIRED+=("$suffix")
    else
      echo "  skip (optional) $suffix" >&2
      FAILED_OPTIONAL+=("$suffix")
    fi
  elif curl -fsSL "$RAW_BASE/$suffix" -o "$dest" 2>/dev/null; then
    echo "  ok  $suffix"
  else
    if [ "$level" = "required" ]; then
      echo "  FAIL (required) $suffix" >&2
      FAILED_REQUIRED+=("$suffix")
    else
      echo "  skip (optional) $suffix" >&2
      FAILED_OPTIONAL+=("$suffix")
    fi
  fi
}

# 3) Copy harness templates (required — they are the gate inputs)
echo "Copying harness/ templates..."
mkdir -p "$TARGET_DIR/harness"
for f in PRD.md.template pain.md.template brainstorm-assumptions.md.template \
         cogs.md.template market.md.template competitors.md.template; do
  fetch "harness/$f" "$TARGET_DIR/harness/$f" required
done

# 4) Copy AGENTS.md (required — entry point)
echo "Copying AGENTS.md..."
fetch "AGENTS.md" "$TARGET_DIR/AGENTS.md" required

# 5) Copy config example (optional)
echo "Copying config.toml.example..."
fetch "config.toml.example" "$TARGET_DIR/config.toml.example" optional

# 6) Copy scripts (required)
echo "Copying scripts/..."
mkdir -p "$TARGET_DIR/scripts"
for f in cogs_sentinel.py decision_log.py exclusions_registry.py generate_report.py \
         interview_synthesis.py ost_generator.py validate-mermaid.py validate_agents.py \
         track-probe.sh hplan_doctor.py; do
  fetch "scripts/$f" "$TARGET_DIR/scripts/$f" required
done
chmod +x "$TARGET_DIR/scripts/track-probe.sh" 2>/dev/null || true

# 7) Copy hplan-core snapshot (required — doctor uses it read-only)
echo "Copying hplan-core snapshot..."
mkdir -p "$TARGET_DIR/docs"
fetch "hplan-core.lock" "$TARGET_DIR/hplan-core.lock" required
for f in hplan-capability-matrix.json HPLAN_CAPABILITY_MATRIX.md hplan-core-adapter.json; do
  fetch "docs/$f" "$TARGET_DIR/docs/$f" required
done

# 8) Fail loud on required-file failures (no false "installed" success)
echo ""
if [ "${#FAILED_REQUIRED[@]}" -gt 0 ]; then
  echo "ERROR: ${#FAILED_REQUIRED[@]} required file(s) failed to download:" >&2
  for f in "${FAILED_REQUIRED[@]}"; do echo "  - $f" >&2; done
  echo "Install is INCOMPLETE. Check your network/branch and re-run." >&2
  exit 1
fi
if [ "${#FAILED_OPTIONAL[@]}" -gt 0 ]; then
  echo "Note: ${#FAILED_OPTIONAL[@]} optional file(s) skipped: ${FAILED_OPTIONAL[*]}"
fi

echo "hplan_codex harness installed to: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. Install the skills in a Codex session:"
echo "       \$skill-installer https://github.com/kimsanguine/hplan_codex"
echo "  2. (optional) Copy config.toml.example keys to ~/.codex/config.toml"
echo "  3. cd $TARGET_DIR and run Codex CLI in this directory"
echo "  4. Check: python3 scripts/hplan_doctor.py"
echo "  5. Start: \$brainstorm \"your idea\""
echo ""
echo "Full workflow:"
echo "  \$brainstorm -> \$socratic-question -> \$opp-tree -> \$prd -> \$conductor"
