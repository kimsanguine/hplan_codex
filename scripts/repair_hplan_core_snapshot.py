#!/usr/bin/env python3
"""Restore the hplan-core snapshot from the local installer backup.

This is an explicit user-run local write operation. Unlike hplan_doctor.py,
it intentionally replaces only the four core snapshot artifacts.
"""

import argparse
import os
import tempfile
from pathlib import Path

from hplan_doctor import BACKUP_DIR, snapshot_problem


ARTIFACTS = (
    Path("hplan-core.lock"),
    Path("docs/hplan-capability-matrix.json"),
    Path("docs/HPLAN_CAPABILITY_MATRIX.md"),
    Path("docs/hplan-core-adapter.json"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore hplan-core snapshot from the local setup backup")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Installed hplan_codex project directory (default: parent of this script)",
    )
    return parser.parse_args()


def stage_bytes(target: Path, payload: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    with os.fdopen(descriptor, "wb") as temporary:
        temporary.write(payload)
        temporary.flush()
        os.fsync(temporary.fileno())
    return Path(temporary_name)


def remove_staged(paths: list[Path]) -> None:
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def rollback(targets: list[Path], originals: dict[Path, bytes | None]) -> list[str]:
    errors = []
    for target in reversed(targets):
        try:
            original = originals[target]
            if original is None:
                target.unlink(missing_ok=True)
            else:
                temporary = stage_bytes(target, original)
                try:
                    os.replace(temporary, target)
                except OSError:
                    temporary.unlink(missing_ok=True)
                    raise
        except OSError as exc:
            errors.append(f"{target}: {exc}")
    return errors


def restore(root: Path) -> tuple[bool, str]:
    root = root.resolve()
    backup_root = root / BACKUP_DIR
    backup_state, backup_problem = snapshot_problem(root, backup_root)
    if backup_state is not None:
        return False, f"로컬 복구 백업을 신뢰할 수 없습니다: {backup_problem}"
    source_paths = [backup_root / artifact for artifact in ARTIFACTS]
    try:
        payloads = [(artifact, source.read_bytes()) for artifact, source in zip(ARTIFACTS, source_paths)]
        targets = [root / artifact for artifact, _ in payloads]
        originals = {target: target.read_bytes() if target.is_file() else None for target in targets}
    except OSError as exc:
        return False, f"로컬 snapshot 복구 준비에 실패했습니다: {exc}"

    staged = []
    try:
        for target, (_, payload) in zip(targets, payloads):
            staged.append(stage_bytes(target, payload))
    except OSError as exc:
        remove_staged(staged)
        return False, f"로컬 snapshot 복구 staging에 실패했습니다: {exc}; live artifact는 변경하지 않았습니다."

    replaced = []
    try:
        for target, temporary in zip(targets, staged):
            os.replace(temporary, target)
            replaced.append(target)
    except OSError as exc:
        rollback_errors = rollback(replaced, originals)
        remove_staged(staged)
        if rollback_errors:
            return False, (
                f"로컬 snapshot 복구에 실패했고 이전 상태 복원도 실패했습니다: {exc}; "
                f"rollback 오류: {'; '.join(rollback_errors)}. 강사 호출이 필요합니다."
            )
        return False, f"로컬 snapshot 복구에 실패했습니다: {exc}; 이전 상태로 모두 복원했습니다."
    remove_staged(staged)
    return True, "hplan-core snapshot 4개 artifact를 로컬 백업에서 복구했습니다."


def main() -> None:
    success, message = restore(parse_args().root)
    if not success:
        print(f"복구 실패: {message}")
        raise SystemExit(1)
    print(message)
    print("다음 행동: `python3 scripts/hplan_doctor.py`로 복구 결과를 확인하세요.")


if __name__ == "__main__":
    main()
