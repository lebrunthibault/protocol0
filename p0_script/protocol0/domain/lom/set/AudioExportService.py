from functools import partial

from protocol0.domain.audit.SetFixerService import SetFixerService
from protocol0.domain.audit.SongStatsService import SongStatsService
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioExportService(object):
    def __init__(
        self,
        song_stats_service: SongStatsService,
        set_fixer_service: SetFixerService,
        playback_component: PlaybackComponent,
    ):
        self._song_stats_service = song_stats_service
        self._set_fixer_service = set_fixer_service
        self._playback_component = playback_component

    def export(self) -> None:
        self._set_fixer_service.fix_set()
        self._song_stats_service.export_song_structure()
        self._bounce_session_to_arrangement()

        self._playback_component.reset()
        ApplicationView.show_arrangement()

        # hack to show 1.1.1 in the arrangement
        Song.view().follow_song = True
        self._playback_component.start_playing()

        seq = Sequence()
        seq.wait_ms(50)
        seq.add(self._playback_component.reset)
        seq.add(partial(setattr, Song.view(), "follow_song", False))
        seq.wait_ms(200)
        seq.add(Backend.client().export_audio)
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

        time = 0.0
        for scene in Song.scenes():
            scene_start = time
            scene_end = time + scene.length

            for scene_cs in scene.clips.clip_slot_tracks:
                clip = scene_cs.clip
                if not clip:
                    continue

                time = scene_start

                # emulate the session handling of tails
                has_tail = clip.loop.end != clip.loop.end_marker
                loop_end = clip.loop.end
                if has_tail:
                    clip.loop.end = clip.loop.end_marker

                while time < scene_end:
                    scene_cs.track.duplicate_clip_to_arrangement(clip, time)
                    time += clip.length

                # restore session loop
                if has_tail:
                    clip.loop.end = loop_end

            time = scene_end
