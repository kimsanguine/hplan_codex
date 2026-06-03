# hplan_codex

> **WHETHER before HOW** — The most expensive code is code that shouldn't have been written.

> 🇰🇷 한국어 가이드: [README-ko.md](README-ko.md)

PM Build Gate for Codex CLI. Structured decision-making framework for AI-assisted product development.

[![skills](https://img.shields.io/badge/skills-28-blue)](skills/)
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

**5-minute start** (after cloning):
```
$brainstorm "your idea here"
```

**Full setup** (for complete workflow):

**0. Get hplan_codex**
```bash
git clone https://github.com/kimsanguine/hplan_codex.git
cd your-project
```

1. Copy harness templates to your project:
   ```bash
   cp -r ../hplan_codex/harness/ ./harness/
   cp -r ../hplan_codex/.codex/ ./.codex/
   cp ../hplan_codex/AGENTS.md ./AGENTS.md
   ```
2. Run Codex CLI in your project folder
3. Start:
   ```
   $brainstorm "your idea"
   ```

---

## Security & Sandbox

hplan_codex runs in Codex CLI's **workspace-write** sandbox by default.

| Mode | Access |
|---|---|
| `workspace-read` | Read project files only (spec-reviewer, quality-reviewer) |
| `workspace-write` | Read + write project files + run bash (implementer, default) |

**Hooks**: Three automatic hooks run in the background:
- `SessionStart`: Checks for `harness/` directory
- `PostToolUse`: Logs file writes to `.track/actual_log.jsonl`
- `Stop`: Validates skill files

**To disable hooks**: Delete or empty `.codex/hooks.json`
**To use read-only mode**: Set `default_sandbox_mode = "workspace-read"` in `.codex/config.toml`

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
