# hplan_codex — AGENTS.md

> **WHETHER before HOW**
> Before asking *how* to build, first ask *whether* to build.
> This is the first principle of hplan_codex.

---

## What is hplan_codex?

hplan_codex is a PM Build Gate system for Codex CLI.
It gives AI coding agents a structured decision-making framework — preventing you from building the wrong thing.

**5 plugins · 28 local skill folders · AGENTS.md based**

---

## 9 Behavioral Rules

### Rule 1 — Think Before Coding
State material assumptions. If ambiguity changes the outcome, request clarification before acting.

### Rule 2 — Simplicity First
Use the minimum implementation that satisfies the stated need; do not add speculative features.

### Rule 3 — Surgical Changes
Change only the requested surface and preserve intentional surrounding work.

### Rule 4 — Goal-Driven Execution
Translate work into verifiable goals and cite verification before completion.

### Rule 5 — Models for Judgment Tasks Only
Use models for drafting, summarizing, classification, and judgment tasks. Use deterministic logic for deterministic control decisions such as routing, retry policy, status handling, and transformations.

### Rule 6 — Tests Verify Intent
Design tests that fail when the intended behavior changes; do not treat a passing command as customer-facing proof.

### Rule 7 — Checkpoint After Every Significant Step
After significant work, state what changed, what was verified, and what remains.

### Rule 8 — Fail Loud
Expose uncertainty and incomplete verification; do not present skipped work as complete.

### Rule 9 — Agent Scope Declaration
Declare the permitted work scope before delegated execution. Stop for approval before irreversible actions.

## Codex Adapter Truth Boundary

`hplan-core.lock` and `docs/hplan-capability-matrix.json` are the Codex snapshot of the core contract. Read a capability's `support_state` before invoking it:

- `native` is the only state that may be presented as directly available in this environment.
- `adapter-required` is not active. It needs a target adapter; use its local fallback artifact or produce a draft only.
- `unavailable` is not active. Do not invoke it; use only its documented local/draft-only fallback.

External connector writes remain disabled. This package may create local artifacts and drafts, but it does not activate, authorize, or write through external connectors.

### Compatibility aliases

| Alias | Compatibility route | Boundary |
| --- | --- | --- |
| roadmap | roadmap → prd --mode roadmap | Compatibility alias; preserve the mode. |
| router | router → orchestration --pattern router | Compatibility alias; preserve the pattern. |
| stakeholder-update | stakeholder-update → ops-review | Compatibility alias; draft-only unless a separately authorized adapter exists. |

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

### Bundled local skill folders

The 28 local folders below are not a claim of core-native support. For every core capability, use `docs/hplan-capability-matrix.json` as the authoritative support state; non-native capabilities remain adapter-required or unavailable with local/draft-only fallbacks.

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

설치 직후에는 아래 읽기 전용 doctor를 실행한다:

```bash
python3 scripts/hplan_doctor.py
```

doctor는 Python, 가능한 Codex CLI 버전, `hplan-core.lock`과 네 개의 core artifact 일치성을 검사한다. `정상`이면 `$brainstorm "아이디어"`로 시작한다. `자동 복구 가능`이면 `python3 scripts/repair_hplan_core_snapshot.py --root .`를 명시적으로 실행한 뒤 doctor를 재실행한다. 이 복구 명령은 포함된 로컬 백업의 snapshot artifact 4개만 바꾸며 doctor 자체는 쓰지 않는다. `강사 호출`은 core snapshot mismatch이며, 임의 덮어쓰기 대신 출력 내용을 유지해 패키지 관리자에게 전달한다.

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

Currently executable: `$skill-installer`, `bash scripts/setup.sh`, `bash scripts/track-probe.sh`, `python3 scripts/hplan_doctor.py` (read-only), `python3 scripts/repair_hplan_core_snapshot.py --root .` (explicit local snapshot repair), and `python3 scripts/validate_agents.py`.
Planned or adapter-dependent references are maintained in `skills/ROUTING_REGISTRY.md`.

Verification commands:

```bash
python3 scripts/validate_agents.py
python3 scripts/hplan_doctor.py
python3 scripts/cogs_sentinel.py --json
# Core snapshot parity test에는 어느 위치의 hplan-core checkout이든 지정한다.
HPLAN_CORE_DIR=/path/to/hplan-core python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
```

---

## Getting Started

1. Install with `$skill-installer https://github.com/kimsanguine/hplan_codex` (or follow the manual steps in `README.md`)
2. Copy `harness/` templates to your project and run `python3 scripts/hplan_doctor.py`
3. Start with `$brainstorm [your idea]` because it records the first WHETHER judgment
4. Use `$socratic-question` next to expose high-risk assumptions
5. Use `$evidence-rubric` to name the missing real evidence before a `GO` decision
6. Follow the plugin lifecycle: hplan → discover → architect → deliver → operate

> "The most expensive code is code that shouldn't have been written."
