#!/usr/bin/env python3
"""validate_agents.py — hplan_codex skill validator (Codex layout)"""
import argparse
import json
import pathlib
import re
import sys

FORBIDDEN = "clau" + "de"
REGISTRY_PATH = pathlib.Path("schemas/skill_reference_registry.json")
ALLOWED_REFERENCE_STATUSES = {
    "planned",
    "adapter-dependent",
    "script-only",
    "external",
}

SCRIPT_REF_RE = re.compile(
    r"(?:\b(?:python3|python|bash|sh)\s+(?:hplan/)?|[`'\"(])"
    r"(scripts/[A-Za-z0-9_.-]+\.(?:py|sh))"
    r"(?=[`'\"),\s]|$)"
)
SKILL_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_])\$([a-z][a-z0-9]*(?:-[a-z0-9]+)*)(?![A-Za-z0-9_-])"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate hplan_codex skill files")
    parser.add_argument(
        "--root",
        default=pathlib.Path(__file__).parent.parent,
        type=pathlib.Path,
        help="Repository root to validate (default: parent of this script)",
    )
    return parser.parse_args()


def frontmatter_value(head: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", head, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def check_script_references(root: pathlib.Path, rel_path: pathlib.Path, content: str, errors: list[str]) -> None:
    for match in SCRIPT_REF_RE.finditer(content):
        script_rel = pathlib.Path(match.group(1))
        if not (root / script_rel).exists():
            errors.append(
                f"Missing script reference in {rel_path}: {script_rel}"
            )


def load_skill_reference_registry(root: pathlib.Path, errors: list[str]) -> dict[str, str]:
    path = root / REGISTRY_PATH
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Malformed skill reference registry {REGISTRY_PATH}: {exc}")
        return {}

    references = data.get("references")
    if not isinstance(references, dict):
        errors.append(f"Malformed skill reference registry {REGISTRY_PATH}: missing object 'references'")
        return {}

    registry: dict[str, str] = {}
    for name, entry in sorted(references.items()):
        if not isinstance(entry, dict):
            errors.append(f"Malformed registry entry for ${name}: expected object")
            continue
        status = entry.get("status")
        if status not in ALLOWED_REFERENCE_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_REFERENCE_STATUSES))
            errors.append(f"Invalid registry status for ${name}: {status!r} (allowed: {allowed})")
            continue
        registry[name] = status
    return registry


def check_skill_references(
    rel_path: pathlib.Path,
    content: str,
    available_skills: set[str],
    registered_references: dict[str, str],
    errors: list[str],
) -> None:
    for match in SKILL_REF_RE.finditer(content):
        name = match.group(1)
        if name in available_skills or name in registered_references:
            continue
        errors.append(f"Unregistered skill reference in {rel_path}: ${name}")


def validate(root: pathlib.Path) -> tuple[int, list[str]]:
    repo_root = root.resolve()
    skills_dir = repo_root / "skills"
    errors: list[str] = []
    skill_count = 0

    if not skills_dir.exists():
        errors.append(f"Missing skills directory: {skills_dir}")
        return 0, errors

    available_skills = {
        skill_dir.name
        for skill_dir in skills_dir.iterdir()
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists()
    }
    registered_references = load_skill_reference_registry(repo_root, errors)

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        skill_count += 1
        rel = skill_md.relative_to(repo_root)
        content = skill_md.read_text(encoding="utf-8")

        if FORBIDDEN in content.lower():
            lines = [i + 1 for i, line in enumerate(content.splitlines()) if FORBIDDEN in line.lower()]
            errors.append(f"FORBIDDEN: {FORBIDDEN} found in {rel} at lines {lines}")

        if not content.startswith("---"):
            errors.append(f"Missing frontmatter in {rel}")
            continue

        fm = content.split("---", 2)
        if len(fm) < 3:
            errors.append(f"Malformed frontmatter in {rel}")
            continue

        head = fm[1]
        name = frontmatter_value(head, "name")
        description = frontmatter_value(head, "description")

        if not name:
            errors.append(f"Missing 'name:' in {rel}")
        elif name != skill_md.parent.name:
            errors.append(
                f"Name mismatch in {rel}: frontmatter name '{name}' != directory '{skill_md.parent.name}'"
            )

        if not description:
            errors.append(f"Missing 'description:' in {rel}")

        check_script_references(repo_root, rel, content, errors)
        check_skill_references(rel, content, available_skills, registered_references, errors)

    for doc in ["AGENTS.md", "README.md", "README-ko.md", "CHANGELOG.md"]:
        path = repo_root / doc
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if FORBIDDEN in content.lower():
            errors.append(f"FORBIDDEN: {FORBIDDEN} found in {doc}")
        check_script_references(repo_root, pathlib.Path(doc), content, errors)
        check_skill_references(pathlib.Path(doc), content, available_skills, registered_references, errors)

    for doc in sorted(repo_root.rglob("*.md")):
        rel = doc.relative_to(repo_root)
        if rel.parts[0] in {".git", "skills"} or str(rel) in {"AGENTS.md", "README.md", "README-ko.md", "CHANGELOG.md"}:
            continue
        content = doc.read_text(encoding="utf-8")
        check_script_references(repo_root, rel, content, errors)
        check_skill_references(rel, content, available_skills, registered_references, errors)

    return skill_count, errors


def main() -> None:
    args = parse_args()
    skill_count, errors = validate(args.root)

    print(f"Skills found: {skill_count}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  x {error}")
        sys.exit(1)
    print(f"All {skill_count} skills valid. No forbidden references found.")


if __name__ == "__main__":
    main()
