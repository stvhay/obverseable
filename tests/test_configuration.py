"""Tests for TargetConfigurationActor and ThreadConfigurationActor."""

from geckordp.actors.target_configuration import TargetConfigurationActor
from geckordp.actors.thread_configuration import ThreadConfigurationActor
from geckordp.actors.watcher import WatcherActor


class TestTargetConfigurationActor:
    def _get_config(self, client, tab_actor):
        watcher_resp = tab_actor.get_watcher()
        watcher = WatcherActor(client, watcher_resp["actor"])
        config_resp = watcher.get_target_configuration_actor()
        if config_resp and "actor" in config_resp:
            return TargetConfigurationActor(client, config_resp["actor"])
        return None

    def test_get_target_configuration_actor(self, client, tab_actor):
        config = self._get_config(client, tab_actor)
        # May not be available on all Firefox versions
        if config is not None:
            assert config.actor_id

    def test_update_configuration_cache(self, client, tab_actor):
        config = self._get_config(client, tab_actor)
        if config is None:
            return
        result = config.update_configuration(cache_disabled=True)
        assert result is not None
        # Reset
        config.update_configuration(cache_disabled=False)


class TestThreadConfigurationActor:
    def _get_config(self, client, tab_actor):
        watcher_resp = tab_actor.get_watcher()
        watcher = WatcherActor(client, watcher_resp["actor"])
        config_resp = watcher.get_thread_configuration_actor()
        if config_resp and "actor" in config_resp:
            return ThreadConfigurationActor(client, config_resp["actor"])
        return None

    def test_get_thread_configuration_actor(self, client, tab_actor):
        config = self._get_config(client, tab_actor)
        if config is not None:
            assert config.actor_id

    def test_update_configuration(self, client, tab_actor):
        config = self._get_config(client, tab_actor)
        if config is None:
            return
        result = config.update_configuration(skip_breakpoints=True)
        assert result is not None
        # Reset
        config.update_configuration(skip_breakpoints=False)
