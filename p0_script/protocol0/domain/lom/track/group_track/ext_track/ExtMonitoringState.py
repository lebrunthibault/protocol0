from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.ext_track.ExtArmState import (
    ExtArmState,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.observer.Observable import Observable


class ExtMonitoringState(Observable):
    def __init__(self, base_track: SimpleAudioTrack) -> None:
        super(ExtMonitoringState, self).__init__()
        self._midi_track = base_track.sub_tracks[0]
        self._audio_track = base_track.sub_tracks[1]

    def update(self, observable: Observable) -> None:
        if isinstance(observable, ExtArmState):
            if observable.is_armed:
                self.monitor_midi()
            else:
                self.monitor_audio()

    def monitor_midi(self) -> None:
        self._midi_track.muted = False

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN

    def monitor_audio(self) -> None:
        self._midi_track.muted = True
        if self._midi_track.instrument is not None:
            self._midi_track.instrument.device.is_enabled = False

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
