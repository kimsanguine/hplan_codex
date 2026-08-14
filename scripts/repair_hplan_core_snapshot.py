#!/usr/bin/env python3
"""Restore the hplan-core snapshot from the local installer backup.

This is an explicit user-run local write operation. Unlike hplan_doctor.py,
it intentionally replaces only the four core snapshot artifacts.
"""

import argparse
import os
import tempfile
from pathlib import Path


ARTIFACTS = (
    Path("hplan-core.lock"),
    Path("docs/hplan-capability-matrix.json"),
    Path("docs/HPLAN_CAPABILITY_MATRIX.md"),
    Path("docs/hplan-core-adapter.json"),
)
BACKUP_DIR = ".hplan-core-snapshot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore hplan-core snapshot from the local setup backup")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Installed hplan_codex project directory (default: parent of this script)",
    )
    return parser.parse_args()


def restore(root: Path) -> tuple[bool, str]:
    root = root.resolve()
    backup_root = root / BACKUP_DIR
    source_paths = [backup_root / artifact for artifact in ARTIFACTS]
    missing = [str(path.relative_to(root)) for path in source_paths if not path.is_file()]
    if missing:
        return False, "로컬 복구 백업이 누락되었습니다: " + ", ".join(missing)
    try:
        payloads = [(artifact, source.read_bytes()) for artifact, source in zip(ARTIFACTS, source_paths)]
        for artifact, payload in payloads:
            target = root / artifact
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
            try:
                with os.fdopen(descriptor, "wb") as temporary:
                    temporary.write(payload)
                    temporary.flush()
                    os.fsync(temporary.fileno())
                os.replace(temporary_name, target)
            except OSError:
                Path(temporary_name).unlink(missing_ok=True)
                raise
    except OSError as exc:
        return False, f"로컬 snapshot 복구에 실패했습니다: {exc}"
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
