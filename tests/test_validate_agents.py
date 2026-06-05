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


if __name__ == "__main__":
    unittest.main()
