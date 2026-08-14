# Changelog

---

## [0.2.3] — 2026-08-14

### Added
- Versioned hplan-core adapter contract: 34 canonical capabilities with 25 `native` and 9 `adapter-required` support states, nine behavioral rules, and three compatibility aliases.
- Read-only `python3 scripts/hplan_doctor.py` checks Python, Codex CLI availability, and the three first-success skills installed in `$CODEX_HOME/skills`, plus four total core snapshot artifacts: `hplan-core.lock` and three `docs/` artifacts.
- Explicit `python3 scripts/repair_hplan_core_snapshot.py --root .` local snapshot repair. It verifies the project-local `.hplan-core-snapshot/` backup, stages the four total artifacts, rolls back on a failed replacement, and rejects symlinked repair paths.

### Fixed
- CI parity tests now use the checked-in `hplan-core-fixture/` fixture pinned to the private hplan-core commit recorded in `hplan-core-fixture/PROVENANCE.json`; it is CI-only and not a runtime snapshot or repair backup, so public CI no longer requires an external core checkout.
- Documentation distinguishes the 34-capability core contract from 28 local skill folders, including the three compatibility aliases.
- Codex CLI 0.130.0 behavior is documented as a verified baseline, not as a claim about the current CLI.

## [0.2.1] — 2026-06-03

### Fixed
- `scripts/setup.sh`: fail loud on required-file download failure. Previously `curl ... || echo skip` neutralized `set -euo pipefail`, so a 404 on a required file (AGENTS.md, harness templates, scripts) printed "skip" and still ended with an "installed" success message (silent partial install). Now required vs optional files are distinguished; any required failure prints the list and exits 1.
- `scripts/setup.sh`: added unknown-argument guard.

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
