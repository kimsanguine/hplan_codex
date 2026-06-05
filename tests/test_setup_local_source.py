#!/usr/bin/env python3
import os
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "scripts" / "setup.sh"


class SetupLocalSourceTests(unittest.TestCase):
    def test_setup_can_install_from_local_source_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["HPLAN_CODEX_SOURCE_DIR"] = str(REPO_ROOT)

            result = subprocess.run(
                ["bash", str(SETUP), f"--dir={tmp}"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            for rel_path in [
                "AGENTS.md",
                "config.toml.example",
                "harness/PRD.md.template",
                "scripts/decision_log.py",
                "scripts/exclusions_registry.py",
                "scripts/generate_report.py",
                "scripts/interview_synthesis.py",
                "scripts/ost_generator.py",
                "scripts/track-probe.sh",
                "scripts/validate_agents.py",
            ]:
                with self.subTest(rel_path=rel_path):
                    self.assertTrue((Path(tmp) / rel_path).exists(), rel_path)


if __name__ == "__main__":
    unittest.main()
