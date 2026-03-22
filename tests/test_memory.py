"""Tests for MemoryActor — measure, census, allocations."""

from geckordp.actors.memory import MemoryActor


class TestMemoryActor:
    def _get_memory(self, client, target):
        mem = MemoryActor(client, target["memoryActor"])
        mem.attach()
        return mem

    def test_attach_detach(self, client, target):
        mem = MemoryActor(client, target["memoryActor"])
        result = mem.attach()
        assert result is not None

        result = mem.detach()
        assert result is not None

    def test_measure(self, client, target):
        mem = self._get_memory(client, target)
        result = mem.measure()
        assert result is not None

    def test_take_census(self, client, target):
        mem = self._get_memory(client, target)
        result = mem.take_census()
        assert result is not None

    def test_get_state(self, client, target):
        mem = self._get_memory(client, target)
        result = mem.get_state()
        assert result is not None

    def test_force_garbage_collection(self, client, target):
        mem = self._get_memory(client, target)
        result = mem.force_garbage_collection()
        assert result is not None

    def test_force_cycle_collection(self, client, target):
        mem = self._get_memory(client, target)
        result = mem.force_cycle_collection()
        assert result is not None
