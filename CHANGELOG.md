# Changelog

---

## [0.2.0] — 2026-06-03

### Changed
- Codex CLI 0.130.0 native layout — skills moved to `skills/<name>/SKILL.md`, removed legacy file-based hooks, subagent toml, and nested config.
- Removed `.codex/hooks.json` (file-based hooks unsupported in Codex 0.130.0).
- Removed `.codex/agents/*.toml` subagent definitions (subagents are declared per-skill via `agents/openai.yaml`).
- Removed nested `[project]`/`[sandbox]` `.codex/config.toml`; added top-level `config.toml.example` (`model`, `model_reasoning_effort`, `[projects."..."]`).
- Moved `track-probe.sh` to `scripts/track-probe.sh` as a manual probe (no longer wired as an automatic hook).
- `validate_agents.py` now scans the `skills/<name>/SKILL.md` layout and validates `name` + `description` frontmatter.

### Docs
- README / README-ko: added Codex CLI install prerequisite, `$skill-installer` install flow, and the verified sandbox modes (`read-only` / `workspace-write` / `danger-full-access`).
- AGENTS.md: updated skill layout, configuration, and installation sections to the Codex 0.130.0 schema.

---

## [0.1.0] — 2026-06-03

Initial release of hplan_codex — Codex CLI port of hplan PM Build Gate.

### Added
- AGENTS.md — root entry point with WHETHER philosophy and skill invocation guide
- 5 plugins × 28 skills ported from hplan
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
