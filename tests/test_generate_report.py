import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "generate_report.py"
sys.path.insert(0, str(REPO_ROOT))


class EvidenceReportTests(unittest.TestCase):
    def test_strong_evidence_scores_build_with_no_missing_axes(self):
        from scripts.generate_report import generate_report

        payload = {
            "idea": "AI inbox triage for security review requests",
            "target": "B2B SaaS security leads who review vendor questionnaires every week",
            "hypothesis": (
                "Last week three enterprise deals stalled because questionnaires took "
                "two days each and created renewal risk."
            ),
            "alternatives": (
                "They use spreadsheets, Slack threads, and a compliance consultant "
                "workaround today."
            ),
            "features": "Import questionnaire, draft answer, cite source",
            "interview_notes": "\n".join(
                [
                    "Yesterday I lost a $40k expansion because the answer was late.",
                    "We pay a consultant $3k per month and would switch if citations are reliable.",
                    "I can introduce five security leads in my peer group.",
                ]
            ),
        }

        report = generate_report(payload)

        self.assertGreaterEqual(report["score"], 75)
        self.assertEqual(report["decision"], "build")
        self.assertEqual(report["missing"], [])
        self.assertEqual(set(report["axes"].keys()), set(report["rubric"].keys()))
        self.assertEqual(sum(axis["score"] for axis in report["axes"].values()), report["score"])
        self.assertTrue(report["build_conditions"]["economic_pain"])
        self.assertGreaterEqual(report["build_conditions"]["interview_lines"], 2)

    def test_high_score_without_interviews_is_forced_to_interview(self):
        from scripts.generate_report import generate_report

        payload = {
            "idea": "AI inbox triage for security review requests",
            "target": "B2B SaaS security leads who review vendor questionnaires every week",
            "hypothesis": "Yesterday a $40k deal was delayed by compliance risk.",
            "alternatives": "spreadsheet workaround, consultant, Slack",
            "features": "Import questionnaire, draft answer, cite source",
            "interview_notes": "One note mentions $40k revenue risk.",
        }

        report = generate_report(payload)

        self.assertGreaterEqual(report["score"], 75)
        self.assertEqual(report["decision"], "interview")
        self.assertEqual(report["build_conditions"]["interview_lines"], 1)

    def test_thin_evidence_lists_missing_axes_and_holds(self):
        from scripts.generate_report import generate_report

        payload = {
            "idea": "AI productivity app",
            "target": "everyone",
            "hypothesis": "People want to save time someday.",
            "alternatives": "",
            "features": "Chat, dashboard, analytics, reminders, templates",
            "interview_notes": "",
        }

        report = generate_report(payload)

        self.assertLess(report["score"], 35)
        self.assertEqual(report["decision"], "hold")
        self.assertIn("icp_specificity", report["missing"])
        self.assertIn("economic_pain", report["missing"])
        self.assertIn("mvp_narrowness", report["missing"])

    def test_cli_outputs_json_and_markdown(self):
        payload = {
            "idea": "AI billing dispute copilot",
            "target": "finance operators who handle invoice disputes weekly",
            "hypothesis": "Last month disputes delayed cash collection and caused revenue risk.",
            "alternatives": "email templates, spreadsheet tracker, outsourced collector",
            "features": ["Detect dispute", "Draft reply", "Track promise"],
            "interview_notes": [
                "Yesterday a late reply delayed $12k cash collection.",
                "I would switch if it reduced dispute risk without breaking NetSuite.",
            ],
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(payload, handle)
            input_path = Path(handle.name)

        try:
            json_result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path), "--json"],
                check=True,
                text=True,
                capture_output=True,
            )
            parsed = json.loads(json_result.stdout)
            self.assertEqual(parsed["decision"], "build")

            markdown_result = subprocess.run(
                [sys.executable, str(SCRIPT), str(input_path)],
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertIn("# Evidence Rubric Report", markdown_result.stdout)
            self.assertIn("Decision: `build`", markdown_result.stdout)
            self.assertIn("| Axis | Score | Max |", markdown_result.stdout)
        finally:
            input_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
