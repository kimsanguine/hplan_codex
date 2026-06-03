#!/usr/bin/env python3
"""validate_agents.py — hplan_codex skill validator (Codex layout)"""
import pathlib, sys

FORBIDDEN = "clau" + "de"
REPO_ROOT = pathlib.Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

errors = []
skill_count = 0

for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
    skill_count += 1
    content = skill_md.read_text()
    if FORBIDDEN in content.lower():
        lines = [i+1 for i, l in enumerate(content.splitlines()) if FORBIDDEN in l.lower()]
        errors.append(f"FORBIDDEN: {FORBIDDEN} found in {skill_md.relative_to(REPO_ROOT)} at lines {lines}")
    if not content.startswith("---"):
        errors.append(f"Missing frontmatter in {skill_md.relative_to(REPO_ROOT)}")
    # frontmatter must have name + description
    fm = content.split("---", 2)
    if len(fm) >= 3:
        head = fm[1]
        if "name:" not in head:
            errors.append(f"Missing 'name:' in {skill_md.relative_to(REPO_ROOT)}")
        if "description:" not in head:
            errors.append(f"Missing 'description:' in {skill_md.relative_to(REPO_ROOT)}")

# AGENTS.md / README forbidden check
for doc in ["AGENTS.md", "README.md", "README-ko.md", "CHANGELOG.md"]:
    p = REPO_ROOT / doc
    if p.exists() and FORBIDDEN in p.read_text().lower():
        errors.append(f"FORBIDDEN: {FORBIDDEN} found in {doc}")

print(f"Skills found: {skill_count}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  x {e}")
    sys.exit(1)
print(f"All {skill_count} skills valid. No forbidden references found.")
