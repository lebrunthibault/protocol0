from functools import partial

from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import toggle_note_track_routing
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus

# noinspection SpellCheckingInspection
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ActionGroupMain(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        # TAP tempo encoder
        self.add_encoder(
            identifier=1,
            name="tap tempo",
            on_press=self._container.get(TempoComponent).tap,
            on_scroll=self._container.get(TempoComponent).scroll,
        )

        def log_param() -> None:
            param = Song.selected_parameter()
            device_name = Song.selected_device().name
            enum_name = f"{device_name.upper()}_{param.name.upper()}".replace(" ", "_")

            Logger.info(f"enum_name: {enum_name}")
            Logger.info(f"{param}: {param.min} - {param.max}. Default: {param.default_value}")
            param.reset()

        # PARAm encoder
        self.add_encoder(
            identifier=2,
            name="log param",
            on_press=log_param,
        )

        # FREeZ encoder
        self.add_encoder(
            identifier=3,
            name="freeze / unfreeze",
            on_press=lambda: Song.selected_track().freeze,
        )

        # INIT song encoder
        self.add_encoder(
            identifier=4,
            name="(re) initialize the script",
            on_press=partial(DomainEventBus.emit, ScriptResetActivatedEvent()),
        )

        # RESAmple encoder
        self.add_encoder(
            identifier=5,
            name="Resample",
            on_press=self._container.get(RecordService).resample_selected_track,
            on_long_press=partial(
                self._container.get(RecordService).resample_selected_track, record_audio=True
            ),
        )

        self.add_encoder(identifier=13, name="test", on_press=self.action_test)

        def _record_from_midi_note_track() -> None:
            toggle_note_track_routing(Song.selected_track(), force_routing=True)
            self._container.get(RecordService).record_track(
                Song.selected_track(), RecordTypeEnum.MIDI_OVERWRITE
            )

        # CThULhu encoder
        self.add_encoder(
            identifier=15,
            name="Midi",
            on_press=lambda: partial(toggle_note_track_routing, Song.selected_track()),
            on_long_press=_record_from_midi_note_track,
        )

        # VOLume encoder
        self.add_encoder(
            identifier=16,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )

    def action_test(self) -> None:
        pass
