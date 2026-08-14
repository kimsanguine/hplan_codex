import json
import os
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "hplan-core-fixture"
EXPECTED_CORE_COMMIT = "3055f65e52991e226cc1aabd6fa0f31071aa99d7"
EXPECTED_CONTRACT_SOURCE_SHA256 = "aa5a43827a850892d4b3dab4c2520104cbade9529e835b8bd933ae462d7e263d"
EXPECTED_RAW_FILE_SHA256 = {
    "contracts/rules.json": "c6369184840c4176af8e0b369dc441dc6909ee9ecd6c373a967f18204ef4cfa1",
    "contracts/capabilities.json": "9ece4dd6addbb2605ba07058337926b192bea7fa212bdbdda8748c8421af7e5d",
    "contracts/aliases.json": "b55560c47d3a50aca0af41b80a2592a8d20b9b88c96b78c241af20ac7bd814ff",
    "scripts/render_adapter_snapshot.py": "69d5fd7c5bba7bb68fec44be3e12d74e7ca32197fd9b6f51125adf31f9fa99d7",
    "scripts/validate_core.py": "784224b0c2781cd1a118fcfbc12d878b5c0cbde8b398d18c736ceb4115651477",
}


def find_core_root() -> Path | None:
    configured = os.environ.get("HPLAN_CORE_DIR")
    candidates = [Path(configured)] if configured else []
    if not configured:
        candidates.append(FIXTURE_ROOT)
    candidates.extend(parent / "hplan-core" for parent in ROOT.parents)
    for candidate in candidates:
        renderer = candidate / "scripts" / "render_adapter_snapshot.py"
        if renderer.is_file():
            return candidate.resolve()
    return None


CORE_ROOT = find_core_root()
CORE_RENDERER = CORE_ROOT / "scripts" / "render_adapter_snapshot.py" if CORE_ROOT else None


class HplanCoreAdapterTests(unittest.TestCase):
    def test_ci_mode_uses_checked_in_pinned_core_fixture_without_environment(self):
        original = os.environ.pop("HPLAN_CORE_DIR", None)
        try:
            core_root = find_core_root()
        finally:
            if original is not None:
                os.environ["HPLAN_CORE_DIR"] = original

        self.assertEqual(FIXTURE_ROOT.resolve(), core_root)
        self.assertTrue((core_root / "PROVENANCE.json").is_file())

    def test_fixture_provenance_matches_independent_raw_hashes_and_contract_digest(self):
        provenance = json.loads((FIXTURE_ROOT / "PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED_CORE_COMMIT, provenance["source_commit"])
        self.assertEqual(EXPECTED_CONTRACT_SOURCE_SHA256, provenance["contract_source_sha256"])
        self.assertEqual(EXPECTED_RAW_FILE_SHA256, provenance["raw_file_sha256"])

        for relative_path, expected_hash in EXPECTED_RAW_FILE_SHA256.items():
            with self.subTest(relative_path=relative_path):
                actual_hash = hashlib.sha256((FIXTURE_ROOT / relative_path).read_bytes()).hexdigest()
                self.assertEqual(expected_hash, actual_hash)

        digest = hashlib.sha256()
        for filename in ("rules.json", "capabilities.json", "aliases.json"):
            digest.update(filename.encode("utf-8"))
            digest.update(b"\0")
            digest.update((FIXTURE_ROOT / "contracts" / filename).read_bytes())
            digest.update(b"\0")
        self.assertEqual(EXPECTED_CONTRACT_SOURCE_SHA256, digest.hexdigest())

    def render_core_snapshot(self, output_dir):
        self.assertIsNotNone(
            CORE_RENDERER,
            "Set HPLAN_CORE_DIR to a checkout containing scripts/render_adapter_snapshot.py for core parity tests.",
        )
        return subprocess.run(
            [sys.executable, str(CORE_RENDERER), "--target", "codex", "--output-dir", str(output_dir)],
            cwd=CORE_ROOT,
            text=True,
            capture_output=True,
        )

    def test_snapshot_files_match_current_core_renderer_byte_for_byte(self):
        targets = {
            "hplan-core.lock": ROOT / "runtime" / "hplan-core" / "hplan-core.lock",
            "hplan-capability-matrix.json": ROOT / "runtime" / "hplan-core" / "hplan-capability-matrix.json",
            "HPLAN_CAPABILITY_MATRIX.md": ROOT / "runtime" / "hplan-core" / "HPLAN_CAPABILITY_MATRIX.md",
            "hplan-core-adapter.json": ROOT / "runtime" / "hplan-core" / "hplan-core-adapter.json",
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
        lock_path = ROOT / "runtime" / "hplan-core" / "hplan-core.lock"
        matrix_path = ROOT / "runtime" / "hplan-core" / "hplan-capability-matrix.json"
        adapter_path = ROOT / "runtime" / "hplan-core" / "hplan-core-adapter.json"
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
