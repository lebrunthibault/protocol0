from collections import deque
from functools import partial
from typing import Deque, Iterable, Union, Any, Optional, List, Type, Callable, cast

from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.backend.BackendEvent import BackendEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.event.HasEmitter import HasEmitter
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.debug import get_frame_info
from protocol0.domain.shared.utils.func import nop, get_callable_repr
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.ParallelSequence import ParallelSequence
from protocol0.shared.sequence.SequenceState import SequenceState
from protocol0.shared.sequence.SequenceStep import SequenceStep
from protocol0.shared.sequence.SequenceTransition import SequenceStateEnum


class Sequence(Observable):
    """
    Replacement of the _Framework Task.
    I added asynchronous behavior by hooking in my own event system,
    including communication with the backend
    Encapsulates and composes all asynchronous tasks done in the script.
    """

    RUNNING_SEQUENCES: List["Sequence"] = []
    _DEBUG = False
    _STEP_TIMEOUT = 50  # seconds

    def __init__(self, name: Optional[str] = None) -> None:
        super(Sequence, self).__init__()

        self._steps: Deque[SequenceStep] = deque()
        self._current_step: Optional[SequenceStep] = None
        self.state = SequenceState()
        self.res: Optional[Any] = None
        frame_info = get_frame_info(2)
        if name:
            self.name = name
        elif frame_info:
            self.name = "[seq %s.%s]" % (frame_info.class_name, frame_info.method_name)
        else:
            self.name = "Unknown"

    def __repr__(self, **k: Any) -> str:
        return self.name

    def add(
        self,
        func: Union[Iterable, Callable, object] = nop,
        name: str = None,
        notify_terminated: bool = True,
    ) -> "Sequence":
        """callback can be a callable or a list of callable (will execute in parallel)"""
        assert callable(func) or isinstance(
            func, Iterable
        ), "You passed a non callable (%s) to %s" % (func, self)
        if isinstance(func, List):
            func = ParallelSequence(func).start

        func = cast(Callable, func)

        step_name = "%s : step %s" % (self.name, name or get_callable_repr(func))

        step = SequenceStep(func, step_name, notify_terminated)
        self._steps.append(step)

        return self

    def done(self) -> "Sequence":
        self.state.change_to(SequenceStateEnum.STARTED)
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()
        return self

    def _execute_next_step(self) -> None:
        if not self.state.started:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self._DEBUG:
                Logger.info("%s : Executing %s" % (self, self._current_step))
            self._current_step.register_observer(self)
            self._current_step.start()
        else:
            self._terminate()

    @classmethod
    def reset(cls, name: Optional[str] = None) -> None:
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            if name is not None and seq.name != name:
                continue

            seq._cancel()
        Sequence.RUNNING_SEQUENCES = []

    def update(self, observable: Observable) -> None:
        if isinstance(observable, SequenceStep):
            if observable.state.terminated:
                if self._DEBUG:
                    Logger.info("step terminated : %s" % self._current_step)
                self._execute_next_step()
            elif observable.state.errored:
                self._error()
            elif observable.state.cancelled:
                self._cancel()

            observable.remove_observer(self)

    def _error(self) -> None:
        self.state.change_to(SequenceStateEnum.ERRORED)
        self.disconnect()
        if self._DEBUG:
            Logger.warning("Sequence errored : %s" % self)

    def _cancel(self) -> None:
        if self.state.started:
            self.state.change_to(SequenceStateEnum.CANCELLED)
            Logger.warning("%s has been cancelled" % self)
            if self._current_step:
                self._current_step.cancel()
            self.disconnect()

    def _terminate(self) -> None:
        self.state.change_to(SequenceStateEnum.TERMINATED)

        self.res = self._current_step.res if self._current_step else None
        self.notify_observers()
        self.disconnect()

    """ ACTIONS """

    def log(self, message: str) -> "Sequence":
        return self.add(lambda: Logger.warning(message))

    def defer(self) -> "Sequence":
        return self.add(partial(Scheduler.defer, self._execute_next_step), notify_terminated=False)

    def wait(self, ticks: int) -> "Sequence":
        return self.add(
            partial(Scheduler.wait, ticks, self._execute_next_step), notify_terminated=False
        )

    def wait_ms(self, ms: int) -> "Sequence":
        return self.add(
            partial(Scheduler.wait_ms, ms, self._execute_next_step), notify_terminated=False
        )

    def wait_bars(
        self, bars: float, wait_for_song_start: bool = False, continue_on_song_stop: bool = False
    ) -> "Sequence":
        if not Song.is_playing() and wait_for_song_start:
            self.wait_for_event(SongStartedEvent)

        return self.wait_beats(
            bars * Song.signature_numerator(), continue_on_song_stop=continue_on_song_stop
        )

    def wait_beats(self, beats: float, continue_on_song_stop: bool = False) -> "Sequence":
        def execute() -> None:
            if not Song.is_playing():
                if continue_on_song_stop:
                    self._execute_next_step()
                    return
                else:
                    Logger.warning("Cannot wait %s beats, song is not playing. %s" % (beats, self))
            else:
                Scheduler.wait_beats(beats, self._execute_next_step)

            # make sure step is called if the song stops
            if continue_on_song_stop:
                DomainEventBus.subscribe(SongStoppedEvent, lambda _: self._execute_next_step())

        return self.add(execute, notify_terminated=False)

    def wait_for_event(
        self,
        event_class: Type[object],
        expected_emitter: object = None,
        continue_on_song_stop: bool = False,
    ) -> "Sequence":
        """
        Will continue the sequence after an event of type event_class is fired

        expected_emitter : passing an object here will check that the event was
        emitter from the right emitter before continuing the Sequence

        continue_on_song_stop: for events relying on a playing song, setting
        continue_on_song_stop to
        True
        will continue the sequence on a SongStoppedEvent
        """
        if expected_emitter is not None:
            assert issubclass(event_class, HasEmitter), "expected emitter should be an Emitter"

        def subscribe() -> None:
            DomainEventBus.subscribe(event_class, on_event)
            if continue_on_song_stop:
                if not Song.is_playing():
                    on_event(SongStoppedEvent())
                else:
                    DomainEventBus.once(SongStoppedEvent, on_event)

        def on_event(event: object) -> None:
            if expected_emitter is not None and isinstance(event, HasEmitter):
                if self._DEBUG:
                    Logger.info(
                        "expected emitter: %s, event.target(): %s"
                        % (expected_emitter, event.target())
                    )
                if event.target() != expected_emitter:
                    return  # not the right emitter

            DomainEventBus.un_subscribe(event_class, on_event)
            DomainEventBus.un_subscribe(SongStoppedEvent, on_event)
            if self.state.started:
                self._execute_next_step()

        return self._add_timeout_step(subscribe, "wait_for_event %s" % event_class)

    def wait_for_backend_event(self, event_type: str, timeout: int = 0) -> "Sequence":
        """event types are hardcoded in the script and backend"""

        def step() -> None:
            DomainEventBus.subscribe(BackendEvent, on_event)

            if timeout:
                Scheduler.wait_ms(timeout, cancel)

        def on_event(backend_event: BackendEvent) -> None:
            if event_type != backend_event.event:
                return

            DomainEventBus.un_subscribe(BackendEvent, on_event)

            if self.state.started:
                self.res = backend_event.data
                self._execute_next_step()

        def cancel() -> None:
            DomainEventBus.un_subscribe(BackendEvent, on_event)
            self._cancel()

        self.add(step, notify_terminated=False)

        return self

    def _add_timeout_step(self, func: Callable, legend: str) -> "Sequence":
        seconds = self._STEP_TIMEOUT

        def cancel() -> None:
            if self._current_step and self._current_step._callable == execute:
                self._cancel()
                Logger.warning("cancelling after %s seconds : %s on %s" % (seconds, self, legend))

        def execute() -> None:
            Scheduler.wait_ms(seconds * 1000, cancel)
            func()

        return self.add(execute, notify_terminated=False)

    def disconnect(self) -> None:
        self._current_step = None
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass
