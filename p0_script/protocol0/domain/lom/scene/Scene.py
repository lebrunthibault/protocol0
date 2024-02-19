import collections
from functools import partial
from typing import List, Optional, Dict, cast

import Live
from _Framework.SubjectSlot import SlotManager, subject_slot

from protocol0.domain.lom.scene.NextSceneStartedEvent import NextSceneStartedEvent
from protocol0.domain.lom.scene.SceneAppearance import SceneAppearance
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneCropScroller import SceneCropScroller
from protocol0.domain.lom.scene.SceneFiredEvent import SceneFiredEvent
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.lom.scene.ScenePositionScroller import ScenePositionScroller
from protocol0.domain.lom.set.AbletonSet import SceneTrackState, AbletonScene
from protocol0.domain.lom.song.components.TrackComponent import find_top_group_sub_tracks
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.TrackCategoryEnum import TrackCategoryEnum
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class Scene(SlotManager):
    LAST_MANUALLY_STARTED_SCENE: Optional["Scene"] = None

    def __init__(self, live_scene: Live.Scene.Scene, index: int) -> None:
        super(Scene, self).__init__()
        self._scene = live_scene
        self.index = index
        self.live_id: int = self._scene._live_ptr

        self.clips = SceneClips(self.index)
        self._scene_length = SceneLength(self.clips, self.index)
        self.playing_state = ScenePlayingState(self.clips, self._scene_length)
        self.scene_name = SceneName(live_scene, self._scene_length, self.playing_state)
        self.appearance = SceneAppearance(live_scene, self.scene_name)
        self.crop_scroller = SceneCropScroller(self._scene_length)
        self.position_scroller = ScenePositionScroller(self._scene_length, self.playing_state)

        # listeners
        self.clips.register_observer(self)
        self.is_triggered_listener.subject = self._scene

    def __repr__(self) -> str:
        return "Scene(%s (%s))" % (self.name, self.index)

    @property
    def abstract_tracks(self) -> List[AbstractTrack]:
        tracks: Dict[int, AbstractTrack] = collections.OrderedDict()
        for track in self.clips.tracks:
            tracks[track.abstract_track.index] = track.abstract_track

        return list(sorted(tracks.values(), key=lambda t: t.index))

    def update(self, observable: Observable) -> None:
        if isinstance(observable, SceneClips):
            self.appearance.refresh()

    def on_tracks_change(self) -> None:
        self.clips.build()

    def on_added(self) -> None:
        self.clips.on_added_scene()
        self.scene_name.update("")

    @property
    def next_scene(self) -> "Scene":
        if self.should_loop:
            return self
        else:
            next_scene = Song.scenes()[self.index + 1]
            if next_scene.skipped:
                return next_scene.next_scene
            else:
                return next_scene

    @property
    def should_loop(self) -> bool:
        return (
            self == Song.looping_scene()
            or self == Song.scenes()[-1]
            or Song.scenes()[self.index + 1].bar_length == 0
        )

    @property
    def previous_scene(self) -> "Scene":
        if self == Song.scenes()[0]:
            return self
        else:
            previous_scene = Song.scenes()[self.index - 1]
            if previous_scene.skipped:
                return previous_scene.previous_scene
            else:
                return previous_scene

    @property
    def is_triggered(self) -> bool:
        return bool(self._scene.is_triggered) if self._scene else False

    name = cast(str, ForwardTo("appearance", "name"))
    lower_name = cast(str, ForwardTo("appearance", "lower_name"))
    length = cast(float, ForwardTo("_scene_length", "length"))
    bar_length = cast(int, ForwardTo("_scene_length", "bar_length"))

    @property
    def skipped(self) -> bool:
        return self.lower_name.startswith("skip")

    def on_bar_end(self) -> None:
        if Song.is_track_recording():
            return

        if self.playing_state.in_last_bar:
            next_scene = self.next_scene

            if next_scene != self:
                next_scene.fire()  # do not fire same scene as it focus it again (can lose current parameter focus)

                seq = Sequence()
                seq.wait_for_event(BarChangedEvent)
                seq.add(
                    partial(
                        DomainEventBus.emit,
                        NextSceneStartedEvent(Song.selected_scene().index),
                    )
                )
                seq.done()

    @subject_slot("is_triggered")
    def is_triggered_listener(self) -> None:
        """
        This is called on scene trigger:
        - on click
        - and when the song stars playing

        We activate this only in the first case by checking PlayingScene
        This doesn't execute (duplicated) when the scene was fired from a command

        It is there to handle manual launches (direct click on scene)
        It could almost be removed as this case happens very rarely
        (I fire scenes almost always from keyboard shortcuts / commands)
        """
        if Song.is_playing() is False or not self.playing_state.is_playing:
            return
        if Song.playing_scene() == self:
            return

        DomainEventBus.emit(SceneFiredEvent(self.index))

    def fire(self) -> None:
        # stop the previous scene in advance, using clip launch quantization
        DomainEventBus.emit(SceneFiredEvent(self.index))

        if not Song.is_playing() and Song.mix_buses_track():
            Song.mix_buses_track().reset_bus_tracks_automation()
            for midi_note_track in Song.midi_note_tracks():
                midi_note_track.reset_midi_automation()

        if self._scene:
            self._scene.fire()

    def stop(self, next_scene: Optional["Scene"] = None, immediate: bool = False) -> None:
        """Used to manually stopping previous scene
        because we don't display clip slot stop buttons
        """
        next_scene_index = next_scene.index if next_scene is not None else None

        for track in Song.abstract_tracks():
            track.stop(
                scene_index=self.index, immediate=immediate, next_scene_index=next_scene_index
            )

        seq = Sequence()
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(self.scene_name.update)
        seq.done()

    # @throttle(duration=40)
    def fire_to_position(self, bar_length: int) -> Sequence:
        seq = Sequence()

        self.scene_name.update(bar_position=bar_length)

        seq.add(self.fire)
        seq.defer()
        seq.add(partial(self.position_scroller.set_value, bar_length))

        return seq.done()

    def scroll_tracks(self, go_next: bool) -> None:
        tracks = [track.get_view_track(self.index) for track in self.abstract_tracks]
        tracks = list(filter(None, tracks))
        tracks.sort(key=lambda t: t.index)
        next_track = ValueScroller.scroll_values(tracks, Song.selected_track(), go_next)
        next_track.select()

        ApplicationView.focus_session()

    def unfold(self) -> None:
        """Show only scene tracks"""
        for track in Song.abstract_tracks():
            if track.base_track.is_foldable:
                track.base_track.is_folded = True

        for track in self.abstract_tracks:
            if track.base_track.is_foldable:
                track.base_track.is_folded = False
            if track.group_track:
                track.base_track.group_track.is_folded = False

    def to_scene_state(self) -> AbletonScene:
        scene_state = AbletonScene()
        for group_enum in list(TrackCategoryEnum):
            for track in find_top_group_sub_tracks(group_enum.value):
                getattr(scene_state, group_enum.value).append(
                    SceneTrackState.create(track, group_enum, self.index)
                )

        return scene_state

    def disconnect(self) -> None:
        super(Scene, self).disconnect()
        self.scene_name.disconnect()
