"""Tests for ThreadActor — debugger attach, sources, breakpoints, event breakpoints."""

from geckordp.actors.thread import ThreadActor


class TestThreadAttach:
    def test_attach_and_detach(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        # Attach
        result = thread.attach()
        assert result is not None
        assert thread.is_attached()

        # Detach by resuming (thread must be in running state)
        # Just verify attach worked

    def test_is_attached(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        assert thread.is_attached() is True


class TestSources:
    def test_list_sources(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        sources = thread.sources()
        assert isinstance(sources, list)
        # Should have at least some sources for the page
        assert len(sources) > 0

    def test_source_has_required_fields(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        sources = thread.sources()
        source = sources[0]
        assert "actor" in source
        assert "url" in source


class TestEventBreakpoints:
    def test_get_available_event_breakpoints(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        events = thread.get_available_event_breakpoints()
        assert isinstance(events, list)
        assert len(events) > 0

        # Should have categories
        categories = [e.get("name") for e in events]
        assert "Keyboard" in categories or "Mouse" in categories

    def test_get_active_event_breakpoints(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        active = thread.get_active_event_breakpoints()
        assert isinstance(active, list)

    def test_set_active_event_breakpoints(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()

        # Set and then clear
        result = thread.set_active_event_breakpoints(["event.mouse.click"])
        assert result is not None

        # Verify it's set
        active = thread.get_active_event_breakpoints()
        assert "event.mouse.click" in active

        # Clear
        thread.set_active_event_breakpoints([])
        active = thread.get_active_event_breakpoints()
        assert len(active) == 0


class TestDumpThread:
    def test_dump_thread(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        dump = thread.dump_thread()
        assert dump is not None
        assert "pauseOnExceptions" in dump
        assert "breakpoints" in dump


class TestPauseConfig:
    def test_pause_on_exceptions(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        result = thread.pause_on_exceptions(True, True)
        assert result is not None

        # Reset
        thread.pause_on_exceptions(False, True)

    def test_reconfigure(self, client, target):
        thread = ThreadActor(client, target["threadActor"])
        thread.attach()
        result = thread.reconfigure()
        assert result is not None
