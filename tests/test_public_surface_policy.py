"""Regression checks for files intentionally excluded from the public package."""

import unittest
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_CORE = ROOT / "runtime" / "hplan-core"


class PublicSurfacePolicyTests(unittest.TestCase):
    def test_docs_and_archive_are_not_public_repository_directories(self):
        """Public source must not retain private docs or archived material."""
        self.assertFalse((ROOT / "docs").exists())
        self.assertFalse((ROOT / ".archive").exists())

    def test_no_tracked_path_contains_private_directory_component(self):
        """Nested installer backups must obey the same public-source policy."""
        result = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True
        )
        tracked_paths = result.stdout.splitlines()
        forbidden = [
            path
            for path in tracked_paths
            if {"docs", ".archive"}.intersection(path.split("/"))
        ]
        self.assertEqual([], forbidden)

    def test_gitignore_rejects_future_docs_and_archive_additions(self):
        """The policy needs an explicit guard in addition to removing current files."""
        ignore_rules = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/docs/", ignore_rules)
        self.assertIn("/.archive/", ignore_rules)

    def test_runtime_core_contains_the_four_active_snapshot_artifacts(self):
        """Install and health tooling need data assets without a public docs directory."""
        for filename in (
            "hplan-core.lock",
            "hplan-capability-matrix.json",
            "HPLAN_CAPABILITY_MATRIX.md",
            "hplan-core-adapter.json",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((RUNTIME_CORE / filename).is_file())


if __name__ == "__main__":
    unittest.main()
