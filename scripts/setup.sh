#!/usr/bin/env bash
# setup.sh — hplan_codex installer
# Usage: bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
# Or:    bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh) --dir=./myproject

set -euo pipefail

REPO_URL="https://github.com/kimsanguine/hplan_codex.git"
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

echo "hplan_codex installer"
echo "Target: $TARGET_DIR"
echo ""

# 1) Check dependencies
for cmd in git curl; do
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
    echo "  ✓ harness/$f" || echo "  ✗ harness/$f (skipped)" >&2
done

# 4) Copy .codex/ configuration
echo "Copying .codex/ configuration..."
CODEX_FILES=(
  "config.toml"
  "hooks.json"
  "agents/spec-reviewer.toml"
  "agents/quality-reviewer.toml"
  "agents/implementer.toml"
  "scripts/track-probe.sh"
)
mkdir -p "$TARGET_DIR/.codex/agents"
mkdir -p "$TARGET_DIR/.codex/scripts"
for f in "${CODEX_FILES[@]}"; do
  curl -fsSL "$RAW_BASE/.codex/$f" -o "$TARGET_DIR/.codex/$f" 2>/dev/null && \
    echo "  ✓ .codex/$f" || echo "  ✗ .codex/$f (skipped)" >&2
done
chmod +x "$TARGET_DIR/.codex/scripts/track-probe.sh" 2>/dev/null || true

# 5) Copy AGENTS.md
echo "Copying AGENTS.md..."
curl -fsSL "$RAW_BASE/AGENTS.md" -o "$TARGET_DIR/AGENTS.md" && \
  echo "  ✓ AGENTS.md" || echo "  ✗ AGENTS.md (skipped)" >&2

# 6) Copy scripts
echo "Copying scripts/..."
mkdir -p "$TARGET_DIR/scripts"
for f in cogs_sentinel.py validate_agents.py; do
  curl -fsSL "$RAW_BASE/scripts/$f" -o "$TARGET_DIR/scripts/$f" 2>/dev/null && \
    echo "  ✓ scripts/$f" || echo "  ✗ scripts/$f (skipped)" >&2
done

echo ""
echo "hplan_codex installed to: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Run Codex CLI in this directory"
echo "  3. Start: \$brainstorm \"your idea\""
echo ""
echo "Full workflow:"
echo "  \$brainstorm → \$socratic-question → \$opp-tree → \$prd → \$conductor"
