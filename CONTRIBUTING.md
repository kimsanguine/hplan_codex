# Contributing to hplan_codex

Thanks for improving hplan_codex. This repo is a Codex CLI PM Build Gate skill
pack, so changes should preserve two things: build/no-build discipline and
deterministic gate behavior.

## Contribution Principles

- Keep changes surgical. Do not rewrite unrelated docs, contracts, tests, or
  scripts while touching a skill.
- Fail loud. If a capability is not executable in this repo, mark it as
  `planned`, `adapter-dependent`, `script-only`, or `external`.
- Separate LLM work from deterministic work. LLMs may draft, summarize, and
  classify; scripts and explicit rules should handle thresholds, routing,
  status codes, retries, arithmetic, and file-contract checks.
- Preserve append-only artifacts such as decision logs and exclusion records.
- When changing docs, keep Korean and English terminology aligned where both
  root READMEs are affected.

## Skill Frontmatter Rules

Each skill must live at:

```text
skills/<skill-name>/SKILL.md
```

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: <skill-name>
description: "One clear sentence describing when Codex should use this skill."
metadata:
  short-description: "Short label for humans."
  plugin: hplan
---
```

Rules:

- `name` must exactly match the containing directory name.
- `description` is required and should describe trigger context, not only the
  artifact the skill writes.
- `metadata.short-description` and `metadata.plugin` are recommended for
  consistency, even though the current validator only requires `name` and
  `description`.
- Do not reference missing scripts as executable commands.
- Do not present planned or adapter-dependent capabilities as available skills.

## Determinism Boundary Expectations

Every skill should make the boundary visible. A concise table is preferred:

| Task | Method | Reason |
|---|---|---|
| Natural-language summary | LLM | Prose generation is allowed. |
| Score calculation | Deterministic | Numeric gates must not depend on LLM judgment. |
| Route selection | Deterministic | Skill routing and pass/fail gates need explicit rules. |

Use deterministic logic for:

- scoring and threshold checks;
- status or gate color calculation;
- retry and fallback policy;
- file existence checks;
- artifact parsing where the schema is known;
- script output validation.

Use LLMs for:

- interview synthesis;
- PRD drafting;
- stakeholder prose;
- failure-mode brainstorming;
- classification when the criteria are shown and uncertainty is reported.

## Tests And Validation Commands

Run the smallest relevant check first, then broader checks when the change can
affect contracts.

Recommended repo-level checks:

```bash
python3 scripts/validate_agents.py
python3 scripts/cogs_sentinel.py --json
python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
mkdir -p .track
printf '%s\n' track-smoke > .track/current_task
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
test -s .track/actual_log.jsonl
```

For docs-only changes, at minimum run:

```bash
python3 scripts/validate_agents.py
```

If your docs mention setup, COGS, tracking, or tests, run the matching command
above before reporting the change as verified.

## Changelog Expectations

Update `CHANGELOG.md` when the change affects:

- install or setup behavior;
- skill invocation or routing;
- harness file contracts;
- public command availability;
- validation behavior;
- user-facing compatibility claims.

Docs-only additions may skip the changelog when they do not change behavior, but
the final report should still list the files changed and the validation run.

## How To Add A Skill Safely

1. Create `skills/<skill-name>/SKILL.md`.
2. Add valid frontmatter where `name` exactly matches `<skill-name>`.
3. State trigger gates, route-to-other-skill rules, boundary checks, inputs,
   outputs, and verification expectations.
4. Add a Determinism Boundary table.
5. If the skill needs scripts, add tests and make script references real before
   documenting them as executable.
6. If the skill writes harness artifacts, define the file path and schema in the
   skill body.
7. Mark external integrations as `adapter-dependent` until the adapter exists in
   the default install path.
8. Run validation and tests.
9. Update README links or status only if the skill is actually available.
10. Update `CHANGELOG.md` if the public surface changed.

## Multi-Worker Safety

This repo is often edited by parallel workers. Before editing:

- check `git status --short`;
- avoid reverting changes you did not make;
- prefer new docs or narrow diffs over broad rewrites;
- do not edit scripts/tests if another worker owns validation;
- do not change PRD or conductor contracts unless that is your assigned scope.
