#!/usr/bin/env python3
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "quality-gate.yml"


class QualityGateWorkflowTests(unittest.TestCase):
    def test_workflow_runs_setup_golden_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("HPLAN_CODEX_SOURCE_DIR", workflow)
        self.assertIn("scripts/setup.sh --dir=", workflow)
        self.assertIn("scripts/cogs_sentinel.py", workflow)
        self.assertIn("scripts/generate_report.py", workflow)
        self.assertIn("scripts/decision_log.py", workflow)
        self.assertIn("scripts/validate_agents.py", workflow)
        self.assertIn("runtime/hplan-core/hplan-core.lock", workflow)
        self.assertIn("runtime/hplan-core/hplan-capability-matrix.json", workflow)
        self.assertIn("HPLAN_CORE_DIR: ${{ github.workspace }}/hplan-core-fixture", workflow)
        self.assertIn("Smoke test track probe", workflow)
        self.assertIn(".track/actual_log.jsonl", workflow)


if __name__ == "__main__":
    unittest.main()
