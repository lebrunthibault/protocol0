from functools import partial

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ResetPlaybackCommand import ResetPlaybackCommand
from protocol0.domain.lom.device.DeviceDisplayService import DeviceDisplayService
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.simple_track.midi.special.CthulhuTrack import CthulhuTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SongInitService(object):
    def __init__(
        self,
        playback_component: PlaybackComponent,
        device_display_service: DeviceDisplayService,
        ableton_set: AbletonSet,
    ) -> None:
        self._playback_component = playback_component
        self._device_display_service = device_display_service
        self._ableton_set = ableton_set

    def init_song(self) -> Sequence:
        self._log_outdated_plugins()

        # the song usually starts playing after this method is executed
        CommandBus.dispatch(ResetPlaybackCommand())

        DomainEventBus.emit(SongInitializedEvent())

        seq = Sequence()
        seq.wait(2)
        selected_track = Song.selected_track()
        for track in Song.simple_tracks():
            if isinstance(track, CthulhuTrack):
                seq.add(track.select)
                seq.add(
                    partial(
                        self._device_display_service.toggle_plugin_window,
                        track,
                        list(track.devices)[0],
                    )
                )
        seq.add(ApplicationView.show_session)
        seq.add(selected_track.select)
        seq.wait(8)

        seq.add(self._playback_component.reset)
        seq.add(self._ableton_set.loop_notify_selected_scene)

        return seq.done()

    def _log_outdated_plugins(self) -> None:
        tracks = []

        for track in Song.simple_tracks():
            black_box = find_if(lambda d: d.enum == DeviceEnum.BLACK_BOX_MS, track.devices)

            if black_box:
                tracks.append(track)

        if len(tracks):
            message = f"Found blackbox on {' - '.join(tracks)}"
            Logger.info(message)
            Backend.client().show_warning(message)
