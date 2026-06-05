#!/usr/bin/env python3
"""Generate docs/OPPORTUNITY_TREE.md from a JSON OST input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_OUT = Path("docs") / "OPPORTUNITY_TREE.md"


def mermaid_label(value: object) -> str:
    text = str(value).replace("\n", " ").replace('"', "'")
    return text


def load_input(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON input: {exc}") from exc


def active_and_parked(opportunities: list[dict]) -> tuple[list[dict], list[dict]]:
    active = []
    parked = []
    for opp in opportunities:
        if int(opp.get("evidence_count", 0)) >= 3:
            active.append(opp)
        else:
            parked.append(opp)
    return active, parked


def render_mermaid(outcome: str, active: list[dict], parked: list[dict]) -> str:
    lines = [
        "```mermaid",
        "graph TD",
        f'  outcome["Outcome: {mermaid_label(outcome)}"]',
    ]
    if active:
        for opp_index, opp in enumerate(active, 1):
            opp_id = f"opp{opp_index}"
            lines.append(
                f'  {opp_id}["Opportunity: {mermaid_label(opp.get("name", ""))}<br/>Evidence: {int(opp.get("evidence_count", 0))}"]'
            )
            lines.append(f"  outcome --> {opp_id}")
            for sol_index, solution in enumerate(opp.get("solutions", []), 1):
                sol_id = f"{opp_id}_sol{sol_index}"
                exp_id = f"{sol_id}_exp"
                rule_id = f"{sol_id}_rule"
                lines.append(f'  {sol_id}["Solution: {mermaid_label(solution.get("name", ""))}"]')
                lines.append(f'  {exp_id}["Experiment: {mermaid_label(solution.get("experiment", "MISSING"))}"]')
                lines.append(
                    f'  {rule_id}["Decision rule: {mermaid_label(solution.get("decision_rule", "MISSING"))}"]'
                )
                lines.append(f"  {opp_id} --> {sol_id}")
                lines.append(f"  {sol_id} --> {exp_id}")
                lines.append(f"  {exp_id} --> {rule_id}")
    if parked:
        lines.append('  parking["Parking Lot: evidence_count < 3"]')
        lines.append("  outcome -.-> parking")
        for park_index, opp in enumerate(parked, 1):
            park_id = f"park{park_index}"
            lines.append(
                f'  {park_id}["{mermaid_label(opp.get("name", ""))}<br/>Evidence: {int(opp.get("evidence_count", 0))}"]'
            )
            lines.append(f"  parking -.-> {park_id}")
    lines.append("```")
    return "\n".join(lines)


def render_solution_rows(active: list[dict]) -> list[str]:
    rows = [
        "| Opportunity | Evidence | Solution | Experiment | Decision Rule |",
        "|---|---:|---|---|---|",
    ]
    for opp in active:
        solutions = opp.get("solutions", [])
        if not solutions:
            rows.append(
                f'| {opp.get("name", "")} | {int(opp.get("evidence_count", 0))} | MISSING | MISSING | MISSING |'
            )
            continue
        for solution in solutions:
            rows.append(
                "| {opp} | {evidence} | {solution} | {experiment} | {rule} |".format(
                    opp=opp.get("name", ""),
                    evidence=int(opp.get("evidence_count", 0)),
                    solution=solution.get("name", ""),
                    experiment=solution.get("experiment", "MISSING"),
                    rule=solution.get("decision_rule", "MISSING"),
                )
            )
    return rows


def render_parking_rows(parked: list[dict]) -> list[str]:
    if not parked:
        return ["No opportunities parked."]
    rows = ["| Opportunity | Evidence | Reason |", "|---|---:|---|"]
    for opp in parked:
        rows.append(
            f'| {opp.get("name", "")} | {int(opp.get("evidence_count", 0))} | evidence_count < 3 |'
        )
    return rows


def render_markdown(data: dict) -> str:
    outcome = data.get("outcome")
    opportunities = data.get("opportunities", [])
    if not outcome:
        raise SystemExit("OST input requires outcome")
    if not isinstance(opportunities, list):
        raise SystemExit("OST input requires opportunities as a list")

    active, parked = active_and_parked(opportunities)
    lines = [
        "# Opportunity Solution Tree",
        "",
        f"**Outcome:** {outcome}",
        "",
        render_mermaid(outcome, active, parked),
        "",
        "## Solutions",
        "",
        *render_solution_rows(active),
        "",
        "## Parking Lot",
        "",
        *render_parking_rows(parked),
        "",
        "## Rules",
        "",
        "- Opportunities with `evidence_count < 3` stay in the parking lot.",
        "- Each active solution should have one experiment and one decision rule.",
        "- Opportunities describe unmet user needs; solutions describe interventions.",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    markdown = render_markdown(load_input(args.input))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(markdown, encoding="utf-8")
    print(str(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
