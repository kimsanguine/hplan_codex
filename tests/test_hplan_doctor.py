import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup.sh"
DOCTOR = ROOT / "scripts" / "hplan_doctor.py"


class HplanDoctorTests(unittest.TestCase):
    def install_fixture(self, target: Path) -> None:
        env = os.environ.copy()
        env["HPLAN_CODEX_SOURCE_DIR"] = str(ROOT)
        result = subprocess.run(
            ["bash", str(SETUP), f"--dir={target}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout)

    def doctor_with_codex(self, target: Path) -> subprocess.CompletedProcess[str]:
        fake_bin = target / "fake-bin"
        fake_bin.mkdir(exist_ok=True)
        codex = fake_bin / "codex"
        codex.write_text("#!/usr/bin/env bash\necho 'codex-cli 0.test'\n", encoding="utf-8")
        codex.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
        return subprocess.run(
            [sys.executable, str(target / "scripts" / "hplan_doctor.py"), "--root", str(target)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def test_doctor_reports_normal_for_a_complete_local_install(self):
        """Removing a required snapshot artifact must turn this normal result into recovery status."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.install_fixture(target)

            result = self.doctor_with_codex(target)

            self.assertEqual(0, result.returncode, result.stdout)
            self.assertIn("상태: 정상", result.stdout)
            self.assertIn("Codex CLI: 정상 (codex-cli 0.test)", result.stdout)
            self.assertIn("hplan-core 스냅샷: 정상 (34 capabilities, 9 rules, 3 aliases)", result.stdout)
            self.assertIn("다음 행동: `$brainstorm \"아이디어\"`", result.stdout)

    def test_doctor_reports_recovery_when_a_core_artifact_is_missing(self):
        """A printed repair command must restore a normal local installation without a network call."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.install_fixture(target)
            (target / "docs" / "hplan-capability-matrix.json").unlink()

            result = self.doctor_with_codex(target)

            self.assertEqual(1, result.returncode, result.stdout)
            self.assertIn("상태: 자동 복구 가능", result.stdout)
            self.assertIn("hplan-core 스냅샷: 자동 복구 가능", result.stdout)
            self.assertIn("python3 scripts/repair_hplan_core_snapshot.py --root .", result.stdout)

            repair = subprocess.run(
                [sys.executable, "scripts/repair_hplan_core_snapshot.py", "--root", "."],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(0, repair.returncode, repair.stdout)

            repaired = self.doctor_with_codex(target)
            self.assertEqual(0, repaired.returncode, repaired.stdout)
            self.assertIn("상태: 정상", repaired.stdout)

    def test_doctor_escalates_when_lock_core_source_identity_disagrees(self):
        """Ignoring a changed core identity would report a mixed snapshot as safe."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.install_fixture(target)
            lock_path = target / "hplan-core.lock"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["core_source_sha256"] = "0" * 64
            lock_path.write_text(json.dumps(lock), encoding="utf-8")

            result = self.doctor_with_codex(target)

            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("상태: 강사 호출", result.stdout)
            self.assertIn("core source digest", result.stdout)

    def test_setup_copies_doctor_and_all_core_snapshot_artifacts(self):
        """Dropping a setup manifest entry must leave a detected incomplete local installation."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.install_fixture(target)

            for rel_path in [
                "scripts/hplan_doctor.py",
                "scripts/repair_hplan_core_snapshot.py",
                "hplan-core.lock",
                "docs/hplan-capability-matrix.json",
                "docs/HPLAN_CAPABILITY_MATRIX.md",
                "docs/hplan-core-adapter.json",
                ".hplan-core-snapshot/hplan-core.lock",
                ".hplan-core-snapshot/docs/hplan-capability-matrix.json",
                ".hplan-core-snapshot/docs/HPLAN_CAPABILITY_MATRIX.md",
                ".hplan-core-snapshot/docs/hplan-core-adapter.json",
            ]:
                with self.subTest(rel_path=rel_path):
                    self.assertTrue((target / rel_path).is_file(), rel_path)

    def test_doctor_reports_structured_teacher_status_for_invalid_markdown_bytes(self):
        """An unreadable matrix must not escape as a traceback."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.install_fixture(target)
            (target / "docs" / "HPLAN_CAPABILITY_MATRIX.md").write_bytes(b"\xff\xfe")

            result = self.doctor_with_codex(target)

            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("상태: 강사 호출", result.stdout)
            self.assertIn("Markdown capability matrix를 읽을 수 없습니다", result.stdout)

    def test_local_source_setup_does_not_require_curl_on_path(self):
        """A local installer must not reject an otherwise complete source checkout because curl is absent."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            env = os.environ.copy()
            env["HPLAN_CODEX_SOURCE_DIR"] = str(ROOT)
            env["PATH"] = "/bin"

            result = subprocess.run(
                ["/bin/bash", str(SETUP), f"--dir={target}"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stdout)
            self.assertTrue((target / "scripts" / "hplan_doctor.py").is_file())


if __name__ == "__main__":
    unittest.main()
