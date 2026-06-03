# hplan_codex

> **WHETHER before HOW** — The most expensive code is code that shouldn't have been written.

PM Build Gate for Codex CLI. Structured decision-making framework for AI-assisted product development.

[![skills](https://img.shields.io/badge/skills-26-blue)](skills/)
[![plugins](https://img.shields.io/badge/plugins-5-green)](skills/)
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

## Quick Start

1. **Copy harness templates** to your project:
```bash
cp -r hplan_codex/harness/ your-project/harness/
```

2. **Configure Codex CLI** (copy `.codex/` to your project):
```bash
cp -r hplan_codex/.codex/ your-project/.codex/
```

3. **Start with an idea**:
```
$brainstorm [your idea]
```

4. **Follow the lifecycle**:
```
$brainstorm → $socratic-question → $opp-tree → $prd → $conductor
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
