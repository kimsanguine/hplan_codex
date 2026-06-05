import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "ost_generator.py"


class OstGeneratorCliTest(unittest.TestCase):
    def test_generates_markdown_with_mermaid_and_parking_lot(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "ost.json"
            source.write_text(
                json.dumps(
                    {
                        "outcome": "Solo PM closed-won rate +25% within 90 days",
                        "opportunities": [
                            {
                                "name": "Solo PM cannot create follow-up artifacts after meetings",
                                "evidence_count": 3,
                                "solutions": [
                                    {
                                        "name": "60-second action item draft",
                                        "experiment": "Concierge for 5 ICP",
                                        "decision_rule": "5/5 use without edits",
                                    }
                                ],
                            },
                            {
                                "name": "Solo PM cannot compare stakeholder objections",
                                "evidence_count": 1,
                                "solutions": [],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--out", "docs/OPPORTUNITY_TREE.md"],
                cwd=tmp,
                text=True,
                capture_output=True,
                check=True,
            )

            output = Path(tmp) / "docs" / "OPPORTUNITY_TREE.md"
            self.assertTrue(output.exists())
            content = output.read_text(encoding="utf-8")
            self.assertIn("# Opportunity Solution Tree", content)
            self.assertIn("```mermaid", content)
            self.assertIn("Solo PM closed-won rate +25% within 90 days", content)
            self.assertIn("Parking Lot", content)
            self.assertIn("Concierge for 5 ICP", content)


if __name__ == "__main__":
    unittest.main()
