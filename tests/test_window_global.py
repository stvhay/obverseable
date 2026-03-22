"""Tests for WindowGlobalActor — tab/window control."""

from geckordp.actors.targets.window_global import WindowGlobalActor


class TestWindowGlobalActor:
    def _get_window(self, client, target):
        return WindowGlobalActor(client, target["actor"])

    def test_list_frames(self, client, target):
        window = self._get_window(client, target)
        frames = window.list_frames()
        assert isinstance(frames, list)
        assert len(frames) > 0
        # Top-level frame
        top_frames = [f for f in frames if f.get("isTopLevel")]
        assert len(top_frames) > 0

    def test_list_workers(self, client, target):
        window = self._get_window(client, target)
        result = window.list_workers()
        assert result is not None
        assert "workers" in result

    def test_focus(self, client, target):
        window = self._get_window(client, target)
        result = window.focus()
        assert result is not None
