import collections
from functools import partial

from _Framework.SubjectSlot import SlotManager
from typing import Optional, Dict

from protocol0.domain.lom.scene.PlayingScene import PlayingScene
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SceneFiredEvent import SceneFiredEvent
from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.scheduler.ThirdBeatPassedEvent import ThirdBeatPassedEvent
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ScenePlaybackService(SlotManager):
    _DEBUG = False

    def __init__(self, playback_component: PlaybackComponent) -> None:
        super(ScenePlaybackService, self).__init__()
        self._playback_component = playback_component

        self._live_scene_id_to_scene: Dict[int, Scene] = collections.OrderedDict()

        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)
        DomainEventBus.subscribe(ThirdBeatPassedEvent, self._on_third_beat_passed_event)
        DomainEventBus.subscribe(ScenePositionScrolledEvent, self._on_scene_position_scrolled_event)
        DomainEventBus.subscribe(SongStoppedEvent, self._on_song_stopped_event)
        DomainEventBus.subscribe(SceneFiredEvent, self._on_scene_fired_event)

    def _on_bar_changed_event(self, _: BarChangedEvent) -> None:
        if Song.playing_scene():
            Song.playing_scene().scene_name.update()

    def _on_third_beat_passed_event(self, _: ThirdBeatPassedEvent) -> None:
        if Song.playing_scene() and Song.playing_scene().playing_state.is_playing:
            Scheduler.defer(Song.playing_scene().on_bar_end)

    def _on_scene_position_scrolled_event(self, _: ScenePositionScrolledEvent) -> None:
        scene = Song.selected_scene()
        Scene.LAST_MANUALLY_STARTED_SCENE = scene
        scene.scene_name.update(bar_position=scene.position_scroller.current_value)

    def fire_scene(self, scene: Scene) -> Optional[Sequence]:
        seq = Sequence()
        # stop to start the scene right again
        # also it will stop the tails
        seq.add(self._playback_component.stop)
        seq.defer()
        seq.add(scene.fire)

        return seq.done()

    def fire_scene_to_position(self, scene: Scene, bar_length: Optional[int] = None) -> Sequence:
        if bar_length is not None and bar_length >= scene.bar_length:
            bar_length = 0

        bar_length = self._get_position_bar_length(scene, bar_length)
        Scene.LAST_MANUALLY_STARTED_SCENE = scene

        if self._DEBUG:
            Logger.info("Firing %s to bar_length %s" % (scene, bar_length))

        # if bar_length != 0:
        # removing click when changing position
        # (created by playing shortly the scene beginning)
        # Song.master_track().mute_for(150)

        seq = Sequence()
        seq.add(self._playback_component.stop)
        seq.defer()  # removes an artefact by changing too fast the playback state
        seq.add(partial(scene.fire_to_position, bar_length))
        return seq.done()

    def _get_position_bar_length(self, scene: Scene, bar_length: Optional[int]) -> int:
        # as we use single digits
        if bar_length is None:
            return scene.position_scroller.current_value

        return bar_length

    def _on_song_stopped_event(self, _: SongStoppedEvent) -> None:
        # don't activate when doing quick play / stop (e.g. in FireSelectedSceneCommand)
        if not Song.is_playing():
            self._stop_previous_playing_scene()

    def _on_scene_fired_event(self, event: SceneFiredEvent) -> None:
        """Event is fired *before* the scene starts playing"""
        # Stop the previous scene : quantized or immediate
        playing_scene = Song.playing_scene()
        try:
            fired_scene = Song.scenes()[event.scene_index]
        except IndexError:
            return None

        if playing_scene is not None and playing_scene.index != event.scene_index:
            playing_scene.stop(immediate=not Song.is_playing(), next_scene=fired_scene)

        # update the playing scene singleton at the next bar
        seq = Sequence()
        if Song.is_playing():
            seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(partial(PlayingScene.set, fired_scene))
        seq.done()

    def _stop_previous_playing_scene(self) -> None:
        """
        Stop previous playing scene,
        else on play
        tracks with tail from the previous scene are going to play again
        """
        if PlayingScene.get_previous() is not None:
            PlayingScene.get_previous().stop(immediate=True)
