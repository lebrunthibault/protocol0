from functools import partial

from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.track.simple_track.midi.special.CthulhuTrack import (
    toggle_cthulhu_routing,
    get_cthulhu_track,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus

# noinspection SpellCheckingInspection
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song


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

        # INIT song encoder
        self.add_encoder(
            identifier=4,
            name="(re) initialize the script",
            on_press=partial(DomainEventBus.emit, ScriptResetActivatedEvent()),
        )

        self.add_encoder(identifier=13, name="test", on_press=self.action_test)

        def _record_from_cthulhu() -> None:
            cthulhu_track = get_cthulhu_track(Song.selected_track())
            cthulhu_track.toggle_routing(force_cthulhu_routing=True)
            self._container.get(RecordService).record_track(
                Song.selected_track(), RecordTypeEnum.MIDI
            )

        # CThULhu encoder
        self.add_encoder(
            identifier=15,
            name="Cthulhu",
            on_press=lambda: partial(toggle_cthulhu_routing, Song.selected_track()),
            on_long_press=_record_from_cthulhu,
        )

        # VOLume encoder
        self.add_encoder(
            identifier=16,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )

    def action_test(self) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(Song.selected_track().input_routing.channel)
        channels = Song.selected_track()._track.available_input_routing_channels
        Logger.dev(channels)
        Logger.dev([c.display_name for c in channels])
