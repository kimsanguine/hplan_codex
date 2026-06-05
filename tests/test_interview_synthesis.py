#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "interview_synthesis.py"


class InterviewSynthesisTests(unittest.TestCase):
    def test_import_tag_audit_creates_persona_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pain = root / "pain.md"
            interviews = root / "interviews.jsonl"
            personas = root / "PERSONA_SPECS.json"
            pain.write_text(
                """# Pain Evidence

- Source: HR manager, 200-person startup
- Date: 2026-06-01
- Quote: "Manual onboarding checks cost us two hours every Monday."

- Source: Finance lead, SaaS
- Date: 2026-06-02
- Quote: "Approval delays create churn risk when invoices wait."
""",
                encoding="utf-8",
            )

            imported = subprocess.run(
                [sys.executable, str(SCRIPT), "import", "--input", str(pain), "--out", str(interviews)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(imported.returncode, 0, imported.stdout)
            self.assertTrue(interviews.exists())

            tagged = subprocess.run(
                [sys.executable, str(SCRIPT), "tag", "--input", str(interviews), "--out", str(personas)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(tagged.returncode, 0, tagged.stdout)
            data = json.loads(personas.read_text(encoding="utf-8"))
            self.assertEqual([p["id"] for p in data], ["P01", "P02"])
            self.assertEqual(data[0]["source"], "HR manager, 200-person startup")
            self.assertIn("cost", data[0]["anxiety_tags"])

            audited = subprocess.run(
                [sys.executable, str(SCRIPT), "audit", "--input", str(personas)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(audited.returncode, 0, audited.stdout)
            self.assertIn("interview_evidence_verified: true", audited.stdout)


if __name__ == "__main__":
    unittest.main()
