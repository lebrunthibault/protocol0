from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.plugins.ViewPlugin import ViewPlugin


def _plugin(p0) -> ViewPlugin:
    return PluginLoader.get(ViewPlugin)


def test_show_arrangement(p0):
    _plugin(p0).show_arrangement()
    ApplicationView._INSTANCE._application_view.show_view.assert_any_call("Arranger")
    assert p0.song().back_to_arranger is False


def test_show_session(p0):
    _plugin(p0).show_session()
    ApplicationView._INSTANCE._application_view.show_view.assert_any_call("Session")


def test_toggle_browser(p0):
    _plugin(p0).toggle_browser()
    assert ApplicationView._INSTANCE._application_view.toggle_browse.called
