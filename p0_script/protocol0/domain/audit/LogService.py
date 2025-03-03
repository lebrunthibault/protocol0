from protocol0.domain.audit.utils import tail_logs
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class LogService(object):
    def __init__(
        self,
        ableton_set: AbletonSet,
        track_mapper_service: TrackMapperService,
    ) -> None:
        self._ableton_set = ableton_set
        self._track_mapper_service = track_mapper_service

    @tail_logs
    def log_current(self) -> None:
        Logger.clear()

        Logger.info("********* SELECTED_TRACK *************")
        Logger.info("selected_track: %s" % Song.selected_track())
        Logger.info()
        Logger.info("selected_track.color: %s" % Song.selected_track().color)
        Logger.info()
        Logger.info("selected_track.group_track: %s" % Song.selected_track().group_track)
        Logger.info()
        Logger.info("selected_track.sub_tracks: %s" % Song.selected_track().sub_tracks)
        Logger.info()
        Logger.info()
        Logger.info("selected_track.clip_slots: %s" % Song.selected_track().clip_slots)
        Logger.info()
        Logger.info("selected_track.clips: %s" % Song.selected_track().clips)
        Logger.info()
        Logger.info("selected_track.instrument: %s" % Song.selected_track().instrument)
        if Song.selected_track().instrument:
            Logger.info(
                "selected_track.instrument.device: %s" % Song.selected_track().instrument.device
            )
        Logger.info()
        Logger.info("********* SELECTED_SCENE *************")
        Logger.info()
        Logger.info("selected_scene: %s" % Song.selected_scene())
        Logger.info()
        Logger.info("selected_scene.clips.all: %s" % Song.selected_scene().clips.all)
        Logger.info()
        Logger.info("selected_scene.clips.tracks: %s" % Song.selected_scene().clips.tracks)
        Logger.info()
        longest_clip = Song.selected_scene()._scene_length.get_longest_clip()
        clip_track = find_if(lambda t: longest_clip in t.clips, Song.simple_tracks())
        Logger.info("selected_scene.longest_clip: %s (%s)" % (longest_clip, clip_track))
        Logger.info()
        Logger.info("********* SELECTED_DEVICE *************")
        Logger.info()
        try:
            Logger.info("selected_device: %s" % Song.selected_track().devices.selected)
            Logger.info()
        except AssertionError:
            pass
        Logger.info("selected_parameter: %s" % Song.selected_parameter())
        if Song.selected_parameter():
            Logger.info()
            Logger.info("selected_parameter: %s" % Song.selected_parameter())
            Logger.info()
            if Song.selected_track().devices.selected is not None:
                Logger.info(
                    "selected_device.parameters: %s"
                    % Song.selected_track().devices.selected.parameters
                )
        Logger.info()

        if Song.selected_track().instrument:
            Logger.info("********* INSTRUMENT *************")
            Logger.info()
            Logger.info("selected_track.instrument: %s" % Song.selected_track().instrument)
            Logger.info()

    @tail_logs
    def log_set(self) -> None:
        Logger.clear()

        Logger.info("********* GLOBAL objects *************")
        Logger.info("song.is_playing: %s" % Song.is_playing())
        Logger.info()
        Logger.info("song.midi_recording_quantization: %s" % Song.midi_recording_quantization())
        Logger.info()
        Logger.info("********* SONG TRACKS *************")
        Logger.info(
            "live_tracks : %s"
            % list(self._track_mapper_service._live_track_id_to_simple_track.values())
        )
        Logger.info()
        Logger.info("simple_tracks : %s" % list(Song.simple_tracks()))
        Logger.info()
        Logger.info("********* SELECTED_CLIP_SLOT *************")
        Logger.info()
        Logger.info("song.selected_clip_slot: %s" % Song.selected_clip_slot())
        if Song.selected_clip_slot():
            Logger.info(
                "song.selected_clip_slot._clip_slot: %s" % Song.selected_clip_slot()._clip_slot
            )

        if Song.selected_clip_slot().clip is not None:
            selected_clip = Song.selected_clip()
            Logger.info()
            Logger.info("********* SELECTED_CLIP *************")
            Logger.info()
            Logger.info("song.selected_clip: %s" % selected_clip)
            Logger.info()
            Logger.info("song.selected_clip.length: %s" % selected_clip.length)
            Logger.info()

        Logger.info()
        Logger.info("********* ABLETON_SET *************")
        Logger.info(self._ableton_set.to_model())
