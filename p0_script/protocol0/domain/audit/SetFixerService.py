from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class SetFixerService(object):
    def __init__(self, validator_service: ValidatorService) -> None:
        self._validator_service = validator_service

    def fix_set(self) -> None:
        """Fix the current set to the current standard regarding naming / coloring etc .."""
        Logger.clear()

        invalid_objects = []

        objects_to_validate = Song.scenes() + list(Song.abstract_tracks())  # noqa
        for obj in objects_to_validate:
            is_valid = self._validator_service.validate_object(obj)
            if not is_valid:
                invalid_objects.append(obj)

        def is_routed_to_master(t: SimpleTrack) -> bool:
            return (
                t.name.lower().strip() not in ("*", "pre")
                and isinstance(t, SimpleAudioTrack)
                and t.output_routing.track == Song.master_track()
            )

        routed_to_master = list(filter(is_routed_to_master, Song.simple_tracks()))

        if len(routed_to_master) != 0:
            Backend.client().show_warning("Too many tracks routed to master")
            Logger.info(f"Routed to master: {routed_to_master}")
            return

        if len(invalid_objects) == 0:
            self._refresh_objects_appearance()
        else:
            Backend.client().show_warning("Invalid set: fixing")
            for invalid_object in invalid_objects:
                self._validator_service.fix_object(invalid_object, log=False)
            Logger.info("set fixed")

    def _refresh_objects_appearance(self) -> None:
        clip_slots = [cs for track in Song.simple_tracks() for cs in track.clip_slots]
        clips = [clip for track in Song.simple_tracks() for clip in track.clips]
        # noinspection PyTypeChecker
        objects_to_refresh_appearance = clip_slots + clips + Song.scenes()

        for obj in objects_to_refresh_appearance:
            obj.appearance.refresh()

        for track in Song.external_synth_tracks():
            track.midi_track.name = "m"
            track.audio_track.name = "a"
