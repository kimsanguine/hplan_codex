import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "exclusions_registry.py"


class ExclusionsRegistryCliTest(unittest.TestCase):
    def run_cli(self, cwd, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        )

    def test_add_check_and_list_detects_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            added = self.run_cli(
                tmp,
                "add",
                "AI marketing copy generator",
                "--why",
                "incumbents own the generic wedge",
                "--reopen",
                "3 enterprise compliance interviews",
                "--competitor",
                "Incumbent A",
                "--competitor",
                "Incumbent B",
            )
            entry = json.loads(added.stdout)
            self.assertEqual(entry["idea"], "AI marketing copy generator")
            self.assertEqual(entry["reopen_trigger"], "3 enterprise compliance interviews")

            path = Path(tmp) / "harness" / "exclusions.jsonl"
            self.assertTrue(path.exists())

            collision = self.run_cli(tmp, "check", "generic AI marketing copy tool")
            result = json.loads(collision.stdout)
            self.assertEqual(result["verdict"], "COLLISION")
            self.assertEqual(result["matches"][0]["idea"], "AI marketing copy generator")

            listed = self.run_cli(tmp, "list")
            rows = json.loads(listed.stdout)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["competitors"], ["Incumbent A", "Incumbent B"])


if __name__ == "__main__":
    unittest.main()
