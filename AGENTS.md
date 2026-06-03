# hplan_codex — AGENTS.md

> **WHETHER before HOW**
> Before asking *how* to build, first ask *whether* to build.
> This is the first principle of hplan_codex.

---

## What is hplan_codex?

hplan_codex is a PM Build Gate system for Codex CLI.
It gives AI coding agents a structured decision-making framework — preventing you from building the wrong thing.

**5 plugins · 26 skills · AGENTS.md based**

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
| **hplan** | Should we build this? | brainstorm, evidence-rubric, decision-log |
| **discover** | What problem is real? | socratic-question, opp-tree, assumptions, cost-sim |
| **architect** | How should it be designed? | orchestration, memory-arch, router |
| **deliver** | How do we build and ship? | prd, conductor, sprint, roadmap |
| **operate** | How do we sustain it? | pm-engine, metrics-design, ops-review |

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
│   ├── decision-log.jsonl        ← Append-only decision log
│   └── build-gate/
│       └── cogs_result.json      ← COGS gate result
```

Copy templates from `harness/` directory of this repo to get started.

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
Score ≥ 60 → `GO`. Score < 60 → `INVESTIGATE` or `HOLD`.

---

## Determinism Boundary (P1 applied)

Every skill in hplan_codex declares what is LLM and what is deterministic.
Look for the **Determinism Boundary** table in each skill file.

Example from `$ticket-bridge`:
| Task | Method | Reason |
|---|---|---|
| Issue body → task decomposition | LLM | Classification allowed |
| Label → complexity mapping | Deterministic lookup | No LLM if-statement |
| Task ↔ issue matching | Deterministic | JSON key lookup |

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

Codex CLI settings for hplan_codex are in `.codex/config.toml`:
```toml
[agents]
max_threads = 6
max_depth = 2

[project]
doc_max_bytes = 65536
doc_fallback_filenames = ["AGENTS.md"]
```

Hooks are configured in `.codex/hooks.json`.

---

## Getting Started

1. Copy `harness/` templates to your project
2. Run `$brainstorm [your idea]` to start
3. Follow the plugin lifecycle: hplan → discover → architect → deliver → operate
4. Each gate must pass before moving to the next plugin

> "The most expensive code is code that shouldn't have been written."
