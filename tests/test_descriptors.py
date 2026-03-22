"""Tests for ProcessActor, WorkerActor, WebExtensionActor, AddonsActor."""

from geckordp.actors.addon.addons import AddonsActor
from geckordp.actors.descriptors.process import ProcessActor


class TestProcessActor:
    def test_get_target(self, client, root):
        processes = root.list_processes()
        parent = [p for p in processes if p.get("isParent")][0]
        proc = ProcessActor(client, parent["actor"])
        target = proc.get_target()
        assert target is not None


class TestAddonsActor:
    def test_addons_actor_accessible(self, client, root):
        root_info = root.get_root()
        assert "addonsActor" in root_info
        addons = AddonsActor(client, root_info["addonsActor"])
        assert addons.actor_id
