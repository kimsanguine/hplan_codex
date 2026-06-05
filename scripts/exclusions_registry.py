#!/usr/bin/env python3
"""Manage the hplan do-not-build exclusions registry."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


REGISTRY_PATH = Path("harness") / "exclusions.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def print_json(data) -> None:
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))


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


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[0-9A-Za-z가-힣]+", text.lower()))


def compact(text: str) -> str:
    return "".join(re.findall(r"[0-9A-Za-z가-힣]+", text.lower()))


def bigrams(text: str) -> set[str]:
    value = compact(text)
    if len(value) <= 1:
        return {value} if value else set()
    return {value[i : i + 2] for i in range(len(value) - 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def similarity(left: str, right: str) -> tuple[float, str]:
    left_compact = compact(left)
    right_compact = compact(right)
    if left_compact and right_compact and (
        left_compact in right_compact or right_compact in left_compact
    ):
        return 1.0, "substring"
    token_score = jaccard(tokens(left), tokens(right))
    bigram_score = jaccard(bigrams(left), bigrams(right))
    if token_score >= bigram_score:
        return token_score, "token_jaccard"
    return bigram_score, "char_bigram_jaccard"


def cmd_add(args: argparse.Namespace) -> None:
    row = {
        "id": f"exc-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "ts": now_iso(),
        "idea": args.idea,
        "why": args.why,
        "reopen_trigger": args.reopen,
        "competitors": args.competitor or [],
    }
    append_jsonl(args.file, row)
    print_json(row)


def cmd_check(args: argparse.Namespace) -> None:
    matches = []
    for row in read_jsonl(args.file):
        score, method = similarity(args.idea, row.get("idea", ""))
        if score >= args.threshold:
            matches.append(
                {
                    "id": row.get("id"),
                    "idea": row.get("idea"),
                    "score": round(score, 4),
                    "method": method,
                    "why": row.get("why"),
                    "reopen_trigger": row.get("reopen_trigger"),
                    "competitors": row.get("competitors", []),
                }
            )
    matches.sort(key=lambda row: row["score"], reverse=True)
    print_json({"verdict": "COLLISION" if matches else "CLEAR", "matches": matches})


def cmd_list(args: argparse.Namespace) -> None:
    print_json(read_jsonl(args.file))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=REGISTRY_PATH, help="JSONL path")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Append an exclusion")
    add.add_argument("idea")
    add.add_argument("--why", required=True)
    add.add_argument("--reopen", required=True)
    add.add_argument("--competitor", action="append", default=[])
    add.set_defaults(func=cmd_add)

    check = sub.add_parser("check", help="Check an idea against exclusions")
    check.add_argument("idea")
    check.add_argument("--threshold", type=float, default=0.40)
    check.set_defaults(func=cmd_check)

    list_cmd = sub.add_parser("list", help="List exclusions")
    list_cmd.set_defaults(func=cmd_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
