import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "scripts" / "setup.sh"
DOCTOR = ROOT / "scripts" / "hplan_doctor.py"
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import repair_hplan_core_snapshot as repair  # noqa: E402


class HplanDoctorTests(unittest.TestCase):
    def install_first_success_skills(self, codex_home: Path) -> None:
        for skill_name in ("brainstorm", "socratic-question", "evidence-rubric"):
            skill = codex_home / "skills" / skill_name / "SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text(
                f"---\nname: {skill_name}\ndescription: test fixture\n---\n",
                encoding="utf-8",
            )

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

    def doctor_with_codex(self, target: Path, codex_home: Path) -> subprocess.CompletedProcess[str]:
        fake_bin = target / "fake-bin"
        fake_bin.mkdir(exist_ok=True)
        codex = fake_bin / "codex"
        codex.write_text("#!/usr/bin/env bash\necho 'codex-cli 0.test'\n", encoding="utf-8")
        codex.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
        env["CODEX_HOME"] = str(codex_home)
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
            codex_home = Path(tmp) / "codex-home"
            self.install_first_success_skills(codex_home)
            self.install_fixture(target)

            result = self.doctor_with_codex(target, codex_home)

            self.assertEqual(0, result.returncode, result.stdout)
            self.assertIn("상태: 정상", result.stdout)
            self.assertIn("Codex CLI: 정상 (codex-cli 0.test)", result.stdout)
            self.assertIn("hplan-core 스냅샷: 정상 (34 capabilities, 9 rules, 3 aliases)", result.stdout)
            self.assertIn("다음 행동: `$brainstorm \"아이디어\"`", result.stdout)

    def test_doctor_reports_recovery_when_a_core_artifact_is_missing(self):
        """A printed repair command must restore a normal local installation without a network call."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            codex_home = Path(tmp) / "codex-home"
            self.install_first_success_skills(codex_home)
            self.install_fixture(target)
            (target / "docs" / "hplan-capability-matrix.json").unlink()

            result = self.doctor_with_codex(target, codex_home)

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

            repaired = self.doctor_with_codex(target, codex_home)
            self.assertEqual(0, repaired.returncode, repaired.stdout)
            self.assertIn("상태: 정상", repaired.stdout)

    def test_doctor_escalates_when_lock_core_source_identity_disagrees(self):
        """Ignoring a changed core identity would report a mixed snapshot as safe."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            codex_home = Path(tmp) / "codex-home"
            self.install_first_success_skills(codex_home)
            self.install_fixture(target)
            lock_path = target / "hplan-core.lock"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["core_source_sha256"] = "0" * 64
            lock_path.write_text(json.dumps(lock), encoding="utf-8")

            result = self.doctor_with_codex(target, codex_home)

            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("상태: 강사 호출", result.stdout)
            self.assertIn("core source digest", result.stdout)

    def test_setup_copies_doctor_and_all_core_snapshot_artifacts(self):
        """Dropping a setup manifest entry must leave a detected incomplete local installation."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            codex_home = Path(tmp) / "codex-home"
            self.install_first_success_skills(codex_home)
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
            codex_home = Path(tmp) / "codex-home"
            self.install_first_success_skills(codex_home)
            self.install_fixture(target)
            (target / "docs" / "HPLAN_CAPABILITY_MATRIX.md").write_bytes(b"\xff\xfe")

            result = self.doctor_with_codex(target, codex_home)

            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("상태: 강사 호출", result.stdout)
            self.assertIn("Markdown capability matrix를 읽을 수 없습니다", result.stdout)

    def test_doctor_blocks_first_success_until_skills_are_installed_in_codex_home(self):
        """A project-only setup must not claim brainstorm is usable when CODEX_HOME has no hplan skills."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            empty_codex_home = Path(tmp) / "empty-codex-home"
            self.install_fixture(target)

            result = self.doctor_with_codex(target, empty_codex_home)

            self.assertEqual(1, result.returncode, result.stdout)
            self.assertIn("First-success skills: 자동 복구 가능", result.stdout)
            self.assertIn("$skill-installer https://github.com/kimsanguine/hplan_codex", result.stdout)
            self.assertNotIn("상태: 정상", result.stdout)

    def test_doctor_escalates_when_live_and_repair_backup_artifacts_are_missing(self):
        """A partial repair backup must never be offered as safe automatic recovery."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            codex_home = Path(tmp) / "codex-home"
            self.install_first_success_skills(codex_home)
            self.install_fixture(target)
            live_matrix = target / "docs" / "hplan-capability-matrix.json"
            backup_matrix = target / ".hplan-core-snapshot" / "docs" / "hplan-capability-matrix.json"
            live_matrix.unlink()
            backup_matrix.unlink()

            result = self.doctor_with_codex(target, codex_home)

            self.assertEqual(2, result.returncode, result.stdout)
            self.assertIn("상태: 강사 호출", result.stdout)
            self.assertIn("로컬 복구 백업을 신뢰할 수 없습니다", result.stdout)
            repair = subprocess.run(
                [sys.executable, "scripts/repair_hplan_core_snapshot.py", "--root", "."],
                cwd=target,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(1, repair.returncode, repair.stdout)
            self.assertFalse(live_matrix.exists(), "incomplete backup must not partially restore the live snapshot")

    def test_repair_rolls_back_every_live_artifact_when_second_replace_fails(self):
        """A mid-transaction write failure must not leave the first snapshot artifact replaced."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            self.install_fixture(target)
            before = {}
            for artifact in repair.ARTIFACTS:
                path = target / artifact
                path.write_bytes(f"original-live-{artifact}".encode("utf-8"))
                before[artifact] = path.read_bytes()

            real_replace = repair.os.replace
            calls = 0

            def fail_second_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected second replace failure")
                return real_replace(source, destination)

            with patch.object(repair.os, "replace", side_effect=fail_second_replace):
                success, message = repair.restore(target)

            self.assertFalse(success)
            self.assertIn("이전 상태", message)
            for artifact, expected in before.items():
                with self.subTest(artifact=artifact):
                    self.assertEqual(expected, (target / artifact).read_bytes())

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
