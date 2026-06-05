import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "decision_log.py"


class DecisionLogCliTest(unittest.TestCase):
    def run_cli(self, cwd, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_log_update_and_audit_decision_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = self.run_cli(
                tmp,
                "log",
                "--project",
                "alpha-app",
                "--gate",
                "build",
                "--decision",
                "build",
                "--score",
                "78",
                "--reason",
                "5/5 strong signal",
                "--reason",
                "COGS GREEN",
            )
            entry = json.loads(log.stdout)

            path = Path(tmp) / "harness" / "decisions.jsonl"
            self.assertTrue(path.exists())
            self.assertEqual(entry["project"], "alpha-app")
            self.assertEqual(entry["reasons"], ["5/5 strong signal", "COGS GREEN"])

            updated = self.run_cli(tmp, "update", "--id", entry["id"], "--outcome", "shipped")
            update_entry = json.loads(updated.stdout)
            self.assertEqual(update_entry["id"], entry["id"])
            self.assertEqual(update_entry["outcome"], "shipped")

            audit = self.run_cli(tmp, "audit")
            summary = json.loads(audit.stdout)
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["resolved"], 1)
            self.assertEqual(summary["pending"], 0)
            self.assertEqual(summary["hit_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
