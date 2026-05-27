from protocol0.application.http.Router import route
from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.plugins.live_set.LiveSetPlugin import LiveSetPlugin


@route("GET", "/clip/key_detected")
def on_key_detected(pitch: int) -> None:
    """Notify the script that a musical key (MIDI pitch) was detected for the current clip."""
    PluginLoader.get(LiveSetPlugin).on_key_detected(pitch)
