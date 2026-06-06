#!/usr/bin/env python3
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = REPO_ROOT / "skills" / "stakeholder-update" / "SKILL.md"


class StakeholderUpdateSkillTests(unittest.TestCase):
    def test_confluence_export_and_notion_publish_are_separate_modes(self):
        content = SKILL.read_text(encoding="utf-8")

        self.assertIn("### mode: confluence-export", content)
        self.assertIn("### mode: notion-publish", content)
        self.assertNotIn("### mode: confluence-export (Notion publish)", content)
        self.assertIn("Confluence API를 직접 호출하지 않는다", content)
        self.assertIn("승인 게이트 전에는 Notion 페이지 생성 0", content)


if __name__ == "__main__":
    unittest.main()
