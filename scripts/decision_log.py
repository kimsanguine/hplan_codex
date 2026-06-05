#!/usr/bin/env python3
"""Append and audit hplan gate decisions as JSONL."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path("harness") / "decisions.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def folded_decisions(rows: list[dict]) -> dict[str, dict]:
    decisions: dict[str, dict] = {}
    for row in rows:
        event = row.get("event", "decision")
        if event == "decision":
            decisions[row["id"]] = dict(row)
        elif event == "outcome_update" and row.get("id") in decisions:
            decisions[row["id"]]["outcome"] = row.get("outcome")
            decisions[row["id"]]["outcome_ts"] = row.get("ts")
    return decisions


def cmd_log(args: argparse.Namespace) -> None:
    row = {
        "id": f"dec-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "ts": now_iso(),
        "event": "decision",
        "project": args.project,
        "gate": args.gate,
        "decision": args.decision,
        "score": args.score,
        "reasons": args.reason or [],
    }
    append_jsonl(args.file, row)
    print_json(row)


def cmd_update(args: argparse.Namespace) -> None:
    decisions = folded_decisions(read_jsonl(args.file))
    if args.id not in decisions:
        raise SystemExit(f"decision id not found: {args.id}")
    row = {
        "id": args.id,
        "ts": now_iso(),
        "event": "outcome_update",
        "outcome": args.outcome,
    }
    append_jsonl(args.file, row)
    print_json(row)


def is_missed_build(decision: str, outcome: str) -> bool:
    return decision in {"build", "CONDITIONAL_GO"} and outcome in {
        "killed",
        "alive_no_revenue",
        "pivoted",
        "RETENTION_MISS",
        "ECONOMICS_MISS",
        "PIVOT",
    }


def is_false_hold(decision: str, outcome: str) -> bool:
    return decision in {"hold", "interview", "pivot"} and outcome == "external_success"


def cmd_audit(args: argparse.Namespace) -> None:
    decisions = list(folded_decisions(read_jsonl(args.file)).values())
    by_decision = Counter(row.get("decision", "unknown") for row in decisions)
    by_decision_outcome: dict[str, Counter] = defaultdict(Counter)
    resolved = 0
    false_holds = []
    missed_builds = []

    for row in decisions:
        outcome = row.get("outcome")
        if not outcome:
            continue
        resolved += 1
        decision = row.get("decision", "unknown")
        by_decision_outcome[decision][outcome] += 1
        if is_false_hold(decision, outcome):
            false_holds.append(row["id"])
        if is_missed_build(decision, outcome):
            missed_builds.append(row["id"])

    correct = resolved - len(false_holds) - len(missed_builds)
    pending = len(decisions) - resolved
    guidance = []
    if false_holds:
        guidance.append("Review hold/pivot threshold; external success appeared after a non-build decision.")
    if missed_builds:
        guidance.append("Tighten build gate evidence or economics checks; build decisions later failed.")
    if pending:
        guidance.append("Backfill pending outcomes when 3-6 month evidence is available.")
    if not guidance:
        guidance.append("No calibration warnings.")

    summary = {
        "total": len(decisions),
        "resolved": resolved,
        "pending": pending,
        "by_decision": dict(by_decision),
        "by_decision_outcome": {k: dict(v) for k, v in by_decision_outcome.items()},
        "hit_rate": round(correct / resolved, 4) if resolved else None,
        "false_holds": false_holds,
        "missed_builds": missed_builds,
        "guidance": guidance,
    }
    print_json(summary)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=LOG_PATH, help="JSONL path")
    sub = parser.add_subparsers(dest="command", required=True)

    log = sub.add_parser("log", help="Append a decision")
    log.add_argument("--project", required=True)
    log.add_argument("--gate", required=True)
    log.add_argument("--decision", required=True)
    log.add_argument("--score", required=True, type=int)
    log.add_argument("--reason", action="append", default=[])
    log.set_defaults(func=cmd_log)

    update = sub.add_parser("update", help="Append an outcome update")
    update.add_argument("--id", required=True)
    update.add_argument("--outcome", required=True)
    update.set_defaults(func=cmd_update)

    audit = sub.add_parser("audit", help="Summarize decision accuracy")
    audit.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
