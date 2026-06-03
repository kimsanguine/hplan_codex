#!/usr/bin/env python3
"""
validate_agents.py — hplan_codex skill validator
Checks: skill count, no forbidden strings, frontmatter format
"""
import os, pathlib, sys

# Forbidden brand reference — split to avoid self-detection
FORBIDDEN = "clau" + "de"

REPO_ROOT = pathlib.Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

PLUGINS = ["hplan", "discover", "architect", "deliver", "operate"]

errors = []
skill_count = 0

for plugin in PLUGINS:
    plugin_dir = SKILLS_DIR / plugin
    if not plugin_dir.exists():
        errors.append(f"Missing plugin directory: skills/{plugin}/")
        continue
    skills = list(plugin_dir.glob("*.md"))
    skill_count += len(skills)
    for skill_file in skills:
        content = skill_file.read_text()
        # Check no forbidden brand references
        if FORBIDDEN in content.lower():
            lines = [i+1 for i, l in enumerate(content.splitlines()) if FORBIDDEN in l.lower()]
            errors.append(f"FORBIDDEN: {FORBIDDEN} found in {skill_file.relative_to(REPO_ROOT)} at lines {lines}")
        # Check frontmatter
        if not content.startswith("---"):
            errors.append(f"Missing frontmatter in {skill_file.relative_to(REPO_ROOT)}")

# Check AGENTS.md
agents_md = REPO_ROOT / "AGENTS.md"
if agents_md.exists():
    if FORBIDDEN in agents_md.read_text().lower():
        errors.append(f"FORBIDDEN: {FORBIDDEN} found in AGENTS.md")
else:
    errors.append("Missing AGENTS.md")

print(f"Skills found: {skill_count}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  x {e}")
    sys.exit(1)
else:
    print(f"All {skill_count} skills valid. No forbidden references found.")

