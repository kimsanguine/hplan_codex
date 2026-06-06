#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
TRACK_PROBE = REPO_ROOT / "scripts" / "track-probe.sh"


class TrackProbeTests(unittest.TestCase):
    def test_probe_writes_actual_log_for_write_file_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            track_dir = workdir / ".track"
            track_dir.mkdir()
            (track_dir / "current_task").write_text("P1-smoke\n", encoding="utf-8")
            payload = {
                "tool_name": "write_file",
                "tool_input": {
                    "file_path": "harness/PRD.md",
                    "content": "one\ntwo\n",
                },
            }

            result = subprocess.run(
                ["bash", str(TRACK_PROBE)],
                cwd=workdir,
                input=json.dumps(payload),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout)
            log_path = track_dir / "actual_log.jsonl"
            self.assertTrue(log_path.exists())
            entries = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["task"], "P1-smoke")
            self.assertEqual(entries[0]["event"], "tool_call")
            self.assertEqual(entries[0]["tool"], "write_file")
            self.assertEqual(entries[0]["file"], "harness/PRD.md")
            self.assertEqual(entries[0]["loc_delta"], 2)
            self.assertEqual(entries[0]["source"], "probe")


if __name__ == "__main__":
    unittest.main()
