# hplan_codex Case Studies

These case studies are illustrative examples for learning the hplan_codex gate
logic. They are not customer claims, production metrics, or evidence that a
specific company used hplan_codex.

## How To Read These Examples

- Treat each case as a worked scenario, not a testimonial.
- The numbers are intentionally simple so the decision path is easy to inspect.
- The important part is the gate logic: evidence quality, COGS, mitigations, and
  decision logging.

---

## Case Study 1: Not Built, Time And Money Saved

### Scenario

A team wants to build an AI meeting-summary agent for startup founders. The first
idea is broad: "Summarize every meeting and suggest next actions."

### Initial Evidence

| Signal | Example input |
|---|---|
| ICP | "Busy founders" |
| Pain | Founders say meeting notes are annoying |
| Current workaround | Mixed: some use built-in recorder summaries, some delegate notes |
| Competitors | Native meeting tools, Notion AI, manual assistant, doing nothing |
| COGS | Expected to be high because every user uploads long audio and expects fast turnaround |

### Gate Findings

- ICP was too broad. "Busy founders" did not identify a repeated buyer behavior.
- Interview notes showed interest, but not strong-push. Users disliked the task,
  yet most already had acceptable summaries.
- The current workaround was cheap and embedded in tools they already used.
- COGS risk was material because long audio plus follow-up generation created
  recurring token and transcription cost.
- Differentiation was weak against native meeting tools.

### Decision

`hold`

The team should not build the general meeting-summary product. It should record
the decision and return only if a sharper wedge appears.

### Saved Cost

Illustrative avoided spend:

| Work avoided | Example estimate |
|---|---|
| 2-week prototype | 80 engineering hours |
| Design/research polishing | 20 product/design hours |
| Model/transcription testing | $300-$800 in exploratory usage |
| Opportunity cost | One sprint redirected to a stronger candidate |

### Decision Log Entry

```bash
python3 scripts/decision_log.py log \
  --project meeting-summary-agent \
  --gate product \
  --decision hold \
  --score 42 \
  --reason "ICP too broad" \
  --reason "No strong-push: users have acceptable native summaries" \
  --reason "COGS risk high for long audio workload"
```

### What hplan_codex Teaches

The win is not that the team wrote no code. The win is that it avoided building a
fast, polished, low-differentiation product before evidence justified the spend.

---

## Case Study 2: Conditional Build With Mitigations

### Scenario

A support team wants an AI refund-triage assistant. The agent reads support
tickets, classifies refund eligibility, drafts a reply, and routes uncertain
cases to a human.

### Initial Evidence

| Signal | Example input |
|---|---|
| ICP | B2C subscription support teams with 500+ monthly refund tickets |
| Pain | Support leads report queue spikes after billing cycles |
| Current workaround | Spreadsheet macros plus manual policy lookup |
| strong-push | 4 support leads describe recent billing-week incidents and overtime |
| Competitors | Helpdesk macros, internal scripts, outsourced support |
| COGS | Positive at normal volume, risky at billing-cycle spikes |

### Gate Findings

- The ICP was behaviorally specific.
- strong-push evidence was credible: recent painful events plus current
  workarounds.
- The workflow had clear deterministic boundaries:
  - policy lookup and eligibility thresholds should be deterministic;
  - reply drafting may use an LLM;
  - low-confidence or high-value refunds need HITL approval.
- COGS was acceptable in steady state but uncertain during spikes.
- Risk was manageable if the first version stayed narrow.

### Decision

`CONDITIONAL_GO`

Build a narrow version only if the team accepts explicit mitigations.

### Mitigations

| Risk | Mitigation |
|---|---|
| Wrong refund decision | LLM drafts only; deterministic policy lookup decides eligibility class. |
| High-value refund exposure | HITL approval for refunds above a fixed amount. |
| Billing-cycle COGS spike | Cap daily processed tickets in beta and monitor p90 cost. |
| Low-confidence classification | Route to human when confidence is below threshold. |
| QA blind spots | Generate QA Pool from PRD Section 15 and run adversarial QA before launch. |

### Build Scope

Allowed:
- classify ticket category;
- retrieve policy text;
- draft reply;
- route uncertain/high-value cases;
- log decisions and reviewer overrides.

Not allowed in v1:
- autonomous refund execution;
- policy edits by the agent;
- broad support automation outside refunds;
- silent handling of low-confidence cases.

### Verification Plan

```bash
python3 scripts/validate_agents.py
python3 scripts/cogs_sentinel.py --json
python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/track-probe.sh
```

Project-specific verification should also include:

- fixture tickets for eligible, ineligible, ambiguous, and high-value refunds;
- QA cases from `harness/QA_POOL.json`;
- a COGS comparison after billing-cycle beta usage;
- decision-log backfill after 30 days.

### Decision Log Entry

```bash
python3 scripts/decision_log.py log \
  --project refund-triage-assistant \
  --gate build \
  --decision CONDITIONAL_GO \
  --score 78 \
  --reason "4 strong-push interviews" \
  --reason "COGS acceptable outside billing spikes" \
  --reason "Mitigations: HITL high-value refunds, deterministic policy lookup, beta volume cap"
```

### What hplan_codex Teaches

`CONDITIONAL_GO` is not a soft pass. It is a build permission with constraints.
The mitigations are part of the decision, and the follow-up audit determines
whether the gate was calibrated correctly.
