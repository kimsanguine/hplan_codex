# hplan_codex Markdown Persona Review

Date: 2026-06-05
Repo: `/Users/sanguinekim/Documents/3_Code/Vibe/Project/hplan_codex`
Scope: all Markdown files returned by `rg --files -g '*.md'`

## Executive Summary

Six AI reviewer personas read the Markdown documentation and skill files from independent perspectives:

1. Senior CPO / Product Strategy
2. Agent Architect / Multi-agent Systems
3. Developer Experience / Installer & CLI Usability
4. QA / E2E Verification and Release Risk
5. Korean Technical Documentation / Education
6. GTM / Adoption and Open Source Packaging

Central verification found 32 Markdown files:

- Root docs: `AGENTS.md`, `README.md`, `README-ko.md`, `CHANGELOG.md`
- Skills: 28 `skills/*/SKILL.md` files

Overall verdict: hplan_codex has a strong product philosophy and an unusually coherent PM/agent skill taxonomy, but it still needs a clearer first-run path, a canonical artifact/schema contract, and stricter validation for stale or unavailable skill references.

## Cross-Persona Consensus

All six personas converged on four themes:

1. The core positioning is strong.
   `WHETHER before HOW`, `Determinism First`, `Fail Loud`, and build/no-build discipline are memorable and differentiated.

2. The onboarding path is too heavy for first-time users.
   Users see 5 plugins, 28 skills, harness files, PRD 15 sections, QA Pool, COGS, TK, and multiple gates before they experience one concrete win.

3. Executable capabilities and planned capabilities are mixed.
   Several skill docs reference unavailable or adapter-dependent targets such as `$parallel-team`, `$harness-design`, `$ticket-bridge`, `$ask-team`, `$agent-gtm`, `$instruction`, `$respect`, and `$ui-validate`.

4. The docs need stronger machine-checkable contracts.
   PRD section numbers, evidence files, COGS artifacts, track events, QA artifacts, and routing references should be validated by scripts, not just described in prose.

## Main Strengths

### 1. Clear Product Thesis

The repo has a strong conceptual center:

- `README.md` and `README-ko.md` explain the problem: AI coding agents can build the wrong thing too quickly.
- `AGENTS.md` anchors the work in "WHETHER before HOW".
- The principles fit the product category: deterministic gates, explicit uncertainty, surgical changes, and verification before completion.

Why it matters: this is not "another PRD template". It is a PM build gate for agentic coding.

### 2. Strong PM Lifecycle Coverage

The 5-plugin lifecycle gives users a map:

- `hplan`: should we build?
- `discover`: what problem is real?
- `architect`: how should agents be designed?
- `deliver`: how should we build and ship?
- `operate`: how should we sustain it?

The skill set covers discovery, cost, HITL, orchestration, PRD, QA, sprint execution, incident response, and portfolio review. This is unusually broad for a Codex skill pack.

### 3. Agent-Specific Differentiation

The strongest skills are not generic PM docs; they are agent-product docs:

- `skills/cost-sim/SKILL.md`
- `skills/hitl/SKILL.md`
- `skills/memory-arch/SKILL.md`
- `skills/orchestration/SKILL.md`
- `skills/router/SKILL.md`
- `skills/incident/SKILL.md`
- `skills/qa-checklist/SKILL.md`

These make the package feel purpose-built for AI-agent products, not simply repackaged product management advice.

### 4. Institutional Memory Is a Real Moat

`decision-log`, `exclusions`, and `pm-engine` are especially strong because they turn PM judgment into cumulative memory:

- `skills/decision-log/SKILL.md` tracks decisions and later outcomes.
- `skills/exclusions/SKILL.md` preserves "do not build" memory.
- `skills/pm-engine/SKILL.md` captures and reuses tacit PM knowledge.

This could become the most defensible part of the package if the artifact contracts are tightened.

### 5. Verification Culture Is Present

The repo already has meaningful quality checks:

- `python3 scripts/validate_agents.py`
- `python3 scripts/cogs_sentinel.py --json`
- `python3 -m unittest discover -s tests`
- `bash -n scripts/setup.sh scripts/track-probe.sh`
- setup golden path checks in CI

The current validation does not yet catch all documentation contract problems, but the foundation is there.

## Main Weaknesses And Risks

### P0 Risk: PRD Section Contracts Are Inconsistent

`skills/prd/SKILL.md` defines the current 15-section PRD structure:

- §1: user / ICP / persona
- §7: role + primary goal + anti-goals
- §11: output specification
- §12: success metrics
- §14: failure modes + HITL

But `skills/conductor/SKILL.md` references:

- PRD §7 as success metrics
- PRD §3 as ICP

This is a direct contract risk. If future scripts parse sections based on these references, they can read the wrong content while still reporting success.

Recommended fix:

