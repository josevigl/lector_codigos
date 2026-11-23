import unittest
from unittest.mock import call, patch

from system import browser_action


class BrowserActionTests(unittest.TestCase):
    @patch("system.browser_action.time.sleep")
    @patch("system.browser_action._press_control_key")
    @patch("system.browser_action.click_at")
    def test_clicks_code_field_then_pastes_then_clicks_continue(
        self, click_at, press_control_key, sleep
    ):
        browser_action.paste_and_continue((10, 20), (30, 40), page_wait_ms=125)

        self.assertEqual(click_at.call_args_list, [call((10, 20)), call((30, 40))])
        self.assertEqual(
            press_control_key.call_args_list,
            [call(browser_action._VK_A), call(browser_action._VK_V)],
        )
        sleep.assert_called_once_with(0.125)

    def test_rejects_negative_page_wait(self):
        with self.assertRaises(ValueError):
            browser_action.paste_and_continue((10, 20), (30, 40), page_wait_ms=-1)


if __name__ == "__main__":
    unittest.main()
