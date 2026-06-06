#!/usr/bin/env python3
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = REPO_ROOT / "schemas"


class ArtifactSchemaTests(unittest.TestCase):
    def test_key_artifact_schemas_exist_and_are_json_schema_objects(self):
        expected = [
            "prd_section_map.schema.json",
            "qa_pool.schema.json",
            "qa_checklist.schema.json",
            "cogs_result.schema.json",
            "track_event_log.schema.json",
        ]

        for name in expected:
            with self.subTest(schema=name):
                data = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
                self.assertEqual(data.get("$schema"), "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(data.get("type"), "object")
                self.assertIn("required", data)
                self.assertIn("properties", data)

    def test_track_event_schema_requires_probe_log_fields(self):
        data = json.loads((SCHEMAS / "track_event_log.schema.json").read_text(encoding="utf-8"))

        for field in ["ts", "task", "event", "tool", "file", "loc_delta", "source"]:
            self.assertIn(field, data["required"])

        self.assertIn("tool_call", data["properties"]["event"]["enum"])
        self.assertIn("probe", data["properties"]["source"]["enum"])


if __name__ == "__main__":
    unittest.main()
