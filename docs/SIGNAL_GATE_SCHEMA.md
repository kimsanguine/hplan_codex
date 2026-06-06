# Signal Gate Evidence Schema

Canonical evidence contract for hplan_codex. Use this file when documenting Signal Gate requirements in `AGENTS.md`, README files, or future validators.

## Evidence Status

Every evidence item must declare one of these statuses:

| Status | Meaning | Can pass Signal Gate? |
|---|---|---|
| `real_evidence` | Collected from a real source such as interview, customer email, analytics, pricing page, competitor page, or market report. Includes source and date. | Yes |
| `ai_generated_seed` | AI-generated draft, assumption, synthetic quote, or placeholder created to start discovery. | No |
| `missing` | Required evidence is not present. | No |

AI-generated seeds are useful for planning interviews and search terms, but they are not evidence. They must be replaced or marked as rejected before a `GO` decision.

## Required Files

Before proceeding to build, these files must exist under `harness/`.

| File | Minimum real-evidence requirement |
|---|---|
| `pain.md` | 3+ real interview quotes with source, date, role, and pain statement |
| `cogs.md` | Unit economics estimate with assumptions, model/API price source, and date |
| `market.md` | Market sizing evidence with source, date, and sizing method |
| `competitors.md` | Top 3 alternatives with source URL/date and observed tradeoff |

## Entry Format

Use this compact block for each evidence item.

```markdown
### EVIDENCE-[NN] — [short title]
- status: real_evidence | ai_generated_seed | missing
- source_type: interview | analytics | customer_email | market_report | competitor_page | pricing_page | internal_metric | other
- source: [person/company/report/url/file]
- source_date: YYYY-MM-DD
- collected_date: YYYY-MM-DD
- role_or_segment: [buyer/user/persona/market segment]
- claim: [what this evidence supports]
- artifact: [quote/snippet/metric/table/link]
- confidence: low | medium | high
- next_action: [replace seed, verify source, run interview, accept]
```

## Gate Logic

`$evidence-rubric` should score only `real_evidence` items. Items marked `ai_generated_seed` can appear in discovery notes, but they must contribute 0 evidence points.

Recommended gate interpretation:

- `GO` / `build`: score >= 75, `economic_pain` present, 2+ real interview lines, and all required files contain real evidence.
- `INVESTIGATE` / `interview`: score >= 55, or score >= 75 without all mandatory `GO` conditions.
- `PIVOT`: score 35-54.
- `HOLD`: score < 35, or a required file is missing and no credible next evidence action exists.
- Any core pain quote marked only as `ai_generated_seed`: cannot be `GO`
