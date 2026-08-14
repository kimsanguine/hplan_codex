import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = Path("/Users/sanguinekim/Documents/3_Code/Vibe/Project/hplan-core")
CORE_RENDERER = CORE_ROOT / "scripts" / "render_adapter_snapshot.py"


class HplanCoreAdapterTests(unittest.TestCase):
    def render_core_snapshot(self, output_dir):
        return subprocess.run(
            [sys.executable, str(CORE_RENDERER), "--target", "codex", "--output-dir", str(output_dir)],
            cwd=CORE_ROOT,
            text=True,
            capture_output=True,
        )

    def test_snapshot_files_match_current_core_renderer_byte_for_byte(self):
        targets = {
            "hplan-core.lock": ROOT / "hplan-core.lock",
            "hplan-capability-matrix.json": ROOT / "docs" / "hplan-capability-matrix.json",
            "HPLAN_CAPABILITY_MATRIX.md": ROOT / "docs" / "HPLAN_CAPABILITY_MATRIX.md",
            "hplan-core-adapter.json": ROOT / "docs" / "hplan-core-adapter.json",
        }
        with tempfile.TemporaryDirectory() as tmp:
            result = self.render_core_snapshot(Path(tmp))
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for filename, target in targets.items():
                self.assertEqual(
                    (Path(tmp) / filename).read_bytes(),
                    target.read_bytes(),
                    f"{filename} must be regenerated from the current hplan-core renderer",
                )

    def test_codex_snapshot_preserves_core_contract_and_truthful_boundaries(self):
        lock_path = ROOT / "hplan-core.lock"
        matrix_path = ROOT / "docs" / "hplan-capability-matrix.json"
        adapter_path = ROOT / "docs" / "hplan-core-adapter.json"
        self.assertTrue(lock_path.is_file(), "missing hplan-core.lock")
        self.assertTrue(matrix_path.is_file(), "missing Codex capability matrix")
        self.assertTrue(adapter_path.is_file(), "missing adapter status metadata")
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        adapter = json.loads(adapter_path.read_text(encoding="utf-8"))

        self.assertEqual("codex", lock["target"])
        self.assertRegex(lock["source_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual("codex", matrix["target"])
        self.assertEqual(34, len(matrix["capabilities"]))
        self.assertEqual(9, len(matrix["rules"]))
        self.assertEqual(
            ["roadmap", "router", "stakeholder-update"],
            [alias["alias_id"] for alias in matrix["aliases"]],
        )
        self.assertEqual("codex", adapter["target"])
        self.assertEqual(matrix["contract_version"], adapter["core_version"])
        self.assertEqual(lock["source_sha256"], adapter["core_source_sha256"])
        self.assertEqual("hplan-capability-matrix.json", adapter["capability_status_source"])
        self.assertEqual("entrypoint-and-smoke-fixture-required", adapter["native_execution_policy"])
        self.assertEqual("fallback_artifact", adapter["non_native_fallback"])
        self.assertEqual("disabled", adapter["external_connector_writes"])
        non_native_states = {
            capability["support_state"]
            for capability in matrix["capabilities"]
            if capability["support_state"] != "native"
        }
        self.assertTrue(non_native_states)
        self.assertTrue(non_native_states <= {"adapter-required", "unavailable"})

    def test_agents_validator_enforces_snapshot_contract_and_nine_rules(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_agents.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("HPLAN core adapter contract valid: 34 capabilities, 9 rules, 3 aliases.", result.stdout)


if __name__ == "__main__":
    unittest.main()
