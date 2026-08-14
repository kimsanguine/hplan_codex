#!/usr/bin/env python3
"""Read-only health check for a local hplan_codex installation."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


EXPECTED_FILES = [
    "hplan-core.lock",
    "hplan-capability-matrix.json",
    "HPLAN_CAPABILITY_MATRIX.md",
    "hplan-core-adapter.json",
]
EXPECTED_RULE_IDS = {
    "think-before-coding",
    "simplicity-first",
    "surgical-changes",
    "goal-driven-execution",
    "models-for-judgment-only",
    "tests-verify-intent",
    "checkpoint-after-significant-step",
    "fail-loud",
    "agent-scope-declaration",
}
EXPECTED_ALIASES = {
    "roadmap": "prd",
    "router": "orchestration",
    "stakeholder-update": "ops-review",
}
EXPECTED_POLICY = {
    "capability_status_source": "hplan-capability-matrix.json",
    "native_execution_policy": "entrypoint-and-smoke-fixture-required",
    "non_native_fallback": "fallback_artifact",
    "external_connector_writes": "disabled",
}
BACKUP_DIR = ".hplan-core-snapshot"
FIRST_SUCCESS_SKILLS = ("brainstorm", "socratic-question", "evidence-rubric")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only health check for hplan_codex")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Installed hplan_codex project directory (default: parent of this script)",
    )
    return parser.parse_args()


def codex_version() -> tuple[bool, str]:
    executable = shutil.which("codex")
    if executable is None:
        return False, "Codex CLI를 찾지 못했습니다"
    try:
        result = subprocess.run(
            [executable, "--version"], text=True, capture_output=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"Codex CLI 버전을 확인하지 못했습니다 ({exc})"
    version = (result.stdout or result.stderr).strip()
    if result.returncode != 0 or not version:
        return False, "Codex CLI 버전을 확인하지 못했습니다"
    return True, version.splitlines()[0]


def first_success_skills_problem() -> str | None:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    missing = [
        skill_name
        for skill_name in FIRST_SUCCESS_SKILLS
        if not (codex_home / "skills" / skill_name / "SKILL.md").is_file()
    ]
    if missing:
        return f"CODEX_HOME={codex_home}에 누락: {', '.join(missing)}"
    return None


def load_json(path: Path) -> tuple[dict | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "최상위 JSON 값이 object가 아닙니다"
    return value, None


def snapshot_problem(root: Path, artifact_root: Path | None = None) -> tuple[str | None, str | None]:
    artifact_root = artifact_root or root
    paths = {
        "lock": artifact_root / "hplan-core.lock",
        "matrix": artifact_root / "docs" / "hplan-capability-matrix.json",
        "markdown": artifact_root / "docs" / "HPLAN_CAPABILITY_MATRIX.md",
        "adapter": artifact_root / "docs" / "hplan-core-adapter.json",
    }
    try:
        missing = [str(path.relative_to(root)) for path in paths.values() if not path.is_file()]
    except OSError as exc:
        return "teacher", f"snapshot 파일 상태를 읽을 수 없습니다: {exc}"
    if missing:
        return "recovery", "필수 파일 누락: " + ", ".join(missing)

    lock, error = load_json(paths["lock"])
    if error:
        return "teacher", f"hplan-core.lock을 읽을 수 없습니다: {error}"
    matrix, error = load_json(paths["matrix"])
    if error:
        return "teacher", f"capability matrix를 읽을 수 없습니다: {error}"
    adapter, error = load_json(paths["adapter"])
    if error:
        return "teacher", f"adapter metadata를 읽을 수 없습니다: {error}"

    if lock.get("target") != "codex" or matrix.get("target") != "codex" or adapter.get("target") != "codex":
        return "teacher", "스냅샷 target이 codex와 일치하지 않습니다"
    if lock.get("files") != EXPECTED_FILES:
        return "teacher", "hplan-core.lock의 artifact 목록이 일치하지 않습니다"
    digest = lock.get("source_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        return "teacher", "hplan-core.lock의 source digest가 유효하지 않습니다"
    core_digest = lock.get("core_source_sha256")
    if not isinstance(core_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", core_digest):
        return "teacher", "hplan-core.lock의 core source digest가 유효하지 않습니다"
    if matrix.get("contract_version") != lock.get("contract_version") or adapter.get("core_version") != lock.get("contract_version"):
        return "teacher", "contract version이 lock, matrix, adapter 사이에 일치하지 않습니다"
    if adapter.get("core_source_sha256") != core_digest:
        return "teacher", "core source digest가 lock과 adapter 사이에 일치하지 않습니다"
    if any(adapter.get(key) != value for key, value in EXPECTED_POLICY.items()):
        return "teacher", "adapter 안전 정책이 core 계약과 일치하지 않습니다"

    capabilities = matrix.get("capabilities")
    if not isinstance(capabilities, list) or len(capabilities) != 34:
        return "teacher", "capability matrix는 정확히 34개 capability가 필요합니다"
    ids = [item.get("capability_id") for item in capabilities if isinstance(item, dict)]
    if len(ids) != 34 or len(set(ids)) != 34:
        return "teacher", "capability ID가 고유하지 않습니다"
    for item in capabilities:
        if not isinstance(item, dict):
            return "teacher", "capability matrix 항목 형식이 올바르지 않습니다"
        state = item.get("support_state")
        if state not in {"native", "adapter-required", "unavailable"}:
            return "teacher", "알 수 없는 capability support state가 있습니다"
        if item.get("canonical_owner") != "hplan-core" or not item.get("fallback_artifact"):
            return "teacher", "capability ownership 또는 fallback artifact가 누락되었습니다"
        if state == "native" and (not item.get("entrypoint") or not item.get("smoke_fixture_id")):
            return "teacher", "native capability에 entrypoint 또는 smoke fixture가 없습니다"
        if state != "native" and (item.get("entrypoint") is not None or item.get("smoke_fixture_id") is not None):
            return "teacher", "non-native capability에 실행 entrypoint를 선언할 수 없습니다"

    rules = matrix.get("rules")
    rule_ids = {item.get("rule_id") for item in rules if isinstance(item, dict)} if isinstance(rules, list) else set()
    if not isinstance(rules, list) or len(rules) != 9 or rule_ids != EXPECTED_RULE_IDS:
        return "teacher", "9개 Behavioral Rule이 core 계약과 일치하지 않습니다"
    aliases = matrix.get("aliases")
    alias_map = {item.get("alias_id"): item.get("target") for item in aliases if isinstance(item, dict)} if isinstance(aliases, list) else {}
    if not isinstance(aliases, list) or len(aliases) != 3 or alias_map != EXPECTED_ALIASES:
        return "teacher", "3개 compatibility alias가 core 계약과 일치하지 않습니다"

    try:
        markdown = paths["markdown"].read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return "teacher", f"Markdown capability matrix를 읽을 수 없습니다: {exc}"
    if f"Contract version: `{lock['contract_version']}`" not in markdown or "Target: `codex`" not in markdown:
        return "teacher", "Markdown capability matrix의 버전 또는 target이 JSON과 일치하지 않습니다"
    if any(f"| {capability_id} |" not in markdown for capability_id in ids):
        return "teacher", "Markdown capability matrix가 JSON capability 목록을 반영하지 않습니다"
    if any(f"| {alias_id} | {target} |" not in markdown for alias_id, target in EXPECTED_ALIASES.items()):
        return "teacher", "Markdown capability matrix가 compatibility alias를 반영하지 않습니다"
    return None, None


def main() -> None:
    root = parse_args().root.resolve()
    codex_ok, version = codex_version()
    problem_state, problem = snapshot_problem(root)
    if problem_state == "recovery":
        backup_state, backup_problem = snapshot_problem(root, root / BACKUP_DIR)
        if backup_state is not None:
            problem_state = "teacher"
            problem = f"로컬 복구 백업을 신뢰할 수 없습니다: {backup_problem}"
    skills_problem = first_success_skills_problem()

    print("hplan_codex doctor (read-only)")
    print(f"Python: 정상 ({sys.version.split()[0]})")
    if codex_ok:
        print(f"Codex CLI: 정상 ({version})")
    else:
        print(f"Codex CLI: 자동 복구 가능 ({version})")

    if problem_state is None:
        print("hplan-core 스냅샷: 정상 (34 capabilities, 9 rules, 3 aliases)")
    elif problem_state == "recovery":
        print(f"hplan-core 스냅샷: 자동 복구 가능 ({problem})")
    else:
        print(f"hplan-core 스냅샷: 강사 호출 ({problem})")
    if skills_problem is None:
        print("First-success skills: 정상 (brainstorm, socratic-question, evidence-rubric)")
    else:
        print(f"First-success skills: 자동 복구 가능 ({skills_problem})")

    if problem_state == "teacher":
        print("상태: 강사 호출")
        print("다음 행동: 설치 원본의 core snapshot을 확인하고, mismatch 내용을 유지한 채 지원 담당자에게 전달하세요.")
        raise SystemExit(2)
    if not codex_ok or problem_state == "recovery" or skills_problem is not None:
        print("상태: 자동 복구 가능")
        actions = []
        if not codex_ok:
            actions.append("`npm install -g @openai/codex`")
        if skills_problem is not None:
            actions.append("Codex session에서 `$skill-installer https://github.com/kimsanguine/hplan_codex` 실행")
        if problem_state == "recovery":
            actions.append("`python3 scripts/repair_hplan_core_snapshot.py --root .`")
        print("다음 행동: " + " 후 ".join(actions) + " 후 `python3 scripts/hplan_doctor.py`를 다시 실행하세요.")
        raise SystemExit(1)

    print("상태: 정상")
    print('다음 행동: `$brainstorm "아이디어"`로 첫 WHETHER 판단을 기록하세요.')


if __name__ == "__main__":
    main()
