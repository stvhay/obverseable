"""Tests for PreferenceActor and DeviceActor — root-level actors."""

from geckordp.actors.device import DeviceActor
from geckordp.actors.preference import PreferenceActor


class TestPreferenceActor:
    def _get_pref(self, client, root):
        root_info = root.get_root()
        return PreferenceActor(client, root_info["preferenceActor"])

    def test_get_bool_pref(self, client, root):
        pref = self._get_pref(client, root)
        result = pref.get_bool_pref("devtools.debugger.remote-enabled")
        # Returns dict with 'value' key or the value directly
        if isinstance(result, dict):
            assert result.get("value") is True
        else:
            assert result is True

    def test_get_char_pref(self, client, root):
        pref = self._get_pref(client, root)
        # Use a pref that is likely to exist
        result = pref.get_char_pref("intl.accept_languages")
        assert result is not None

    def test_get_int_pref(self, client, root):
        pref = self._get_pref(client, root)
        result = pref.get_int_pref("network.http.max-connections")
        # Returns dict with 'value' key or the value directly
        if isinstance(result, dict):
            assert isinstance(result.get("value"), int)
        else:
            assert isinstance(result, int)


class TestDeviceActor:
    def test_get_description(self, client, root):
        root_info = root.get_root()
        device = DeviceActor(client, root_info["deviceActor"])
        desc = device.get_description()
        assert desc is not None
        assert isinstance(desc, dict)
        # Should have browser info
        has_useful_keys = any(
            k in desc
            for k in [
                "apptype",
                "platformversion",
                "useragent",
                "name",
                "brandName",
            ]
        )
        assert has_useful_keys, f"Unexpected keys: {list(desc.keys())}"
