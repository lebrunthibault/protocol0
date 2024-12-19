from dataclasses import field, dataclass
from typing import List, Dict

from protocol0.domain.lom.track.ControlledTracksEnum import ControlledTracksEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.shared.Song import Song, find_track_or_none, find_track


@dataclass(frozen=True)
class ControlledTracks:
    enum: ControlledTracksEnum
    is_top_track: bool = True
    track_names: List[str] = field(default_factory=lambda: [])
    skip_group_track: bool = False

    def __repr__(self) -> str:
        return self.enum.name

    @property
    def _bus_name(self) -> str:
        return self.enum.value.title()

    @property
    def _main_track(self) -> SimpleTrack:
        return find_track(self._bus_name, exact=False, is_top=self.is_top_track)

    @property
    def _tracks(self) -> List[SimpleTrack]:
        track_names = self.track_names or [self._bus_name]
        return list(
            filter(
                None,
                [
                    find_track_or_none(name, exact=False, is_top=self.is_top_track)
                    for name in track_names
                ],
            )
        )

    @property
    def has_tracks(self) -> bool:
        return bool(self._tracks)

    @property
    def muted(self) -> bool:
        return any(t.muted for t in self._tracks)

    @property
    def soloed(self) -> bool:
        return any(t.solo for t in self._tracks)

    def toggle(self) -> None:
        for track in self._tracks:
            track.toggle()

    def solo_toggle(self) -> None:
        for track in self._tracks:
            track.solo_toggle()

    def select(self) -> SimpleTrack:
        tracks = [] if self.skip_group_track else [self._main_track]
        tracks += self._main_track.sub_tracks

        track_to_select: SimpleTrack = ValueScroller.scroll_values(
            tracks, Song.selected_track(), True
        )
        track_to_select.select()

        return track_to_select

    def set_volume(self, value: float) -> None:
        self._main_track.devices.mixer_device.volume.value = value


ControlledTracksRegistry: Dict[ControlledTracksEnum, ControlledTracks] = {
    ControlledTracksEnum.DRUMS: ControlledTracks(ControlledTracksEnum.DRUMS),
    ControlledTracksEnum.KICK: ControlledTracks(
        ControlledTracksEnum.KICK, is_top_track=False, skip_group_track=True
    ),
    ControlledTracksEnum.HAT: ControlledTracks(
        ControlledTracksEnum.HAT, is_top_track=False, skip_group_track=True
    ),
    ControlledTracksEnum.PERC: ControlledTracks(
        ControlledTracksEnum.PERC,
        is_top_track=False,
        track_names=["Perc", "FX"],
        skip_group_track=True,
    ),
    ControlledTracksEnum.FX: ControlledTracks(
        ControlledTracksEnum.FX,
        is_top_track=False,
        skip_group_track=True,
    ),
    ControlledTracksEnum.VOCALS: ControlledTracks(ControlledTracksEnum.VOCALS),
    ControlledTracksEnum.HARMONY: ControlledTracks(ControlledTracksEnum.HARMONY),
    ControlledTracksEnum.MELODY: ControlledTracks(ControlledTracksEnum.MELODY),
    ControlledTracksEnum.BASS: ControlledTracks(ControlledTracksEnum.BASS, skip_group_track=True),
    ControlledTracksEnum.SUB: ControlledTracks(ControlledTracksEnum.SUB, is_top_track=False),
}
