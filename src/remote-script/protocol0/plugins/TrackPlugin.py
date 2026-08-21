"""Track actions over the addressing grammar.

Every action targets a track through a spec string (`track` param, default SEL):
SEL | MST/master | 1-based index | "name" (exact) | bare name (exact then
substring) | < / > relative to the selection. Boolean values take ON / OFF /
TGL; volume takes dB, pan takes -1..1 or x% / < / > / RND.
"""
from typing import Optional

from protocol0.application.http.HttpServer import get_container
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.addressing.scene import resolve_scene
from protocol0.domain.lom.addressing.track import resolve_track
from protocol0.domain.lom.addressing.values import (
    resolve_adjustable,
    resolve_bool,
    resolve_continuous,
    resolve_quasi_continuous,
)
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.sequence.Sequence import Sequence

_MONITORING_STATES = ["in", "auto", "off"]


class TrackPlugin(PluginInterface):
    name = "track"

    @action
    def select(self, track: str = "SEL") -> None:
        """Select a track (track: SEL, MST/master, index, "name", name, < / >)."""
        resolve_track(track).select()

    @action
    def arm(self, track: str = "SEL", value: str = "TGL") -> None:
        """Arm a track for recording (value: ON, OFF or TGL)."""
        arm_state = resolve_track(track).arm_state
        arm_state.is_armed = resolve_bool(value, arm_state.is_armed)

    @action
    def mute(self, track: str = "SEL", value: str = "TGL") -> None:
        """Mute a track (value: ON, OFF or TGL)."""
        target = resolve_track(track)
        target.muted = resolve_bool(value, target.muted)

    @action
    def solo(self, track: str = "SEL", value: str = "TGL") -> None:
        """Solo a track (value: ON, OFF or TGL)."""
        target = resolve_track(track)
        target.solo = resolve_bool(value, target.solo)

    @action
    def fold(self, track: str = "SEL", value: str = "TGL") -> None:
        """Fold or unfold a group track (value: ON, OFF or TGL)."""
        target = resolve_track(track)
        if not target.is_foldable:
            raise Protocol0Warning("'%s' is not a group track" % target.name)
        target.is_folded = resolve_bool(value, target.is_folded)

    @action
    def monitor(self, track: str = "SEL", value: str = ">") -> None:
        """Set the monitoring state (value: in, auto, off, or < / > cycling)."""
        target = resolve_track(track)
        current = target.current_monitoring_state.name.lower()
        state = resolve_adjustable(value, _MONITORING_STATES, current)
        target.current_monitoring_state = CurrentMonitoringStateEnum[state.upper()]

    @action
    def rename(self, name: str, track: str = "SEL") -> None:
        """Rename a track."""
        resolve_track(track).appearance.name = name

    @action
    def color(self, value: str, track: str = "SEL") -> None:
        """Set a track's color (value: Live color index 0-69)."""
        resolve_track(track).color = int(resolve_continuous(value, 0, 0, 69))

    @action
    def volume(self, value: str, track: str = "SEL") -> None:
        """Set a track's volume in dB (value: like "-6", or < / > dB steps)."""
        target = resolve_track(track)
        target.volume = resolve_quasi_continuous(value, target.volume, -70.0, 6.0)

    @action
    def pan(self, value: str, track: str = "SEL") -> None:
        """Set a track's panning (value: -1..1, x%, < / > steps, RND or RESET)."""
        target = resolve_track(track)
        target.pan = resolve_continuous(value, target.pan, -1.0, 1.0, default=0.0)

    @action
    def send(self, send: str, value: str, track: str = "SEL") -> None:
        """Set a track send (send: 1-based index or name; value: 0..1, x%, < / >)."""
        target = resolve_track(track)
        sends = target.devices.mixer_device.sends
        if not sends:
            raise Protocol0Warning("'%s' has no sends" % target.name)
        if send.strip().isdigit():
            index = int(send)
            if not 1 <= index <= len(sends):
                raise Protocol0Warning(
                    "no send %s on '%s' (%d sends)" % (send, target.name, len(sends))
                )
            parameter = sends[index - 1]
        else:
            matches = [s for s in sends if send.strip().lower() in s.name.lower()]
            if not matches:
                raise Protocol0Warning(
                    "no send matching '%s' on '%s' (sends: %s)"
                    % (send, target.name, ", ".join(s.name for s in sends))
                )
            parameter = matches[0]
        parameter.value = resolve_continuous(value, parameter.value, 0.0, 1.0, default=0.0)

    @action
    def fire(self, track: str = "SEL", scene: str = "SEL") -> None:
        """Fire a track's clip in the given scene (scene: SEL, index, name)."""
        resolve_track(track).fire(resolve_scene(scene).index)

    @action
    def stop(self, track: str = "SEL") -> None:
        """Stop every playing clip of a track."""
        resolve_track(track).stop()

    @action
    def create_midi(self, index: str = "") -> Sequence:
        """Create a MIDI track (index: 1-based position, empty = at the end)."""
        position = int(index) - 1 if index.strip().isdigit() else None
        return get_container().get(TrackCrudComponent).create_midi_track(position)

    @action
    def create_audio(self, index: str = "") -> Sequence:
        """Create an audio track (index: 1-based position, empty = at the end)."""
        position = int(index) - 1 if index.strip().isdigit() else None
        return get_container().get(TrackCrudComponent).create_audio_track(position)

    @action
    def duplicate(self, track: str = "SEL") -> Sequence:
        """Duplicate a track."""
        return get_container().get(TrackCrudComponent).duplicate_track(resolve_track(track))

    @action
    def delete(self, track: str = "SEL") -> Optional[Sequence]:
        """Delete a track."""
        return get_container().get(TrackCrudComponent).delete_track(resolve_track(track).index)