- Create a single PRD section map in docs or config.
- Update `conductor`, `qa-checklist`, `roadmap`, and `stakeholder-update` to reference that map.
- Add a validator that fails when skill docs mention stale PRD section numbers.

### P0 Risk: Capability Status Is Not Canonical

The repo currently has 28 valid skills, but several docs mention commands that are not present as skills:

- `$parallel-team`
- `$harness-design`
- `$ticket-bridge`
- `$ask-team`
- `$agent-gtm`
- `$instruction`
- `$respect`
- `$ui-validate`
- `$weekly-rollup`

Some are marked `[예정]` or `[adapter-dependent]`; others appear in active flow language.

Recommended fix:

- Add `skills/ROUTING_REGISTRY.md` or `harness/skill-contracts.json`.
- Track each referenced skill as `available`, `planned`, `adapter-dependent`, `script-only`, or `external`.
- Extend `scripts/validate_agents.py` to scan `$skill-name` references and fail on unregistered references.

### P0 Risk: First-Run UX Is Too Heavy

The README quick start currently gives a short `$brainstorm` entry point, but it does not show the expected output, generated files, or next gate.

Recommended fix:

- Add "First 10 Minutes" to `README.md` and `README-ko.md`:
  1. Install skills.
  2. Run project setup.
  3. Run `$brainstorm "idea"`.
  4. Inspect generated harness files.
  5. Run `$evidence-rubric`.
  6. Continue or stop based on the decision.

Include one complete worked example with input, command, expected output, generated files, and decision.

### P0 Risk: Manual Config Copy Can Overwrite User Settings

The manual install path copies:

```bash
cp hplan_codex/config.toml.example ~/.codex/config.toml
```

This can overwrite an existing global Codex config.

Recommended fix:

- Replace with backup/merge instructions.
- Prefer "append only the project trust block and model settings you need" language.
- Add a shell-safe example that preserves the old file.

### P0 Risk: Evidence Gate Schema Is Fragmented

Several docs describe related but different evidence requirements:

- `AGENTS.md`: `pain.md`, `cogs.md`, `market.md`, `competitors.md`
- `skills/evidence-rubric/SKILL.md`: `harness/evidence/report.md`, interview lines >= 2
- `skills/ost/SKILL.md`: strong-push >= 3
- `skills/brainstorm/SKILL.md`: AI-generated `harness/pain.md` seed that still needs real interviews

Recommended fix:

- Define one canonical Signal Gate contract.
- Separate AI-generated hypothesis seeds from real evidence files.
- Add validation for "real quote" fields: source, date, role, quote, workaround, recency.

### P1 Risk: `track-probe` Smoke Does Not Prove Tracking Works

The current README verification pipe can exit 0 without proving `.track/actual_log.jsonl` was written.

Recommended fix:

- In docs and tests, create `.track/`, run the probe, and assert `test -s .track/actual_log.jsonl`.
- Align `track-probe.sh`, `skills/sprint/SKILL.md`, and `skills/stakeholder-update/SKILL.md` around one event vocabulary.

### P1 Risk: `confluence-export` And Notion Publish Are Mixed

`skills/stakeholder-update/SKILL.md` uses `confluence-export`, but also mentions Notion publish under the same mode.

Recommended fix:

- Split modes:
  - `confluence-export`
  - `notion-publish`
  - `wiki-export` if a generic mode is needed

### P1 Risk: Determinism Boundary Claim Is Too Broad

`AGENTS.md` says every skill declares what is LLM and what is deterministic. Several skills have related guidance, but not every skill has a standardized "Determinism Boundary" table.

Recommended fix:

- Either add a standard section to every skill, or change the root claim to "core skills declare..." until the migration is complete.

### P1 Risk: Artifact Map Is Missing

Users need a single view of:

- Which skill reads which file.
- Which skill writes which file.
- Which artifacts are required versus optional.
- Which files are generated from hypotheses versus real evidence.

Recommended fix:

- Add an Artifact Map table covering `harness/`, `.track/`, `docs/`, and root memory files.
- Add "Reads / Writes / Next Skill" metadata near the top of each `SKILL.md`.

### P2 Risk: Version And Model Claims Need Date-Bound Language

Docs mention Codex CLI `0.130.0` and example model slugs such as `gpt-5.5`, `gpt-5.4`, and `gpt-5.3-codex`.

Local check on 2026-06-05:

```bash
npm view @openai/codex version
# 0.137.0
```

External references checked:

- OpenAI Models docs: https://platform.openai.com/docs/models
- OpenAI Codex docs: https://developers.openai.com/codex

Recommended fix:

- Mark version statements as "verified with Codex CLI 0.130.0" instead of implying current latest.
- Move model and pricing references into a date-stamped compatibility table.
- Add a release checklist item: "re-check official model/pricing docs".

## Prioritized Improvement Backlog

### P0

