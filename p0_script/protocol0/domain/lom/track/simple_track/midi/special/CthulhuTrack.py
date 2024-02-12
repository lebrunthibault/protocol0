import Live
from typing import Optional
from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackService import rename_tracks
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.Song import Song


def _get_cthulhu_track(track: SimpleTrack) -> "CthulhuTrack":
    if isinstance(track.input_routing.track, CthulhuTrack):
        return track.input_routing.track
    else:
        try:
            cthulhu_track = list(Song.simple_tracks())[track.index - 1]
        except IndexError:
            cthulhu_track = None

        assert isinstance(cthulhu_track, CthulhuTrack), "Could not find Cthulhu track"

    return cthulhu_track


def toggle_cthulhu_routing(track: SimpleTrack, force_cthulhu_routing: bool = False) -> None:
    cthulhu_track = _get_cthulhu_track(track)

    if track.input_routing.type == InputRoutingTypeEnum.ALL_INS or force_cthulhu_routing:
        # listen to Cthulhu
        track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        track.input_routing.track = cthulhu_track
        track.input_routing.channel = InputRoutingChannelEnum.CTHULHU
    else:
        # listen to synth track
        track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        track.input_routing.type = InputRoutingTypeEnum.ALL_INS


class CthulhuTrack(SimpleMidiTrack):
    @classmethod
    def is_track_valid(cls, track: Live.Track.Track) -> bool:
        devices = list(track.devices)
        return len(devices) > 0 and any(d.name == DeviceEnum.CTHULHU.value for d in devices)

    @subject_slot("solo")
    @defer
    def _solo_listener(self) -> None:
        """Handle Cthulhu tracks"""
        if not self.solo:
            return

        synth_track: Optional[SimpleAudioTrack] = next(
            filter(lambda t: t.input_routing.track == self, Song.simple_tracks()), None  # type: ignore[arg-type]
        )
        if synth_track:
            synth_track.solo = True
        if Song.notes_track():
            Song.notes_track().solo = True

    def on_added(self) -> None:
        rename_tracks(list(Song.top_tracks()), self.name)
        assert Song.notes_track(), "No 'Notes' track"

        self.input_routing.track = Song.notes_track()  # type: ignore[assignment]
        self.select()

        if not self.synth_track:
            return

        rename_tracks(list(Song.top_tracks()), self.synth_track.name)

        def get_bus_track(name: str) -> Optional[SimpleAudioTrack]:
            track = find_if(
                lambda t: t.name.lower().strip() == name.lower().strip(), Song.simple_tracks()
            )
            if track:
                assert (
                    track.current_monitoring_state == CurrentMonitoringStateEnum.IN
                ), f"bus track {track} has not monitor IN"

            return track

        bus_track = get_bus_track(f"{self.synth_track.name} Bus")
        assert bus_track, f"Could not find bus track for {self.synth_track}"

        self.synth_track.output_routing.track = bus_track

    @property
    def synth_track(self) -> Optional[SimpleAudioTrack]:
        try:
            return list(Song.simple_tracks())[self.index + 1]
        except IndexError:
            return None
