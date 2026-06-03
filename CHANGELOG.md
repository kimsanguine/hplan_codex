# Changelog

---

## [0.1.0] — 2026-06-03

Initial release of hplan_codex — Codex CLI port of hplan PM Build Gate.

### Added
- AGENTS.md — root entry point with WHETHER philosophy and skill invocation guide
- 5 plugins × 26 skills ported from hplan
- `.codex/` configuration (config.toml, hooks.json, subagent definitions)
- `harness/` templates (PRD, pain, brainstorm-assumptions)
- `scripts/` (cogs_sentinel.py, validate_agents.py)

### Plugins
- **hplan** (5 skills): brainstorm, decision-log, evidence-rubric, exclusions, ost
- **discover** (6 skills): socratic-question, opp-tree, assumptions, cost-sim, customer-reach, hitl
- **architect** (5 skills): orchestration, memory-arch, design-token, router, strategy
- **deliver** (7 skills): prd, conductor, sprint, roadmap, qa-checklist, stakeholder-update, build-loop
- **operate** (5 skills): pm-engine, metrics-design, ops-review, incident, portfolio

### Not Ported
- `ui-validate` — Playwright sandbox constraints
- `reliability` — `context: fork` not supported in Codex CLI
- `ticket-bridge`, `ask-team`, `stakeholder-review` — MCP-heavy, port in v0.2
