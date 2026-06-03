#!/usr/bin/env bash
# setup.sh — hplan_codex harness installer
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
# Or:    bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh) --dir=./myproject
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
DEFAULT_TARGET="."

TARGET_DIR="${1:-$DEFAULT_TARGET}"
for arg in "$@"; do
  case "$arg" in
    --dir=*) TARGET_DIR="${arg#--dir=}" ;;
    --help|-h)
      echo "Usage: bash setup.sh [--dir=<target-project-dir>]"
      echo "  --dir  Target project directory (default: current directory)"
      exit 0
      ;;
  esac
done

echo "hplan_codex harness installer"
echo "Target: $TARGET_DIR"
echo ""

# 1) Check dependencies
for cmd in curl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: '$cmd' is required but not found." >&2
    exit 1
  fi
done

# 2) Create target directory if needed
mkdir -p "$TARGET_DIR"

# 3) Copy harness templates
echo "Copying harness/ templates..."
HARNESS_FILES=(
  "PRD.md.template"
  "pain.md.template"
  "brainstorm-assumptions.md.template"
  "cogs.md.template"
  "market.md.template"
  "competitors.md.template"
)
mkdir -p "$TARGET_DIR/harness"
for f in "${HARNESS_FILES[@]}"; do
  curl -fsSL "$RAW_BASE/harness/$f" -o "$TARGET_DIR/harness/$f" 2>/dev/null && \
    echo "  ok harness/$f" || echo "  skip harness/$f" >&2
done

# 4) Copy AGENTS.md
echo "Copying AGENTS.md..."
curl -fsSL "$RAW_BASE/AGENTS.md" -o "$TARGET_DIR/AGENTS.md" && \
  echo "  ok AGENTS.md" || echo "  skip AGENTS.md" >&2

# 5) Copy config example
echo "Copying config.toml.example..."
curl -fsSL "$RAW_BASE/config.toml.example" -o "$TARGET_DIR/config.toml.example" 2>/dev/null && \
  echo "  ok config.toml.example" || echo "  skip config.toml.example" >&2

# 6) Copy scripts
echo "Copying scripts/..."
mkdir -p "$TARGET_DIR/scripts"
for f in cogs_sentinel.py validate_agents.py track-probe.sh; do
  curl -fsSL "$RAW_BASE/scripts/$f" -o "$TARGET_DIR/scripts/$f" 2>/dev/null && \
    echo "  ok scripts/$f" || echo "  skip scripts/$f" >&2
done
chmod +x "$TARGET_DIR/scripts/track-probe.sh" 2>/dev/null || true

echo ""
echo "hplan_codex harness installed to: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. Install the skills in a Codex session:"
echo "       \$skill-installer https://github.com/kimsanguine/hplan_codex"
echo "  2. (optional) Copy config.toml.example keys to ~/.codex/config.toml"
echo "  3. cd $TARGET_DIR and run Codex CLI in this directory"
echo "  4. Start: \$brainstorm \"your idea\""
echo ""
echo "Full workflow:"
echo "  \$brainstorm → \$socratic-question → \$opp-tree → \$prd → \$conductor"
