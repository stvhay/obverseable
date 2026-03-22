"""Tests for AccessibilityActor and SimulatorActor."""

from geckordp.actors.accessibility.accessibility import AccessibilityActor
from geckordp.actors.accessibility.simulator import SimulatorActor


class TestAccessibilityActor:
    def test_get_traits(self, client, target):
        a11y = AccessibilityActor(client, target["accessibilityActor"])
        traits = a11y.get_traits()
        assert traits is not None
        assert isinstance(traits, dict)

    def test_bootstrap(self, client, target):
        a11y = AccessibilityActor(client, target["accessibilityActor"])
        result = a11y.bootstrap()
        assert result is not None
        assert "enabled" in result

    def test_get_walker(self, client, target):
        a11y = AccessibilityActor(client, target["accessibilityActor"])
        result = a11y.get_walker()
        assert "actor" in result

    def test_get_simulator(self, client, target):
        a11y = AccessibilityActor(client, target["accessibilityActor"])
        result = a11y.get_simulator()
        assert "actor" in result


class TestSimulatorActor:
    def test_simulate_none(self, client, target):
        a11y = AccessibilityActor(client, target["accessibilityActor"])
        sim_resp = a11y.get_simulator()
        simulator = SimulatorActor(client, sim_resp["actor"])

        result = simulator.simulate(SimulatorActor.Types.NONE)
        assert result is not None

    def test_simulate_protanopia(self, client, target):
        a11y = AccessibilityActor(client, target["accessibilityActor"])
        sim_resp = a11y.get_simulator()
        simulator = SimulatorActor(client, sim_resp["actor"])

        result = simulator.simulate(SimulatorActor.Types.PROTANOPIA)
        assert result is not None

        # Reset
        simulator.simulate(SimulatorActor.Types.NONE)
