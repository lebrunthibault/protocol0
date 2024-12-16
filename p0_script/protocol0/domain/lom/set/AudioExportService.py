from functools import partial

from protocol0.domain.audit.SongStatsService import SongStatsService
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioExportService(object):
    def __init__(
        self,
        song_stats_service: SongStatsService,
        playback_component: PlaybackComponent,
        scene_component: SceneComponent,
    ):
        self._song_stats_service = song_stats_service
        self._playback_component = playback_component
        self._scene_component = scene_component

    def on_export(self) -> None:
        Backend.client().post_scene_stats(
            {
                "scenes": [],
                "tempo": Song.tempo(),
            }
        )
        monitoring_rack: Device = list(Song.master_track().devices)[-1]
        assert monitoring_rack.name.lower() == "monitoring"
        monitoring_rack.is_enabled = False

    def write_session_to_arrangement(self) -> None:
        scene_stats = self._song_stats_service.get_song_structure()

        Backend.client().post_scene_stats(
            {
                "scenes": scene_stats.to_full_dict()["scenes"],
                "tempo": Song.tempo(),
            }
        )

        self._playback_component.reset()

        ApplicationView.show_arrangement()

        for track in Song.simple_tracks():
            track.clear_arrangement()
        seq = Sequence()
        seq.add(self._bounce_session_to_arrangement)
        seq.add(self._create_cue_points)
        seq.wait_ms(50)
        seq.add(self._playback_component.reset)
        seq.done()

    def _bounce_session_to_arrangement(self) -> None:
        sound_id_device = Song.master_track().devices.get_one_from_enum(
            DeviceEnum.SOUNDID_REFERENCE_PLUGIN
        )
        if sound_id_device is not None and sound_id_device.is_enabled:
            sound_id_device.is_enabled = False
            Logger.warning("Deactivating SoundID Reference plugin for export")

        for track in Song.simple_tracks():
            track.clear_arrangement()

        self._scene_component.looping_scene_toggler.reset()

        song_time = 0.0
        for scene in Song.active_scenes():
            scene_start = song_time
            scene_end = song_time + scene.length

            for scene_cs in scene.clips.clip_slot_tracks:
                clip = scene_cs.clip
                if not clip:
                    continue

                song_time = scene_start

                # emulate the session handling of tails
                has_tail = clip.loop.end != clip.loop.end_marker
                loop_end = clip.loop.end
                if has_tail:
                    clip.loop.end = clip.loop.end_marker

                while song_time < scene_end:
                    scene_cs.track.duplicate_clip_to_arrangement(clip, song_time)
                    song_time += clip.length

                # restore session loop
                if has_tail:
                    clip.loop.end = loop_end

            song_time = scene_end

    def _create_cue_points(self) -> Sequence:
        song_time = 0.0

        seq = Sequence()

        for scene in Song.active_scenes():
            if scene.scene_name.get_base_name():
                seq.add(partial(Song.set_or_delete_cue, song_time))

            song_time += scene.length

        return seq.done()
