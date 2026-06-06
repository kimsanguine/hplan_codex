# hplan_codex Glossary

This glossary defines terms used across hplan_codex skills, harness templates,
and gate reports. It is a product/agent operating vocabulary, not a general PM
dictionary.

## Core Gate Terms

| Term | Meaning | Where it appears |
|---|---|---|
| WHETHER before HOW | The hplan principle that a team should decide whether a product, feature, or agent is worth building before asking how to implement it. | README, AGENTS.md, brainstorm, evidence-rubric |
| Signal Gate | The early evidence gate before PRD/build work. It checks whether pain, COGS, market, and competitor evidence are strong enough to justify deeper work. | AGENTS.md, harness templates, brainstorm |
| Product Gate | The decision point that turns discovery evidence into a product judgment: build, interview, pivot, or hold. | evidence-rubric, ost, decision-log |
| Build Gate | The pre-build/pre-ship gate that checks economics, implementation risk, QA readiness, and mitigations before coding or release. | cogs_sentinel.py, conductor, stakeholder-update |
| Evidence Rubric | The 100-point scoring framework that evaluates ICP specificity, painful event recency, workaround, repetition, economic pain, MVP narrowness, and acquisition path. | skills/evidence-rubric/SKILL.md |
| CONDITIONAL_GO | A decision that allows limited build or release only when explicit mitigations are attached. It is not the same as an unconditional pass. | decision-log, cogs_sentinel.py, stakeholder-update |
| HOLD | A decision to stop or pause because evidence, economics, or differentiation is too weak. HOLD decisions should be recorded so the team learns from false holds later. | decision-log, exclusions |

## Evidence And Economics

| Term | Meaning | Deterministic expectation |
|---|---|---|
| COGS | Cost of Goods Sold. In hplan_codex, this usually means the per-user or per-execution cost of model calls, tools, storage, and human review required to run an agent product. | COGS decisions should come from `scripts/cogs_sentinel.py` or explicit numeric inputs, not LLM intuition. |
| COGS Sentinel | The executable economic gate that models p50, p90, and worst-case cost and returns `GREEN`, `CONDITIONAL_GO`, or `RED`. | Run `python3 scripts/cogs_sentinel.py --json` for repo-level smoke validation. |
| strong-push | A user evidence signal where a person describes a recent painful event and a current workaround. It is stronger than a generic opinion or interest statement. | Count real people with strong-push evidence; do not let the LLM invent counts. |
| Interview quote | A direct or summarized user statement with source, date, role, and context. | Signal Gate expects real interview evidence, not only AI-generated hypotheses. |
| Current workaround | What the user does today to survive the problem. Workarounds indicate that the pain already changes behavior. | Treat "no workaround" as weak evidence unless the problem is newly emerging. |
| Market evidence | Evidence about reachable market size, buyer budget, or adoption path. | Separate confirmed data from inference. |
| Competitor alternative | A current substitute, including manual work, spreadsheets, agencies, internal tools, or doing nothing. | Signal Gate requires top alternatives, not only direct software competitors. |

## Agent And Skill Terms

| Term | Meaning | Where it appears |
|---|---|---|
| TK | Tacit Knowledge. A structured record of hard-won PM or operator judgment, usually stored as `TK-NNN` with activation conditions and links to related TK. | pm-engine, sprint, incident, strategy |
| HITL | Human-in-the-Loop. A designed point where a human reviews, approves, audits, or escalates an agent action. | hitl, prd, qa-checklist |
| QA Pool | The PRD Section 15 artifact that defines persona and developer-reviewer roles for adversarial QA. It powers `qa-checklist --mode adversarial`. | prd, qa-checklist, harness/PRD.md.template |
| Ralph Loop | The autonomous build/review/fix loop used in delivery contexts. In hplan_codex docs, it should be treated as a high-risk build mode that needs explicit approval and QA boundaries. | build-loop, qa-checklist |
| adapter-dependent | A capability that depends on an external integration, connector, MCP server, or runtime adapter that may not be present in a default install. | README, AGENTS.md, prd, qa-checklist |
| script-only | A capability that exists as a repository script rather than a callable Codex skill. | setup.sh, track-probe.sh, cogs_sentinel.py |
| planned | A capability described as future work. Planned commands must not be presented as currently executable. | README status sections |
| harness | The project-local working directory where PRDs, evidence files, QA artifacts, decision logs, and build-gate outputs are stored. | README, AGENTS.md, skills |

## Determinism Boundary Terms

| Term | Meaning | Rule of thumb |
|---|---|---|
| deterministic boundary | The line between work that may use an LLM and work that must be handled by code, parsing, lookup tables, or explicit user input. | Use LLMs for classification and prose; use deterministic logic for routing, thresholds, retries, status codes, and arithmetic. |
| LLM-as-prose | Acceptable LLM work: drafting PRDs, summarizing interviews, creating user-facing copy, or turning notes into structured language. | The LLM can write, but should cite inputs and expose uncertainty. |
| LLM-as-if-statement | Disallowed LLM work: choosing branches, calculating scores, deciding retry policy, or silently passing/failing gates. | Replace with scripts, rules, thresholds, or explicit human approval. |
| Fail Loud | The expectation that missing files, skipped checks, uncertain evidence, or unavailable adapters are reported plainly. | Never report `done`, `pass`, `working`, or `deployed` without verification evidence. |
| Surgical Changes | A change discipline: touch only the requested surface, avoid adjacent refactors, and do not rewrite unrelated docs. | Especially important in multi-worker repo edits. |

## Decision Vocabulary

| Decision | Meaning |
|---|---|
| build | Evidence and economics are strong enough to proceed. |
| interview | The idea may be promising, but more user evidence is needed before PRD/build work. |
| pivot | The problem appears real, but the target, wedge, or solution path is wrong. |
| hold | Stop or pause because both evidence and economics are weak, or because an exclusion applies. |
| CONDITIONAL_GO | Proceed only with named mitigations, limits, or follow-up checks. |

## Common Confusions

| Confusion | Clarification |
|---|---|
| Signal Gate vs Build Gate | Signal Gate asks whether the problem is real enough. Build Gate asks whether the implementation can be built or shipped safely and economically. |
| QA Pool vs QA_CHECKLIST.md | QA Pool defines reviewer/persona roles. `QA_CHECKLIST.md` lists concrete test cases. |
| HITL vs QA | HITL is runtime or workflow human review. QA is pre-release verification. They may overlap, but they are not the same control. |
| TK vs documentation | TK is contextual judgment with activation conditions. Documentation is broader reference material. |
| adapter-dependent vs planned | Adapter-dependent may work when the integration exists. Planned is not currently available. |
