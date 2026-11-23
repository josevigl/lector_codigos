import tempfile
import unittest
from pathlib import Path

from select_actions import save_action_coordinates


class SelectActionsTests(unittest.TestCase):
    def test_saves_points_enables_automation_and_preserves_other_config(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "config.yaml"
            config_path.write_text(
                "capture:\n"
                "  fps: 60\n"
                "automation:\n"
                "  enabled: false\n"
                "  page_wait_ms: 400\n"
                "logging:\n"
                "  level: INFO\n",
                encoding="utf-8",
            )

            save_action_coordinates(config_path, (100, 200), (300, 400))

            saved = config_path.read_text(encoding="utf-8")
            self.assertIn("  enabled: true", saved)
            self.assertIn("  code_field: [100, 200]", saved)
            self.assertIn("  continue_button: [300, 400]", saved)
            self.assertIn("  page_wait_ms: 400", saved)
            self.assertIn("  fps: 60", saved)
            self.assertIn("  level: INFO", saved)


if __name__ == "__main__":
    unittest.main()
