# PRD Section Map

Canonical contract for `skills/prd/SKILL.md`, `skills/conductor/SKILL.md`, and downstream generated PRDs.

Use these section numbers exactly. If a generated PRD renames a heading, keep the section number stable.

| Section | Canonical name | Required content | Primary consumers |
|---|---|---|---|
| §1 | User / ICP / Persona | ICP one-liner, 2-3 personas, verified reach channel | `prd`, `conductor` Spec Compliance, `design-shotgun`, QA Pool mapping |
| §2 | JTBD | 1-3 jobs, Switch 4 Forces | `prd`, discovery review |
| §3 | Core Problem + Value | Top problems, workflow-level solution, quantified 10x value | `prd`, build scope review |
| §4 | Decision Option Matrix | At least two options per major decision, tradeoffs, revisit signal | `prd`, architecture review |
| §5 | Out-of-Scope | 5+ explicit exclusions and revisit signals | `prd`, scope control |
| §6 | MVP Scope / Full Vision | Now/Next/Later, cogs p50/p90, Live URL target | `prd`, delivery planning |
| §7 | Agent Role + Primary Goal + Anti-Goals | Agent role, one primary goal, secondary goals, 3+ anti-goals | `prd`, `conductor` Spec Compliance, QA Pool role mapping |
| §8 | Tools & Integrations | Tools/APIs, purpose, usage condition, call limit | `prd`, QA Pool role mapping |
| §9 | Memory & Context Design | Working, long-term, and procedural memory contract | `prd`, architecture review |
| §10 | Trigger & Execution Flow | Trigger type, step-by-step flow, timeout | `prd`, implementation planning |
| §11 | Output Specification | Channel, format, length, language, tone, concrete output sample | `prd`, `conductor`, `design-shotgun`, QA checklist |
| §12 | Metrics | North Star, Business KRs, Operational KRs, mandatory cost KR, anti-metric | `prd`, `conductor`, operate handoff |
| §13 | Testable Hypotheses | Top-3 hypotheses and 2-day experiments | `prd`, assumptions review |
| §14 | Failure Modes + Human-in-the-loop | 4+ failure scenarios, detection, response, user impact, HITL triggers | `prd`, `conductor` Spec Compliance |
| §15 | QA Pool | Persona source, deterministic dev-role mapping, QA_POOL.json save contract | `prd`, `qa-checklist --mode adversarial` |

## P0 Numbering Rules

- ICP is always §1. Do not refer to §3 as the ICP section.
- Agent role is always §7. Do not use §7 for success metrics.
- Output specification is always §11.
- Metrics are always §12.
- Failure and HITL are always §14.
- QA Pool is always §15.

When docs mention a range:

- §1-6 means product/user/problem/scope.
- §7-11 means agent/execution specification.
- §12-14 means metrics/hypotheses/failure.
- §15 means QA Pool appendix.
