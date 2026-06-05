#!/usr/bin/env python3
"""Minimal interview synthesis helper for hplan_codex.

The script turns pain evidence notes into PERSONA_SPECS.json so adversarial QA
can distinguish real interview-backed personas from AI-only placeholders.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TAG_RULES = {
    "cost": ("cost", "money", "budget", "invoice", "margin", "hours", "time"),
    "risk": ("risk", "delay", "approval", "compliance", "legal", "churn"),
    "workflow": ("manual", "spreadsheet", "handoff", "onboarding", "check"),
}


def parse_pain_markdown(text: str) -> list[dict]:
    entries: list[dict] = []
    current: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = re.match(r"-\s*(Source|Date|Quote):\s*(.*)", line, re.IGNORECASE)
        if not match:
            continue

        key = match.group(1).lower()
        value = match.group(2).strip().strip('"')
        if key == "source" and current:
            if current.get("source") or current.get("quote"):
                entries.append(current)
            current = {}
        current[key] = value

    if current.get("source") or current.get("quote"):
        entries.append(current)

    return [
        {
            "source": item.get("source", "unknown"),
            "date": item.get("date", "unknown"),
            "quote": item.get("quote", ""),
        }
        for item in entries
        if item.get("quote")
    ]


def tags_for(text: str) -> list[str]:
    lowered = text.lower()
    tags = [
        tag
        for tag, keywords in TAG_RULES.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    return tags or ["general_pain"]


def experience_level(source: str) -> str:
    lowered = source.lower()
    if any(word in lowered for word in ("lead", "manager", "director", "head", "이사", "팀장")):
        return "숙련"
    return "입문"


def import_notes(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    out_path = Path(args.out)
    entries = parse_pain_markdown(input_path.read_text(encoding="utf-8"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"imported: {len(entries)} interview(s) -> {out_path}")
    return 0 if entries else 1


def tag_interviews(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    out_path = Path(args.out)
    personas = []

    for idx, line in enumerate(input_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        entry = json.loads(line)
        quote = entry.get("quote", "")
        source = entry.get("source", "unknown")
        personas.append(
            {
                "id": f"P{idx:02d}",
                "source": source,
                "date": entry.get("date", "unknown"),
                "quote": quote,
                "trigger": quote[:140],
                "anxiety_tags": tags_for(f"{source} {quote}"),
                "experience_level": experience_level(source),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"tagged: {len(personas)} persona(s) -> {out_path}")
    return 0 if personas else 1


def audit(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    personas = json.loads(input_path.read_text(encoding="utf-8"))
    verified = bool(personas) and all(
        persona.get("id") and persona.get("source") and persona.get("quote")
        for persona in personas
    )
    print(f"persona_count: {len(personas)}")
    print(f"interview_evidence_verified: {'true' if verified else 'false'}")
    return 0 if verified else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import, tag, and audit interview evidence")
    sub = parser.add_subparsers(dest="command", required=True)

    import_cmd = sub.add_parser("import", help="Convert pain.md notes to interviews.jsonl")
    import_cmd.add_argument("--input", default="harness/pain.md")
    import_cmd.add_argument("--out", default="harness/interviews.jsonl")
    import_cmd.set_defaults(func=import_notes)

    tag_cmd = sub.add_parser("tag", help="Convert interviews.jsonl to PERSONA_SPECS.json")
    tag_cmd.add_argument("--input", default="harness/interviews.jsonl")
    tag_cmd.add_argument("--out", default="harness/PERSONA_SPECS.json")
    tag_cmd.set_defaults(func=tag_interviews)

    audit_cmd = sub.add_parser("audit", help="Verify PERSONA_SPECS.json has interview-backed personas")
    audit_cmd.add_argument("--input", default="harness/PERSONA_SPECS.json")
    audit_cmd.set_defaults(func=audit)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
