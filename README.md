# hplan_codex

> **WHETHER before HOW** — The most expensive code is code that shouldn't have been written.

> 🇰🇷 한국어 가이드: [README-ko.md](README-ko.md)

PM Build Gate for Codex CLI. Structured decision-making framework for AI-assisted product development.

[![skills](https://img.shields.io/badge/skills-28-blue)](skills/)
[![plugins](https://img.shields.io/badge/plugins-5-green)](skills/)
[![Codex CLI](https://img.shields.io/badge/Codex%20CLI-0.130.0+-black)](https://developers.openai.com/codex)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## The Problem

AI coding agents are fast. Too fast.
They'll build whatever you ask — wrong product, right velocity.

hplan_codex adds a **WHETHER gate** before the HOW:
- Is this the right problem to solve?
- Do we have real evidence of pain?
- Can we afford to run this at scale?

---

## 5-Plugin Lifecycle

```
hplan → discover → architect → deliver → operate
```

| Plugin | Question | Top Skills |
|---|---|---|
| **hplan** | Should we build? | brainstorm, evidence-rubric |
| **discover** | What's the real problem? | socratic-question, opp-tree, assumptions |
| **architect** | How to design it? | orchestration, memory-arch |
| **deliver** | How to build & ship? | prd, conductor, sprint |
| **operate** | How to sustain it? | pm-engine, metrics-design |

---

## Prerequisite: Install Codex CLI

hplan_codex runs inside the OpenAI Codex CLI. **Install it first:**

```bash
npm install -g @openai/codex
```

Official docs and other install options: https://developers.openai.com/codex

---

## Install hplan_codex

**Recommended — install skills from inside a Codex session:**

```
$skill-installer https://github.com/kimsanguine/hplan_codex
```

This pulls the 28 skills into your Codex CLI skills directory. It does **not**
copy project harness files or helper scripts into the repo you are working on.

**Project setup — copy harness files and scripts into your project:**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
```

`scripts/setup.sh` copies `harness/` templates, `AGENTS.md`, `config.toml.example`,
and helper scripts such as `scripts/track-probe.sh`. It does **not** install
Codex skills; use `$skill-installer` for that.

For local pre-release verification before changes are pushed to `main`:

```bash
HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex bash scripts/setup.sh --dir=/path/to/test-project
```

**Manual alternative** (clone + skills + harness setup):

```bash
git clone https://github.com/kimsanguine/hplan_codex.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R hplan_codex/skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -r hplan_codex/harness/ ./harness/
cp -r hplan_codex/scripts/ ./scripts/
cp hplan_codex/AGENTS.md ./AGENTS.md
# optional: keep a config example for manual merge; do not overwrite your live config
mkdir -p "${CODEX_HOME:-$HOME/.codex}"
cp -n hplan_codex/config.toml.example "${CODEX_HOME:-$HOME/.codex}/config.toml.example"
```

---

## First 10 Minute Success Path

After installing (above), confirm the first useful loop from your project folder:

1. Open the project in Codex CLI.
2. Run `$brainstorm "your idea here"`.
3. Capture the first WHETHER judgment: `GO`, `INVESTIGATE`, or `HOLD`.
4. If the idea is still alive, create or update `harness/pain.md` with real evidence, not AI-generated seed text.
5. Run `$evidence-rubric` and keep the score plus missing-evidence notes.

Expected first success: a documented build/no-build judgment within 10 minutes, plus the next evidence action.

**Full workflow:**

```
$brainstorm → $socratic-question → $opp-tree → $prd → $conductor
```

Reference docs:
- [Glossary](docs/GLOSSARY.md)
- [Illustrative case studies](docs/CASE_STUDIES.md)
- [Contributing](CONTRIBUTING.md)

---

## Security & Sandbox

hplan_codex runs inside Codex CLI's sandbox. Codex 0.130.0 supports three sandbox modes:

| Mode | Access |
|---|---|
| `read-only` | Read project files only — no writes, no network |
| `workspace-write` | Read + write project files + run commands in the workspace (default) |
| `danger-full-access` | Full read/write + network — use only when you trust the task |

Set the sandbox mode in your Codex CLI session or config. hplan_codex skills assume `workspace-write` for the build phases.

> Codex CLI 0.130.0 does not support file-based hooks. `scripts/track-probe.sh` is provided as a manual sprint-tracking probe you can run yourself with `bash scripts/track-probe.sh` or wire into a Codex automation.

## Status & Verification

Currently executable:
- Skill installation via `$skill-installer`
- Harness/script bootstrap via `bash scripts/setup.sh`
- Manual probe invocation via `bash scripts/track-probe.sh`
- Static skill/doc validation via `python3 scripts/validate_agents.py`

Planned or adapter-dependent capabilities are tracked in
[skills/ROUTING_REGISTRY.md](skills/ROUTING_REGISTRY.md).

Canonical references:
- PRD numbering contract: [docs/PRD_SECTION_MAP.md](docs/PRD_SECTION_MAP.md)
- Signal Gate evidence schema: [docs/SIGNAL_GATE_SCHEMA.md](docs/SIGNAL_GATE_SCHEMA.md)
- Skill status registry: [skills/ROUTING_REGISTRY.md](skills/ROUTING_REGISTRY.md)

Verification commands:

```bash
python3 scripts/validate_agents.py
python3 scripts/cogs_sentinel.py --json
python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
mkdir -p .track
printf '%s\n' track-smoke > .track/current_task
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
test -s .track/actual_log.jsonl
```

---

## Skill Invocation

```
$skill-name [arguments]

Examples:
$socratic-question "AI legal document review SaaS"
$opp-tree "legal tech for SMEs"
$prd "contract review agent"
$cost-sim "LLM-based document analysis"
```

Or use natural language:
```
"Challenge my assumptions about [idea] using socratic-question"
"Map opportunities in [domain] with opp-tree"
```

---

## Core Principles

**P1 — Determinism First**: LLM for classification and prose. Not for routing or if-statements.
**P2 — Fail Loud**: Never hide uncertainty. "Done" means verified.
**P3 — Surgical Changes**: Touch only what's necessary.
**P4 — Goal-Driven**: No "done" without verification evidence.

---

## License

MIT
