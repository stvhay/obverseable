"""Tests for RootActor — tab listing, processes, workers, addons."""


class TestListTabs:
    def test_returns_list(self, root):
        tabs = root.list_tabs()
        assert isinstance(tabs, list)
        assert len(tabs) > 0

    def test_tab_has_required_fields(self, root):
        tabs = root.list_tabs()
        tab = tabs[0]
        assert "actor" in tab
        assert "title" in tab
        assert "url" in tab
        assert "browserId" in tab
        assert "browsingContextID" in tab
        assert "selected" in tab

    def test_current_tab(self, root):
        current = root.current_tab()
        assert current is not None
        assert current["selected"] is True
        assert "title" in current


class TestListProcesses:
    def test_returns_list(self, root):
        processes = root.list_processes()
        assert isinstance(processes, list)
        assert len(processes) > 0

    def test_has_parent_process(self, root):
        processes = root.list_processes()
        parents = [p for p in processes if p.get("isParent")]
        assert len(parents) == 1

    def test_get_process(self, root):
        result = root.get_process(0)
        assert result is not None
        assert "processDescriptor" in result


class TestListWorkers:
    def test_returns_list(self, root):
        workers = root.list_workers()
        assert isinstance(workers, list)


class TestListAddons:
    def test_returns_list(self, root):
        addons = root.list_addons()
        assert isinstance(addons, list)


class TestServiceWorkers:
    def test_returns_list(self, root):
        registrations = root.list_service_worker_registrations()
        assert isinstance(registrations, list)


class TestRequestTypes:
    def test_returns_list(self, root):
        types = root.request_types()
        assert isinstance(types, list)
        assert "listTabs" in types
        assert "getRoot" in types


class TestGetRoot:
    def test_returns_actor_ids(self, root):
        info = root.get_root()
        assert "preferenceActor" in info
        assert "deviceActor" in info
        assert "screenshotActor" in info
