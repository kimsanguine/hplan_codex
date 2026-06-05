#!/usr/bin/env python3
"""Validate basic Mermaid fenced blocks in Markdown files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def validate_mermaid(path: Path) -> tuple[int, list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    block_count = 0
    in_mermaid = False
    block_start = 0
    has_body = False

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not in_mermaid and stripped.startswith("```mermaid"):
            in_mermaid = True
            block_start = line_no
            has_body = False
            continue

        if in_mermaid and stripped.startswith("```"):
            if not has_body:
                errors.append(f"{path}:{block_start}: empty mermaid block")
            block_count += 1
            in_mermaid = False
            continue

        if in_mermaid and stripped:
            has_body = True

    if in_mermaid:
        errors.append(f"{path}:{block_start}: unclosed mermaid block")

    return block_count, errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Mermaid fenced blocks")
    parser.add_argument("paths", nargs="+", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    total_blocks = 0
    all_errors: list[str] = []

    for path in args.paths:
        if not path.exists():
            all_errors.append(f"{path}: file not found")
            continue
        block_count, errors = validate_mermaid(path)
        total_blocks += block_count
        all_errors.extend(errors)

    if all_errors:
        for error in all_errors:
            print(error)
        return 1

    print(f"Mermaid blocks valid: {total_blocks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
