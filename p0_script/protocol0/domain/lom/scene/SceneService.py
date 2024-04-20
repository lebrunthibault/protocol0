import collections
from functools import partial
from itertools import chain
from typing import List, Iterator, Dict

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.scene.PlayingScene import PlayingScene
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SceneService(SlotManager):
    # noinspection PyInitNewSignature
    def __init__(
        self,
        live_song: Live.Song.Song,
        scene_crud_component: SceneCrudComponent,
        scene_playback_service: ScenePlaybackService,
    ) -> None:
        super(SceneService, self).__init__()
        self._live_song = live_song
        self._scene_crud_component = scene_crud_component
        self._scene_playback_service = scene_playback_service

        self.scenes_listener.subject = live_song
        self._live_scene_id_to_scene: Dict[int, Scene] = collections.OrderedDict()

    def get_scene(self, live_scene: Live.Scene.Scene) -> Scene:
        return self._live_scene_id_to_scene[live_scene._live_ptr]

    @property
    def scenes(self) -> List[Scene]:
        return list(self._live_scene_id_to_scene.values())

    @property
    def active_scenes(self) -> List[Scene]:
        current_scene = self.scenes[0]
        if current_scene.skipped:
            current_scene = current_scene.next_scene

        active_scenes = [current_scene]

        while current_scene.next_scene and current_scene.next_scene != current_scene:
            current_scene = current_scene.next_scene
            active_scenes.append(current_scene)

        return active_scenes

    @property
    def last_scene(self) -> Scene:
        current_scene = self.scenes[0]
        while current_scene.next_scene and current_scene.next_scene != current_scene:
            current_scene = current_scene.next_scene

        return current_scene

    @subject_slot("scenes")
    @handle_errors()
    def scenes_listener(self) -> None:
        previous_live_scenes_ids = self._live_scene_id_to_scene.keys()

        self._generate_scenes()
        for scene in Song.scenes():
            if len(previous_live_scenes_ids) and scene.live_id not in previous_live_scenes_ids:
                Scheduler.defer(scene.on_added)

        DomainEventBus.defer_emit(ScenesMappedEvent())

        Logger.info("mapped scenes")

    def _generate_scenes(self) -> None:
        # save playing scene
        playing_live_scene = Song.playing_scene()._scene if Song.playing_scene() else None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        tracks: Iterator[AbstractTrack] = chain(Song.simple_tracks(), Song.abstract_tracks())
        for track in collections.OrderedDict.fromkeys(tracks):
            track.on_scenes_change()

        live_scenes = self._live_song.scenes

        # get the right scene or instantiate new scenes
        for index, live_scene in enumerate(live_scenes):
            self.generate_scene(live_scene, index=index)

        self._sort_scenes()

        # restore playing scene
        if playing_live_scene is not None:
            playing_scene = find_if(lambda s: s._scene == playing_live_scene, Song.scenes())
            PlayingScene.set(playing_scene)

    def _clean_deleted_scenes(self) -> None:
        """cleaning all scenes always"""
        existing_scene_ids = [scene._live_ptr for scene in self._live_song.scenes]

        deleted_scenes = []

        for scene_id, scene in self._live_scene_id_to_scene.copy().items():
            # refresh the mapping
            if scene_id not in existing_scene_ids:
                # checking on name and not bar_length
                if len(Song.scenes()) > 5 and scene.name != "0":
                    deleted_scenes.append(scene)

                del self._live_scene_id_to_scene[scene_id]

            scene.disconnect()
            if scene == Song.playing_scene():
                PlayingScene.set(None)

        if len(deleted_scenes) == 1:
            Backend.client().show_warning(f"You just deleted {deleted_scenes[0]}")
        elif len(deleted_scenes) > 1:
            Backend.client().show_warning(f"You just deleted {len(deleted_scenes)} scenes")

    def generate_scene(self, live_scene: Live.Scene.Scene, index: int) -> None:
        # switching to full remap because of persisting mapping problems when moving scenes
        scene = Scene(live_scene, index)
        self._live_scene_id_to_scene[scene.live_id] = scene

    def _sort_scenes(self) -> None:
        sorted_dict = collections.OrderedDict()
        for scene in self._live_song.scenes:
            sorted_dict[scene._live_ptr] = self.get_scene(scene)
        self._live_scene_id_to_scene = sorted_dict

    def duplicate_scene(self) -> Sequence:
        selected_scene_index = Song.selected_scene().index
        seq = Sequence()
        seq.add(partial(self._scene_crud_component.duplicate_scene, Song.selected_scene()))
        seq.add(
            lambda: self._scene_playback_service.fire_scene(Song.scenes()[selected_scene_index + 1])
        )
        return seq.done()
