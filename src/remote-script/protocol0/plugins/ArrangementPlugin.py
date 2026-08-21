"""Arrangement (timeline) actions.

Times are in beats from the arrangement start.
"""
from typing import Optional

from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.addressing.clip import resolve_clip
from protocol0.domain.lom.addressing.track import resolve_track
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ArrangementPlugin(PluginInterface):
    name = "arrangement"

    @action
    def duplicate_clip(self, time: float, track: str = "SEL", clip: str = "SEL") -> None:
        """Copy a session clip to the arrangement at the given time (in beats)."""
        target_track = resolve_track(track)
        target_track.duplicate_clip_to_arrangement(resolve_clip(track, clip), time)

    @action
    def clear(self, track: str = "SEL") -> None:
        """Delete every arrangement clip of a track."""
        resolve_track(track).clear_arrangement()

    @action
    def set_time(self, time: float) -> None:
        """Move the arrangement playhead to the given time (in beats)."""
        Song.set_current_song_time(time)

    @action
    def add_locator(self, time: float) -> Optional[Sequence]:
        """Add a locator (cue point) at the given time (no-op if one is already there)."""
        return Song.set_or_delete_cue(time)