1. Normalize PRD section references across all skills.
2. Add a canonical skill routing/capability registry.
3. Add "First 10 Minutes" quick-start flow with one complete worked example.
4. Replace unsafe `~/.codex/config.toml` overwrite instructions.
5. Define one canonical Signal Gate evidence schema.

### P1

1. Extend `validate_agents.py` to catch stale `$skill` references.
2. Add artifact schemas for PRD, QA Pool, QA Checklist, COGS result, and track events.
3. Improve `track-probe` verification to assert actual log output.
4. Split `confluence-export` and Notion publish paths.
5. Add `Input / Output / Reads / Writes / Next Skill` mini tables to each skill.
6. Add an executable TC runner path for `qa-checklist` output, even if it starts as CLI/API smoke tests.

### P2

1. Add glossary: COGS, TK, HITL, Signal Gate, Build Gate, strong-push, QA Pool, Ralph Loop.
2. Add case studies:
   - "Not built and money/time saved"
   - "Conditional build with mitigations"
3. Add `CONTRIBUTING.md` with skill frontmatter, determinism boundary, examples, and validation rules.
4. Add badges for CI status, release/version, and Codex CLI compatibility.
5. Clean Korean/English terminology style in `README-ko.md` and high-traffic skill docs.

## Persona Summaries

### Persona 1: Senior CPO / Product Strategy

Main praise:

- The thesis is strong and differentiated.
- The product covers the full PM lifecycle.
- `decision-log`, `exclusions`, and `pm-engine` could become a moat.

Main concern:

- ICP is too broad.
- First value is obscured by the breadth of the system.
- The product needs one beachhead user and one golden path.

Top recommendation:

- Position hplan_codex first for "technical PMs and solo founders building AI-agent products with Codex CLI who need a build/no-build gate before PRD and implementation."

### Persona 2: Agent Architect / Multi-agent Systems

Main praise:

- Orchestration, HITL, PRD agent spec, memory architecture, and QA Pool are conceptually strong.
- The repo has the right vocabulary for agentic systems.

Main concern:

- Multi-agent runtime contracts are not standardized.
- PRD section references are inconsistent.
- Some subagent/adapter references are only partially represented in the repo.

Top recommendation:

- Define `CONDUCTOR_AGENT_CONTRACT`: agent roles, input JSON, output JSON, status vocabulary, retry policy, and artifact paths.

### Persona 3: Developer Experience / Installer

Main praise:

- `$skill-installer` and `setup.sh` are correctly separated.
- CI and local checks are reproducible.
- The changelog helps explain the Codex CLI layout migration.

Main concern:

- Manual config copy can overwrite user settings.
- Setup copies templates, but first-run docs refer to concrete files.
- `track-probe` smoke can pass without proving logs were written.

Top recommendation:

- Add a safe installer checklist and make `track-probe` smoke assert actual output.

### Persona 4: QA / E2E Release Risk

Main praise:

- The repo has strong fail-loud language and a good PRD -> QA Pool -> adversarial QA model.
- Basic validation and tests pass.

Main concern:

- QA remains mostly document-contract based.
- `SHIP` conditions are too permissive if §14 or persona specs are missing.
- No executable E2E runner is attached to generated QA cases yet.

Top recommendation:

- Add schema validation and make release readiness require critical/high issue count, failure scenarios, COGS status, and actual test command evidence.

### Persona 5: Korean Technical Docs / Education

Main praise:

- The repeated skill structure teaches users the pattern.
- Good/bad examples are helpful.
- Korean docs explain the philosophy well.

Main concern:

- Concept load is high.
- Executable/planned/adapter-dependent status is not clear enough for learners.
- Determinism boundary is not standardized despite the root claim.

Top recommendation:

- Add glossary, artifact map, and a Korean "10-minute tutorial".

### Persona 6: GTM / Adoption

Main praise:

- The package promise is memorable.
- The lifecycle map can work as an adoption map.
- `customer-reach`, `evidence-rubric`, and `prd` form a persuasive PM workflow.

Main concern:

- README is more installation doc than conversion funnel.
- Buyer/user messaging is too broad.
- No examples, case studies, or contribution path yet.

Top recommendation:

- Add README conversion sections: who this is for, first success path, worked examples, and case studies.

## Corrections To Agent Findings

One agent claimed there were no `agents/openai.yaml` files. Central verification found one:

- `skills/stakeholder-update/agents/openai.yaml`

The corrected issue is not "no subagent definitions exist"; it is "subagent contracts are not standardized across conductor, QA, and skill routing docs."

Some agents reported 31 Markdown files, while central `rg --files -g '*.md' | wc -l` returned 32. The central count is used in this report.

## Verification Performed

Commands run locally:

```bash
rg --files -g '*.md' | wc -l
python3 scripts/validate_agents.py
python3 -m unittest discover -s tests
npm view @openai/codex version
```

Results:

- Markdown files: 32
- Skill validation: 28 skills valid
- Unit tests: 17 tests OK
- Current npm `@openai/codex` version observed: 0.137.0
