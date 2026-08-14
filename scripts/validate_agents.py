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
CORE_ADAPTER_FILES = {
    "lock": pathlib.Path("hplan-core.lock"),
    "matrix": pathlib.Path("docs/hplan-capability-matrix.json"),
    "adapter": pathlib.Path("docs/hplan-core-adapter.json"),
}
CORE_RULE_IDS = {
    "think-before-coding",
    "simplicity-first",
    "surgical-changes",
    "goal-driven-execution",
    "models-for-judgment-only",
    "tests-verify-intent",
    "checkpoint-after-significant-step",
    "fail-loud",
    "agent-scope-declaration",
}
CORE_ALIASES = {
    "roadmap": "prd",
    "router": "orchestration",
    "stakeholder-update": "ops-review",
}
CORE_RENDERED_FILES = [
    "hplan-core.lock",
    "hplan-capability-matrix.json",
    "HPLAN_CAPABILITY_MATRIX.md",
    "hplan-core-adapter.json",
]
CORE_ADAPTER_POLICY = {
    "capability_status_source": "hplan-capability-matrix.json",
    "native_execution_policy": "entrypoint-and-smoke-fixture-required",
    "non_native_fallback": "fallback_artifact",
    "external_connector_writes": "disabled",
}
CORE_RULE_HEADINGS = {
    "Rule 1 — Think Before Coding",
    "Rule 2 — Simplicity First",
    "Rule 3 — Surgical Changes",
    "Rule 4 — Goal-Driven Execution",
    "Rule 5 — Models for Judgment Tasks Only",
    "Rule 6 — Tests Verify Intent",
    "Rule 7 — Checkpoint After Every Significant Step",
    "Rule 8 — Fail Loud",
    "Rule 9 — Agent Scope Declaration",
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


def load_json(path: pathlib.Path, errors: list[str]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Malformed core adapter file {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"Malformed core adapter file {path}: expected object")
        return None
    return value


def check_core_adapter_contract(repo_root: pathlib.Path, errors: list[str]) -> str | None:
    if not (repo_root / "AGENTS.md").exists():
        return None

    paths = {name: repo_root / relative for name, relative in CORE_ADAPTER_FILES.items()}
    missing = [str(CORE_ADAPTER_FILES[name]) for name, path in paths.items() if not path.is_file()]
    if missing:
        errors.append("Missing core adapter files: " + ", ".join(missing))
        return None

    lock = load_json(paths["lock"], errors)
    matrix = load_json(paths["matrix"], errors)
    adapter = load_json(paths["adapter"], errors)
    if lock is None or matrix is None or adapter is None:
        return None

    if lock.get("target") != "codex" or matrix.get("target") != "codex" or adapter.get("target") != "codex":
        errors.append("Core adapter target must be codex in lock, matrix, and adapter metadata")
    if not re.fullmatch(r"[0-9a-f]{64}", str(lock.get("source_sha256", ""))):
        errors.append("Core adapter lock must contain a SHA-256 source digest")
    if lock.get("files") != CORE_RENDERED_FILES:
        errors.append("Core adapter lock must list all 4 renderer artifacts")

    capabilities = matrix.get("capabilities")
    if not isinstance(capabilities, list) or len(capabilities) != 34:
        errors.append("Core capability matrix must contain exactly 34 canonical capabilities")
    else:
        capability_ids = [item.get("capability_id") for item in capabilities if isinstance(item, dict)]
        states = [item.get("support_state") for item in capabilities if isinstance(item, dict)]
        if len(capability_ids) != 34 or len(set(capability_ids)) != 34:
            errors.append("Core capability matrix must use 34 unique capability IDs")
        if any(item.get("canonical_owner") != "hplan-core" for item in capabilities if isinstance(item, dict)):
            errors.append("Core capability matrix must preserve hplan-core ownership")
        if any(state not in {"native", "adapter-required", "unavailable"} for state in states):
            errors.append("Core capability matrix contains an invalid support state")
        if not any(state != "native" for state in states):
            errors.append("Core capability matrix must expose non-native support states")

    rules = matrix.get("rules")
    rule_ids = {item.get("rule_id") for item in rules if isinstance(item, dict)} if isinstance(rules, list) else set()
    if not isinstance(rules, list) or len(rules) != 9 or rule_ids != CORE_RULE_IDS:
        errors.append("Core capability matrix must preserve the 9 Behavioral Rules")

    aliases = matrix.get("aliases")
    alias_map = {item.get("alias_id"): item.get("target") for item in aliases if isinstance(item, dict)} if isinstance(aliases, list) else {}
    if not isinstance(aliases, list) or len(aliases) != 3 or alias_map != CORE_ALIASES:
        errors.append("Core capability matrix must preserve the 3 compatibility aliases")

    if adapter.get("core_version") != matrix.get("contract_version") or adapter.get("core_source_sha256") != lock.get("source_sha256"):
        errors.append("Adapter metadata must match the rendered core version and source digest")
    for key, value in CORE_ADAPTER_POLICY.items():
        if adapter.get(key) != value:
            errors.append(f"Adapter metadata must preserve core policy: {key}={value}")

    agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    if "## 9 Behavioral Rules" not in agents or not all(f"### {heading}" in agents for heading in CORE_RULE_HEADINGS):
        errors.append("AGENTS.md must declare all 9 Behavioral Rules")
    for route in ("roadmap → prd --mode roadmap", "router → orchestration --pattern router", "stakeholder-update → ops-review"):
        if route not in agents:
            errors.append(f"AGENTS.md must declare compatibility alias: {route}")

    if errors:
        return None
    return "HPLAN core adapter contract valid: 34 capabilities, 9 rules, 3 aliases."


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
    core_adapter_summary = check_core_adapter_contract(args.root.resolve(), errors)

    print(f"Skills found: {skill_count}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  x {error}")
        sys.exit(1)
    if core_adapter_summary:
        print(core_adapter_summary)
    print(f"All {skill_count} skills valid. No forbidden references found.")


if __name__ == "__main__":
    main()
