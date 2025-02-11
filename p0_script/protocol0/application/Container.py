from typing import Type, Dict, Any

import Live
from _Framework.ControlSurface import ControlSurface

from protocol0.application.CommandBus import CommandBus
from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.control_surface.ActionGroupFactory import ActionGroupFactory
from protocol0.application.error.ErrorService import ErrorService
from protocol0.domain.audit.LogService import LogService
from protocol0.domain.audit.SongStatsService import SongStatsService
from protocol0.domain.lom.device.DeviceDisplayService import DeviceDisplayService
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.instrument.instrument.InstrumentService import InstrumentService
from protocol0.domain.lom.scene.PlayingScene import PlayingScene
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.set.AudioExportService import AudioExportService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.QuantizationComponent import QuantizationComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.infra.interface.BrowserLoaderService import BrowserLoaderService
from protocol0.infra.interface.BrowserService import BrowserService
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.midi.MidiService import MidiService
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.TickScheduler import TickScheduler
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.types import T


class Container(ContainerInterface):
    """Direct DI container"""

    def __init__(self, control_surface: ControlSurface) -> None:
        self._registry: Dict[Type, Any] = {}

        live_song: Live.Song.Song = control_surface.song()

        Logger(LoggerService())
        Undo(live_song.begin_undo_step, live_song.end_undo_step)
        StatusBar(control_surface.show_message)
        Backend(control_surface._send_midi)
        ErrorService(live_song)
        midi_service = MidiService(control_surface._send_midi)
        beat_scheduler = BeatScheduler(live_song)
        tick_scheduler = TickScheduler(beat_scheduler, live_song)
        Scheduler(tick_scheduler, beat_scheduler)  # setup Scheduler facade

        # song components
        device_component = DeviceComponent(live_song.view)
        playback_component = PlaybackComponent(live_song)
        tempo_component = TempoComponent(live_song)
        quantization_component = QuantizationComponent(live_song, tempo_component)
        recording_component = RecordingComponent(live_song)
        scene_component = SceneComponent(live_song.view)
        scene_crud_component = SceneCrudComponent(
            live_song.create_scene, live_song.duplicate_scene, live_song.delete_scene
        )

        track_component = TrackComponent(live_song.view)
        track_crud_component = TrackCrudComponent(
            live_song.create_midi_track,
            live_song.create_audio_track,
            live_song.duplicate_track,
            live_song.delete_track,
        )

        ableton_set = AbletonSet()

        CommandBus(self, ableton_set)

        ApplicationView(recording_component, control_surface.application().view)

        browser = control_surface.application().browser
        browser_service = BrowserService(browser, BrowserLoaderService(browser))
        DeviceDisplayService()
        device_service = DeviceService(
            track_crud_component, device_component, browser_service, live_song.move_device
        )
        instrument_service = InstrumentService(device_service, device_component)
        track_factory = TrackFactory(track_crud_component, browser_service)
        track_mapper_service = TrackMapperService(live_song, track_factory)
        scene_service = SceneService(live_song, scene_crud_component)
        PlayingScene(scene_component)
        track_recorder_service = RecordService(
            playback_component,
            scene_crud_component,
            quantization_component,
            track_crud_component,
        )
        song_stats_service = SongStatsService(ableton_set)
        audio_export_service = AudioExportService(
            song_stats_service, playback_component, scene_component
        )
        Song(
            live_song,
            device_component,
            playback_component,
            quantization_component,
            recording_component,
            scene_component,
            tempo_component,
            scene_service,
            track_mapper_service,
        )

        mixing_service = MixingService()

        # audit
        log_service = LogService(ableton_set, track_mapper_service)

        self._register(midi_service)
        self._register(browser_service)

        # song components
        self._register(playback_component)
        self._register(scene_component)
        self._register(scene_crud_component)
        self._register(device_component)
        self._register(ableton_set)
        self._register(track_component)
        self._register(track_crud_component)
        self._register(tempo_component)

        self._register(track_factory)
        self._register(track_mapper_service)

        self._register(scene_service)
        self._register(instrument_service)
        self._register(device_service)

        self._register(mixing_service)
        self._register(track_recorder_service)

        # audit
        self._register(log_service)
        self._register(song_stats_service)

        self._register(audio_export_service)

        ActionGroupFactory.create_action_groups(self, control_surface.component_guard)

    def _register(self, service: object) -> None:
        if service.__class__ in self._registry:
            raise Protocol0Error("service already registered in container : %s" % service)
        self._registry[service.__class__] = service

        base_class = service.__class__.__base__
        if base_class.__name__.endswith("Interface"):
            if base_class in self._registry:
                raise Protocol0Error("interface already registered in container : %s" % base_class)
            self._registry[base_class] = service

    def get(self, cls: Type[T]) -> T:
        if cls not in self._registry:
            raise Protocol0Error("Couldn't find %s in container" % cls)

        return self._registry[cls]

    def _disconnect(self) -> None:
        Scheduler.reset()
        self.get(SceneService).disconnect()
        self.get(PlaybackComponent).disconnect()
        self.get(TempoComponent).disconnect()
        self.get(TrackComponent).disconnect()
        self.get(TrackMapperService).disconnect()

        self._registry = {}
