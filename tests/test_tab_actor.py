"""Tests for TabActor — get_target, get_watcher, get_favicon."""


class TestGetTarget:
    def test_returns_all_actor_ids(self, target):
        expected_actors = [
            "consoleActor",
            "inspectorActor",
            "threadActor",
            "networkContentActor",
            "memoryActor",
            "accessibilityActor",
            "screenshotContentActor",
            "styleSheetsActor",
            "animationsActor",
            "changesActor",
            "tracerActor",
            "objectsManagerActor",
        ]
        for actor_key in expected_actors:
            assert actor_key in target, f"Missing {actor_key} in target"
            assert isinstance(target[actor_key], str)

    def test_target_has_page_info(self, target):
        assert "title" in target
        assert "url" in target
        assert "browsingContextID" in target

    def test_target_has_traits(self, target):
        assert "traits" in target
        assert isinstance(target["traits"], dict)


class TestGetWatcher:
    def test_returns_watcher_actor(self, tab_actor):
        watcher = tab_actor.get_watcher()
        assert "actor" in watcher
        assert isinstance(watcher["actor"], str)


class TestGetFavicon:
    def test_returns_result(self, tab_actor):
        # Favicon may be None for some pages, but call should not error
        result = tab_actor.get_favicon()
        # result may be: None, a string, or a dict with 'favicon' key
        if isinstance(result, dict):
            assert "favicon" in result
        else:
            assert result is None or isinstance(result, str)
