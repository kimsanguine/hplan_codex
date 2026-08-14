# hplan_codex

> **WHETHER before HOW** — The most expensive code is code that shouldn't have been written.

> 🇰🇷 한국어 가이드: [README-ko.md](README-ko.md)

PM Build Gate for Codex CLI. Structured decision-making framework for AI-assisted product development.

[![local%20folders](https://img.shields.io/badge/local%20folders-28-blue)](skills/)
[![plugins](https://img.shields.io/badge/plugins-5-green)](skills/)
[![Codex CLI baseline](https://img.shields.io/badge/Codex%20CLI%20baseline-0.130.0-black)](https://developers.openai.com/codex)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## The Problem

AI coding agents are fast. Too fast.
They'll build whatever you ask — wrong product, right velocity.

hplan_codex adds a **WHETHER gate** before the HOW:
- Is this the right problem to solve?
- Do we have real evidence of pain?
- Can we afford to run this at scale?

## Core Contract and Local Folders

The hplan-core contract defines **34 canonical capabilities** for Codex: **25 native** and **9 adapter-required**. `adapter-required` capabilities are not active; use their documented draft or local fallback until a separately authorized adapter exists.

This repository also contains **28 local skill folders**. That is an installation-layout count, not a 28-feature claim: it includes the three compatibility alias folders `roadmap`, `router`, and `stakeholder-update`.

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

## Prerequisite: Install Codex CLI

hplan_codex runs inside the OpenAI Codex CLI. **Install it first:**

```bash
npm install -g @openai/codex
```

Official docs and other install options: https://developers.openai.com/codex

---

## Install hplan_codex

**Recommended — install skills from inside a Codex session:**

```
$skill-installer https://github.com/kimsanguine/hplan_codex
```

This installs the 28 local folders into your Codex CLI skills directory, including three compatibility aliases. It does **not** copy project harness files or helper scripts into the repo you are working on.

**Project setup — latest-main bootstrap, not tag-pinned/reproducible:**

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh)
```

`scripts/setup.sh` copies `harness/` templates, `AGENTS.md`, `config.toml.example`,
and helper scripts such as `scripts/track-probe.sh`. It does **not** install
Codex skills; use `$skill-installer` for that.

For local pre-release verification before changes are pushed to `main`:

```bash
HPLAN_CODEX_SOURCE_DIR=/path/to/hplan_codex bash scripts/setup.sh --dir=/path/to/test-project
```

**Manual alternative — verified local-source setup** (clone + skills + complete project bootstrap):

```bash
git clone https://github.com/kimsanguine/hplan_codex.git
# Copy skills into the Codex CLI scope verified by doctor.
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R hplan_codex/skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
# This also installs harness, doctor, snapshot, and repair backup into this project.
HPLAN_CODEX_SOURCE_DIR="$(pwd)/hplan_codex" bash hplan_codex/scripts/setup.sh --dir=.
# Optional: keep a config example for manual merge; do not overwrite your live config.
mkdir -p "${CODEX_HOME:-$HOME/.codex}"
cp -n hplan_codex/config.toml.example "${CODEX_HOME:-$HOME/.codex}/config.toml.example"
```

---

## First 10 Minute Success Path

The first success needs two separate installs: `$skill-installer` places skills in
`$CODEX_HOME/skills`, while `scripts/setup.sh` copies only project-local harness,
doctor, and core snapshot files. Confirm this order from your project folder:

1. In a Codex session, run `$skill-installer https://github.com/kimsanguine/hplan_codex`; use a new turn after it completes.
2. In the project directory, run the latest-main bootstrap below. It works after `$skill-installer`, but is not tag-pinned or reproducible:

   ```bash
   bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan_codex/main/scripts/setup.sh) --dir=.
   ```
3. Run the read-only installation check: `python3 scripts/hplan_doctor.py`. It checks the three first-success skills in the active `$CODEX_HOME` as well as the project snapshot.
4. Open the project in Codex CLI and run `$brainstorm "your idea here"`.
5. Capture the first WHETHER judgment: `GO`, `INVESTIGATE`, or `HOLD`.
6. If the idea is still alive, create or update `harness/pain.md` with real evidence, not AI-generated seed text.
7. Run `$evidence-rubric` and keep the score plus missing-evidence notes.

Expected first success: a documented build/no-build judgment within 10 minutes, plus the next evidence action.

### Start with these three skills

1. `$brainstorm` — starts with the WHETHER gate, so the first output is a specific build/no-build direction rather than a feature list.
2. `$socratic-question` — turns that direction into explicit assumptions and exposes the highest-risk unknown before implementation.
3. `$evidence-rubric` — scores the evidence and names what is still missing; AI-generated seeds never count as real proof for a `GO` decision.

### Read-only `hplan doctor` equivalent

Run `python3 scripts/hplan_doctor.py` from a project created by `scripts/setup.sh`.
It makes no writes and checks Python, the available Codex CLI version, the three
first-success skills in `$CODEX_HOME/skills`, plus the four total
`hplan-core` snapshot artifacts: `hplan-core.lock` and three files in `docs/`.
The result is intentionally actionable:

- `정상` — start `$brainstorm "your idea"`.
- `자동 복구 가능` — if first-success skills are missing, run `$skill-installer https://github.com/kimsanguine/hplan_codex` in Codex. If the snapshot alone is missing, run `python3 scripts/repair_hplan_core_snapshot.py --root .`. Then run doctor again. This explicit local repair restores only the four total snapshot artifacts (`hplan-core.lock` plus three `docs/` files); doctor itself never writes.
- `강사 호출` — preserve the mismatch output and ask the package maintainer for a matching core snapshot; doctor will not overwrite it.

The project snapshot has four total artifacts: `hplan-core.lock` plus
`docs/hplan-capability-matrix.json`, `docs/HPLAN_CAPABILITY_MATRIX.md`, and
`docs/hplan-core-adapter.json`. The repair source is the project-local
`.hplan-core-snapshot/` backup; the checked-in `hplan-core-fixture/` directory is
CI-only parity data and is never a repair source.

**Full workflow:**

```
$brainstorm → $socratic-question → $opp-tree → $prd → $conductor
```

Reference docs:
- [Glossary](docs/GLOSSARY.md)
- [Illustrative case studies](docs/CASE_STUDIES.md)
- [Contributing](CONTRIBUTING.md)

---

## Security & Sandbox

hplan_codex runs inside Codex CLI's sandbox. The following sandbox behavior was verified against the **Codex CLI 0.130.0 baseline**; check the current Codex documentation before relying on it for a newer CLI:

| Mode | Access |
|---|---|
| `read-only` | Read project files only — no writes, no network |
| `workspace-write` | Read + write project files + run commands in the workspace (default) |
| `danger-full-access` | Full read/write + network — use only when you trust the task |

Set the sandbox mode in your Codex CLI session or config. hplan_codex skills assume `workspace-write` for the build phases.

> At the verified Codex CLI 0.130.0 baseline, file-based hooks were unavailable. `scripts/track-probe.sh` is provided as a manual sprint-tracking probe you can run yourself with `bash scripts/track-probe.sh` or wire into a Codex automation.

## Status & Verification

Currently executable:
- Skill installation via `$skill-installer`
- Harness/script bootstrap via `bash scripts/setup.sh`
- Manual probe invocation via `bash scripts/track-probe.sh`
- Read-only installation and core snapshot check via `python3 scripts/hplan_doctor.py`
- Explicit local snapshot recovery via `python3 scripts/repair_hplan_core_snapshot.py --root .`
- Static skill/doc validation via `python3 scripts/validate_agents.py`

Planned or adapter-dependent capabilities are tracked in
[skills/ROUTING_REGISTRY.md](skills/ROUTING_REGISTRY.md).

Canonical references:
- PRD numbering contract: [docs/PRD_SECTION_MAP.md](docs/PRD_SECTION_MAP.md)
- Signal Gate evidence schema: [docs/SIGNAL_GATE_SCHEMA.md](docs/SIGNAL_GATE_SCHEMA.md)
- Skill status registry: [skills/ROUTING_REGISTRY.md](skills/ROUTING_REGISTRY.md)

Verification commands:

```bash
python3 scripts/validate_agents.py
python3 scripts/hplan_doctor.py
python3 scripts/cogs_sentinel.py --json
# CI uses the checked-in `hplan-core-fixture`, pinned to a private core commit.
# It is a parity fixture, not a public core distribution. Set HPLAN_CORE_DIR only
# to compare an approved local core checkout during maintenance.
python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
bash scripts/setup.sh --help
HPLAN_CODEX_SOURCE_DIR="$PWD" bash scripts/setup.sh --dir="$(mktemp -d)"
mkdir -p .track
printf '%s\n' track-smoke > .track/current_task
printf '%s\n' '{"tool_name":"write_file","tool_input":{"file_path":"noop","content":"a\nb\n"}}' | bash scripts/track-probe.sh
test -s .track/actual_log.jsonl
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
