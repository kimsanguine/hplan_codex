#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate-mermaid.py"


class ValidateMermaidTests(unittest.TestCase):
    def test_accepts_markdown_with_mermaid_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagram.md"
            path.write_text(
                """# Diagram

```mermaid
graph TD
  a["A"] --> b["B"]
```
""",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Mermaid blocks valid: 1", result.stdout)

    def test_rejects_unclosed_mermaid_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.md"
            path.write_text("```mermaid\ngraph TD\n  a --> b\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unclosed mermaid block", result.stdout)


if __name__ == "__main__":
    unittest.main()
