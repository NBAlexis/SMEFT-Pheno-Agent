from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillDebugContractTests(unittest.TestCase):
    def test_debug_mode_is_a_reduced_complete_workflow(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("debug-mode workflow tests", skill)
        self.assertIn("| `nev_scan` | 1000000 | 100000 |", skill)
        self.assertIn("do not add full-size runs", skill)
        self.assertIn("publication-ready only for `debug=false`", skill)
        self.assertNotIn(
            "This skill is for serious scientific research, not quick demonstration runs.",
            skill,
        )
        self.assertNotIn("debug=true` enables extra diagnostics only", skill)

    def test_debug_manuscript_is_labeled_without_removing_deliverables(self):
        phase10 = (ROOT / "reference" / "phase10-manuscript.md").read_text(
            encoding="utf-8"
        )
        deliverables = (ROOT / "reference" / "deliverables-phase10.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("still produce every Phase 10 artifact", phase10)
        self.assertIn("reduced-event workflow test", phase10)
        self.assertIn("all other Phase 10 files and sections remain required", deliverables)

    def test_ui_prompt_preserves_literal_skill_name(self):
        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$automated-smeft-ml-pheno", metadata)


if __name__ == "__main__":
    unittest.main()
