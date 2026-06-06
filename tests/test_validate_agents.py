#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import dedent
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_agents.py"


class ValidateAgentsTests(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def write_skill(self, root: Path, dirname: str, name: str, body: str = "") -> None:
        skill_dir = root / "skills" / dirname
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            dedent(
                f"""\
                ---
                name: {name}
                description: "Test skill"
                ---

                {body}
                """
            ),
            encoding="utf-8",
        )

    def test_valid_skill_pack_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "tool.py").write_text("print('ok')\n", encoding="utf-8")
            self.write_skill(root, "demo", "demo", "Run `python3 scripts/tool.py`.")

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("All 1 skills valid", result.stdout)

    def test_frontmatter_name_must_match_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "demo", "other")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Name mismatch", result.stdout)

    def test_missing_script_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(
                root,
                "demo",
                "demo",
                "Run `python3 hplan/scripts/missing_report.py --json`.",
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing script reference", result.stdout)
            self.assertIn("scripts/missing_report.py", result.stdout)

    def test_missing_bare_script_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(
                root,
                "demo",
                "demo",
                "Validate with `scripts/missing_bare.py` before shipping.",
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing script reference", result.stdout)
            self.assertIn("scripts/missing_bare.py", result.stdout)

    def test_missing_script_reference_in_docs_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "demo", "demo", "Call `$demo`.")
            docs = root / "docs"
            docs.mkdir()
            (docs / "BAD.md").write_text(
                "Run `python3 scripts/not_real.py` before shipping.\n",
                encoding="utf-8",
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing script reference", result.stdout)
            self.assertIn("docs/BAD.md", result.stdout)
            self.assertIn("scripts/not_real.py", result.stdout)

    def test_available_skill_reference_passes_without_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "demo", "demo", "Call `$demo` from docs.")
            (root / "README.md").write_text("Start with `$demo`.\n", encoding="utf-8")

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_skill_reference_requires_registry_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "demo", "demo", "Route to `$future-skill`.")

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unregistered skill reference", result.stdout)
            self.assertIn("$future-skill", result.stdout)

    def test_registered_planned_skill_reference_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "demo", "demo", "Route to `$future-skill`.")
            registry = root / "schemas" / "skill_reference_registry.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                dedent(
                    """\
                    {
                      "references": {
                        "future-skill": {
                          "status": "planned",
                          "reason": "Roadmap placeholder."
                        }
                      }
                    }
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_validator(root)

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_registry_status_must_be_explicit_allowed_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_skill(root, "demo", "demo", "Route to `$future-skill`.")
            registry = root / "schemas" / "skill_reference_registry.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                '{"references":{"future-skill":{"status":"maybe"}}}\n',
                encoding="utf-8",
            )

            result = self.run_validator(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid registry status", result.stdout)


if __name__ == "__main__":
    unittest.main()
