"""View focus actions (session / arrangement / detail views, browser)."""
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.shared.ApplicationView import ApplicationView


class ViewPlugin(PluginInterface):
    name = "view"

    @action
    def show_session(self) -> None:
        """Show the session view."""
        ApplicationView.show_session()

    @action
    def show_arrangement(self) -> None:
        """Show the arrangement view (and resume arrangement playback)."""
        ApplicationView.show_arrangement()

    @action
    def show_clip(self) -> None:
        """Show the clip detail view."""
        ApplicationView.show_clip()

    @action
    def show_device(self) -> None:
        """Show the device chain of the selected track."""
        ApplicationView.show_device()
        ApplicationView.focus_device()

    @action
    def toggle_browser(self) -> None:
        """Toggle the browser (hotswap) for the selected device."""
        ApplicationView.toggle_browse()
