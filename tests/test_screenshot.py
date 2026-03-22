"""Tests for ScreenshotActor — capture from root actor."""

import base64

from geckordp.actors.screenshot import ScreenshotActor


class TestScreenshotFromRoot:
    def test_capture(self, client, root):
        root_info = root.get_root()
        assert "screenshotActor" in root_info

        tabs = root.list_tabs()
        screenshot = ScreenshotActor(client, root_info["screenshotActor"])
        result = screenshot.capture(tabs[0]["browsingContextID"])

        assert result is not None
        assert "value" in result
        assert "data" in result["value"]
        assert result["value"]["data"].startswith("data:image/png;base64,")

    def test_capture_decodes_to_valid_png(self, client, root):
        root_info = root.get_root()
        tabs = root.list_tabs()
        screenshot = ScreenshotActor(client, root_info["screenshotActor"])
        result = screenshot.capture(tabs[0]["browsingContextID"])

        data_uri = result["value"]["data"]
        b64_data = data_uri.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_data)

        # PNG magic bytes
        assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(img_bytes) > 1000  # Should be a real image


class TestScreenshotFromTargetFails:
    """Verify that screenshotContentActor from target does NOT work on Firefox 140+."""

    def test_target_screenshot_actor_unrecognized(self, client, target):
        screenshot = ScreenshotActor(client, target["screenshotContentActor"])
        # This should either return an error or None (timeout)
        result = screenshot.capture(24)  # dummy browsing context
        if result is not None:
            assert "error" in result
