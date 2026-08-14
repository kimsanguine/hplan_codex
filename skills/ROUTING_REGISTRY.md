# Skill Routing Registry

Canonical registry for skill references in README, `AGENTS.md`, and `skills/*/SKILL.md`.

Status meanings:

- `available`: Skill exists in this repo under `skills/<name>/SKILL.md`.
- `planned`: Skill is named as a future hplan_codex capability, but no local skill folder exists yet.
- `adapter-dependent`: Capability depends on an external adapter, plugin, MCP server, or ecosystem-specific bridge.
- `script-only`: Local script or manual command, not a Codex skill.
- `external`: Capability is provided outside this repo, such as another Codex skill or external service.

## Local Skill Folders

There are 28 local folders. Twenty-five are direct local skill folders listed below; the remaining three are compatibility aliases, not additional canonical capabilities.

| Plugin | Skills |
|---|---|
| hplan | `$brainstorm`, `$evidence-rubric`, `$decision-log`, `$exclusions`, `$ost` |
| discover | `$socratic-question`, `$opp-tree`, `$assumptions`, `$cost-sim`, `$customer-reach`, `$hitl` |
| architect | `$orchestration`, `$memory-arch`, `$design-token`, `$strategy` |
| deliver | `$prd`, `$conductor`, `$sprint`, `$qa-checklist`, `$build-loop` |
| operate | `$pm-engine`, `$metrics-design`, `$ops-review`, `$incident`, `$portfolio` |

## Compatibility Alias Folders

These three local folders preserve established invocation routes. They are aliases, not distinct core capabilities.

| Alias | Compatibility route | Boundary |
|---|---|---|
| `$roadmap` | `$roadmap` → `$prd --mode roadmap` | Preserve the mode. |
| `$router` | `$router` → `$orchestration --pattern router` | Preserve the pattern. |
| `$stakeholder-update` | `$stakeholder-update` → `$ops-review` | Draft-only unless a separately authorized adapter exists. |

## Planned Skill References

Use `[planned]` whenever these appear in skill instructions.

| Reference | Intended use | Current fallback |
|---|---|---|
| `$agent-gtm` | ICP, beachhead, JTBD, Switch Interview synthesis | Write §1 and §2 directly using the PRD template |
| `$build-or-buy` | 6-axis build/buy decision matrix | Use §4 decision option matrix manually |
| `$instruction` | Detailed 7-part agent instruction design | Fill §7-10 directly |
| `$reliability` | Reliability, SLO, and failure-mode design | Fill §14 directly |
| `$handoff` | Multi-ecosystem export to Spec-Kit / Kiro / GStack / Codex CLI | Manual handoff document |
| `$harness-design` | Harness artifact structure/design generation | Use `harness/` templates and `AGENTS.md` manually |
| `$parallel-team` | Role-parallel implementation team | Use `$conductor --mode sprint` where task dependencies allow |
| `$weekly-rollup` | Weekly operating summary | Use `$ops-review` or manual report |

## Adapter-Dependent References

Use `[adapter-dependent]` whenever these appear in skill instructions.

| Reference | Dependency | Current fallback |
|---|---|---|
| `$respect --mode brief` | Design signature adapter / RESPECT.md workflow | Add a concise design signature note manually or mark N/A |
| `$ui-validate` | UI validation adapter/browser evidence workflow | Manual browser/e2e evidence capture |
| Tracking automation registration | Codex automation or hook support | Run `bash scripts/track-probe.sh` manually or via external automation |

## Script-Only References

These are backed by executable local scripts or manual commands, not skill directories.

| Reference | Status | Notes |
|---|---|---|
| `$interview-synthesis` | script-only | Backed by `scripts/interview_synthesis.py` |
| `bash scripts/setup.sh` | script-only | Copies harness/templates/scripts into a project |
| `bash scripts/track-probe.sh` | script-only | Manual sprint-tracking probe |
| `python3 scripts/validate_agents.py` | script-only | Static skill/doc validation |

## External References

These are provided outside this repo.

| Reference | Dependency | Current fallback |
|---|---|---|
| `$skill-installer` | Codex skill installer | Manual clone + copy install path |
| `$ticket-bridge` | External issue tracker adapter | Manual issue tracker update |
| `$ask-team` | Team communication channel or adapter | Manual stakeholder request |

## Documentation Placeholders

These are examples or shell variables, not skill references: `$skill-name`, `$HOME`, `$PWD`, `$A`, `$B`, `$C`, `$N`, `$X`, `$Y`, `$Z`, `$NEXT_NUM`, `$TOTAL`, `$TOOL_CALLS`, `$TASK_START`, `$TASK_DONE`, `$HAS_TRACKING_DATA`, `$EXIT_ERRORS`.
