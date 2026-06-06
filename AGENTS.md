# hplan_codex — AGENTS.md

> **WHETHER before HOW**
> Before asking *how* to build, first ask *whether* to build.
> This is the first principle of hplan_codex.

---

## What is hplan_codex?

hplan_codex is a PM Build Gate system for Codex CLI.
It gives AI coding agents a structured decision-making framework — preventing you from building the wrong thing.

**5 plugins · 28 skills · AGENTS.md based**

---

## Core Principles

### P1 — Determinism First
LLM is for: classification, drafting, summarizing, natural language generation.
LLM is NOT for: routing, retry policy, status code handling, deterministic transformation.
Do not use LLM as an if-statement.

### P2 — Fail Loud
If uncertain, say so explicitly. "Done/Pass/Working" is false if there are skipped or unverified steps.
Never hide uncertainty.

### P3 — Surgical Changes
Only touch what is necessary. No adjacent refactoring. No speculative features.

### P4 — Goal-Driven Execution
Convert instructions into verifiable goals. No "done" reports without verification.

### P5 — Think Before Coding
State assumptions explicitly. If ambiguous, stop and ask instead of guessing.

---

## 5-Plugin Lifecycle

```
hplan (gate)  →  discover  →  architect  →  deliver  →  operate
   WHETHER         OPP          DESIGN        BUILD       SUSTAIN
```

| Plugin | Question | Key Skills |
|---|---|---|
| **hplan** | Should we build this? | brainstorm, evidence-rubric, decision-log, exclusions, ost |
| **discover** | What problem is real? | socratic-question, opp-tree, assumptions, cost-sim, customer-reach, hitl |
| **architect** | How should it be designed? | orchestration, memory-arch, design-token, router, strategy |
| **deliver** | How do we build and ship? | prd, conductor, sprint, roadmap, qa-checklist, stakeholder-update, build-loop |
| **operate** | How do we sustain it? | pm-engine, metrics-design, ops-review, incident, portfolio |

---

## How to Invoke Skills

### Explicit invocation
```
$socratic-question [your idea]
$opp-tree [domain or problem]
$brainstorm [idea]
$prd [feature or product]
```

### Natural language invocation
```
"Use socratic-question to challenge my assumptions about [idea]"
"Run opp-tree to map opportunities in [domain]"
"Generate a 15-section PRD for [product]"
"Start brainstorm for [idea]"
```

### Full discovery flow
```
$brainstorm → $socratic-question → $opp-tree → $assumptions → $cost-sim → $prd → $conductor
```

### All 28 Skills

For canonical `available`, `planned`, and `adapter-dependent` status, see `skills/ROUTING_REGISTRY.md`.

| Plugin | Skills |
|---|---|
| hplan | `$brainstorm` `$evidence-rubric` `$decision-log` `$exclusions` `$ost` |
| discover | `$socratic-question` `$opp-tree` `$assumptions` `$cost-sim` `$customer-reach` `$hitl` |
| architect | `$orchestration` `$memory-arch` `$design-token` `$router` `$strategy` |
| deliver | `$prd` `$conductor` `$sprint` `$roadmap` `$qa-checklist` `$stakeholder-update` `$build-loop` |
| operate | `$pm-engine` `$metrics-design` `$ops-review` `$incident` `$portfolio` |

---

## Skill Layout

Each skill lives in its own folder under `skills/`:

```
skills/
├── <skill-name>/
│   └── SKILL.md        ← frontmatter (name + description) + skill body
└── ...
```

Codex CLI discovers a skill by its folder name and reads `skills/<name>/SKILL.md`.
Subagent definitions, when a skill needs them, live alongside the skill (e.g. `skills/<name>/agents/openai.yaml`).

---

## Installation

Install hplan_codex skills directly from a Codex session:

```
$skill-installer https://github.com/kimsanguine/hplan_codex
```

This pulls the skills into your Codex CLI skills directory only.
It does not copy `harness/` templates or helper scripts into the target project.

