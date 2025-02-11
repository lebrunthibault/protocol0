from functools import partial
from typing import Optional

import Live

from protocol0.domain.lom.scene.PlayingScene import PlayingScene
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.QuantizationComponent import QuantizationComponent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.BaseRecorder import BaseRecorder, record_from_config
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.config.RecordProcessors import RecordProcessors
from protocol0.domain.track_recorder.event.RecordCancelledEvent import (
    RecordCancelledEvent,
)
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.domain.track_recorder.event.RecordStartedEvent import RecordStartedEvent
from protocol0.domain.track_recorder.recording_bar_length.RecordingBarLengthEnum import (
    RecordingBarLengthEnum,
)
from protocol0.domain.track_recorder.simple.RecorderSimpleFactory import (
    TrackRecorderSimpleFactory,
)
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class RecordService(object):
    _DEBUG = True

    def __init__(
        self,
        playback_component: PlaybackComponent,
        scene_crud_component: SceneCrudComponent,
        quantization_component: QuantizationComponent,
        track_crud_component: TrackCrudComponent,
    ) -> None:
        self._playback_component = playback_component
        self._scene_crud_component = scene_crud_component
        self._quantization_component = quantization_component
        self._track_crud_component = track_crud_component

        self._recorder: Optional[BaseRecorder] = None
        self._processors: Optional[RecordProcessors] = None

    @property
    def is_recording(self) -> bool:
        return self._recorder is not None

    def record_track(self, track: SimpleTrack, record_type: RecordTypeEnum) -> Optional[Sequence]:
        # we'll subscribe back later
        DomainEventBus.un_subscribe(SongStoppedEvent, self._on_song_stopped_event)

        if self._recorder is not None:
            self._cancel_record()
            return None

        if self._quantization_component.clip_trigger_quantization != Live.Song.Quantization.q_bar:
            self._quantization_component.clip_trigger_quantization = Live.Song.Quantization.q_bar

        recorder_factory = TrackRecorderSimpleFactory()
        config = recorder_factory.get_record_config(
            track=track,
            record_type=record_type,
            recording_bar_length=RecordingBarLengthEnum.ONE.bar_length_value,
        )
        self._processors = recorder_factory.get_processors(record_type)

        self._recorder = BaseRecorder(track, config)

        seq = Sequence()
        # assert there is a scene we can record on
        if config._scene_index is None:
            config.scene_index = len(Song.scenes())
            seq.add(self._scene_crud_component.create_scene)

        if self._DEBUG:
            Logger.info("recorder_config: %s" % config)

        Backend.client().show_info(f"Rec: {config.record_type.name} ({config.bar_length} bars)")

        seq.add(partial(self._start_recording, track, record_type, config))
        return seq.done()

    def _start_recording(
        self,
        track: SimpleTrack,
        record_type: RecordTypeEnum,
        config: RecordConfig,
    ) -> Optional[Sequence]:
        # this will stop the previous playing scene on playback stop
        PlayingScene.set(config.recording_scene)
        DomainEventBus.once(ErrorRaisedEvent, self._on_error_raised_event)

        seq = Sequence()

        # PRE RECORD
        seq.add(partial(self._recorder.pre_record, clear_clips=record_type.clear_clips))
        if self._processors.pre_record is not None:
            seq.add(partial(self._processors.pre_record.process, track, config))

        # COUNT IN
        if not Song.is_playing():
            count_in = partial(
                record_type.get_count_in().launch,
                self._playback_component,
                track,
                record_type.has_solo_count_in,
            )
            seq.add(count_in)

        seq.add(partial(DomainEventBus.subscribe, SongStoppedEvent, self._on_song_stopped_event))

        if not config.record_type.records_midi:
            seq.wait_ms(50)  # so that the record doesn't start before the clip slot is ready

        # RECORD
        record_event = RecordStartedEvent(
            config.scene_index,
            has_count_in=config.record_type.records_midi,
        )
        seq.add(partial(DomainEventBus.emit, record_event))

        if self._processors.record is not None:
            seq.add(partial(self._processors.record.process, track, config))
        else:
            seq.add(partial(record_from_config, self._recorder.config))

        if self._processors.on_record_end is not None:
            seq.add(partial(self._processors.on_record_end.process, track, config))

        seq.defer()
        seq.add(partial(DomainEventBus.emit, RecordEndedEvent()))

        seq.add(partial(Song.set_tempo, config.original_tempo))
        # POST RECORD
        if self._processors.post_record is not None:
            seq.add(partial(self._processors.post_record.process, track, config))

        seq.add(partial(setattr, self, "_recorder", None))
        seq.add(partial(DomainEventBus.un_subscribe, ErrorRaisedEvent, self._on_error_raised_event))

        return seq.done()

    def _on_error_raised_event(self, _: ErrorRaisedEvent) -> None:
        """Cancel the recording on any exception"""
        self._cancel_record(show_notification=False)

    def _cancel_record(self, show_notification: bool = True) -> None:
        DomainEventBus.emit(RecordCancelledEvent())
        Scheduler.restart()

        if self._recorder:
            self._recorder.cancel_record()
            if self._processors.on_record_cancelled:
                self._processors.on_record_cancelled.process(
                    self._recorder._track, self._recorder.config
                )

        self._recorder = None
        if show_notification:
            Backend.client().show_warning("Recording cancelled")

    def _on_song_stopped_event(self, _: SongStoppedEvent) -> None:
        """happens when manually stopping song while recording."""
        if self._recorder:
            self._cancel_record()

    def resample_selected_track(self, record_audio: bool = False) -> Optional[Sequence]:
        source_track = Song.selected_track()
        source_track.solo = True

        def get_existing_resampling_track() -> Optional[SimpleTrack]:
            try:
                next_track = list(Song.simple_tracks())[source_track.index + 1]
                if next_track.input_routing.track == source_track:
                    return next_track
            except IndexError:
                pass

            return None

        record_type = RecordTypeEnum.AUDIO
        track_creator = self._track_crud_component.create_audio_track

        seq = Sequence()

        if isinstance(source_track, SimpleMidiTrack) and not record_audio:
            record_type = RecordTypeEnum.MIDI_RESAMPLE
            track_creator = self._track_crud_component.create_midi_track

        resampling_track = get_existing_resampling_track()
        if resampling_track:
            clip_slot = resampling_track.clip_slots[Song.selected_scene().index]
            if clip_slot.clip:
                seq.add(clip_slot.clip.delete)
            seq.add(resampling_track.select)
        else:
            seq.add(partial(track_creator, source_track.index + 1))

        def set_routing() -> None:
            track = Song.selected_track()
            track.input_routing.track = source_track
            track.input_routing.channel = InputRoutingChannelEnum.POST_FX
            track.current_monitoring_state = CurrentMonitoringStateEnum.OFF
            track.devices.mixer_device.update_from_dict(source_track.devices.mixer_device.to_dict())
            track.arm_state.arm()

        seq.add(set_routing)

        if ApplicationView.is_session_visible():
            seq.add(lambda: self.record_track(Song.selected_track(), record_type))
        else:
            seq.add(Song.record)

        return seq.done()
