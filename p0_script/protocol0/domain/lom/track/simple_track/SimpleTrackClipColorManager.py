from typing import TYPE_CHECKING

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrackClips import SimpleTrackClips


class SimpleTrackClipColorManager(object):
    def __init__(
        self, clips: "SimpleTrackClips", track_devices: SimpleTrackDevices, track_color: int
    ) -> None:
        self._clips = clips
        self._track_devices = track_devices
        self._track_color = track_color

    def toggle_colors(self) -> None:
        colors_on = any(c.color != self._track_color for c in list(self._clips))

        if colors_on:
            self._revert_coloring()
        else:
            self._set_colors()

    def _revert_coloring(self) -> None:
        for clip in self._clips:
            clip.color = self._track_color

    def _set_colors(self) -> None:
        color_index = 0

        clip_infos = ClipInfo.create_from_clips(list(self._clips), self._track_devices.parameters)

        for clip_info in clip_infos:
            clips = clip_info.get_clips(list(self._clips))

            if color_index == self._track_color:
                color_index += 1

            for clip in clips:
                clip.color = color_index

            color_index += 1