Use `scripts/setup.sh` for project setup:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
```

`scripts/setup.sh` copies `harness/`, `AGENTS.md`, `config.toml.example`, and helper scripts such as `scripts/track-probe.sh`. See `README.md` for the manual install alternative, including `skills/` and `scripts/` copy steps.

For local pre-release verification before changes are pushed to `main`:

```bash
HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex bash scripts/setup.sh --dir=/path/to/test-project
```

---

## Harness File Structure

When running skills, hplan_codex reads and writes to a `harness/` directory in your project:

```
your-project/
├── harness/
│   ├── PRD.md                    ← 15-section PRD
│   ├── pain.md                   ← Interview evidence (3+ quotes required)
│   ├── brainstorm-assumptions.md ← Initial assumptions
│   ├── implementation-plan.md    ← WBS task breakdown
│   ├── QA_CHECKLIST.md           ← TC checklist
│   ├── decisions.jsonl           ← Append-only decision log
│   └── build-gate/
│       └── cogs_result.json      ← COGS gate result
```

Copy templates from the `harness/` directory of this repo to get started.

---

## Signal Gate

Before proceeding to build, 4 evidence files must exist in `harness/`:

| File | Minimum requirement |
|---|---|
| `pain.md` | 3+ real interview quotes with source, date, role |
| `cogs.md` | Unit economics estimated |
| `market.md` | Market sizing evidence |
| `competitors.md` | Top 3 alternatives analyzed |

Run `$evidence-rubric` to score your evidence (0-100 points).
`GO` / `build` requires score ≥ 75 plus mandatory economic pain, 2+ real interview lines, and the required real-evidence files. Score ≥ 55 without all mandatory `GO` conditions → `INVESTIGATE` / `interview`; 35-54 → `PIVOT`; <35 → `HOLD`.

Use `docs/SIGNAL_GATE_SCHEMA.md` as the canonical evidence schema. Evidence marked `ai_generated_seed` is allowed only as discovery scaffolding and scores 0; it must not be counted as real pain, market, competitor, or COGS evidence for a `GO` decision.

---

## Determinism Boundary (P1 applied)

Every skill in hplan_codex declares what is LLM and what is deterministic.
Look for the **Determinism Boundary** table in each skill file.

Example from `$sprint`:
| Task | Method | Reason |
|---|---|---|
| Plan notes → task decomposition | LLM | Classification allowed |
| Effort label → priority mapping | Deterministic lookup | No LLM if-statement |
| Task ↔ plan-item matching | Deterministic | JSON key lookup |

---

## Tool Naming Convention

Skills use the following tool names compatible with Codex CLI:

| Action | Tool |
|---|---|
| Read file | `read_file` |
| Write file | `write_file` |
| Run shell | `bash` |
| Web search | `web_search` |
| Web fetch | `web_fetch` |
| MCP tool | `mcp__<server>__<tool>` |

---

## Configuration

Codex CLI reads config from `~/.codex/config.toml` (top-level keys). See `config.toml.example` in this repo:

```toml
# Default model (verified slugs: gpt-5.5, gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, gpt-5.2)
model = "gpt-5.5"
model_reasoning_effort = "high"

# Trust this project directory
[projects."/path/to/your-project"]
trust_level = "trusted"
```

Reasoning depth is controlled by `model_reasoning_effort` (`minimal` / `low` / `medium` / `high`), not by a separate model alias.

Codex CLI 0.130.0 does not support file-based hooks. Background automation, when needed, is driven by Codex automations/rules; `scripts/track-probe.sh` is provided as a manual probe you can invoke directly.

Invoke the probe with Bash:

```bash
bash scripts/track-probe.sh
```

Currently executable: `$skill-installer`, `bash scripts/setup.sh`, `bash scripts/track-probe.sh`, and `python3 scripts/validate_agents.py`.
Planned or adapter-dependent references are maintained in `skills/ROUTING_REGISTRY.md`.

Verification commands:

```bash
python3 scripts/validate_agents.py
python3 scripts/cogs_sentinel.py --json
python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
```

---

## Getting Started

1. Install with `$skill-installer https://github.com/kimsanguine/hplan_codex` (or follow the manual steps in `README.md`)
2. Copy `harness/` templates to your project
3. Run `$brainstorm [your idea]` to start
4. Follow the plugin lifecycle: hplan → discover → architect → deliver → operate
5. Each gate must pass before moving to the next plugin

> "The most expensive code is code that shouldn't have been written."
