#!/usr/bin/env python3
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "scripts" / "setup.sh"


class SetupManifestTests(unittest.TestCase):
    def test_setup_installs_all_helper_scripts(self):
        setup = SETUP.read_text(encoding="utf-8")
        for script in [
            "cogs_sentinel.py",
            "decision_log.py",
            "exclusions_registry.py",
            "generate_report.py",
            "interview_synthesis.py",
            "ost_generator.py",
            "validate-mermaid.py",
            "track-probe.sh",
            "validate_agents.py",
        ]:
            with self.subTest(script=script):
                self.assertIn(script, setup)


if __name__ == "__main__":
    unittest.main()
