import traceback

from typing import Any, Callable, Optional

from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.utils.func import get_callable_repr
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.HasSequenceState import HasSequenceState
from protocol0.shared.sequence.SequenceState import SequenceState
from protocol0.shared.sequence.SequenceTransition import SequenceStateEnum


class SequenceStep(Observable):
    def __init__(self, func: Callable, name: str, notify_terminated: bool) -> None:
        super(SequenceStep, self).__init__()
        self._name = name
        self._callable = func
        self.state = SequenceState()
        self._notify_terminated = notify_terminated
        self.res: Optional[Any] = None

    def __repr__(self, **k: Any) -> str:
        return self._name

    def update(self, observable: Observable) -> None:
        if isinstance(observable, HasSequenceState):
            if observable.state.terminated:
                self._terminate(observable.res)
                observable.remove_observer(self)

    @handle_errors()
    def start(self) -> None:
        self.state.change_to(SequenceStateEnum.STARTED)
        # noinspection PyBroadException
        try:
            self._execute()
        except Exception as e:
            self._error()
            Logger.warning("Error on %s" % get_callable_repr(self._callable))
            Logger.warning(traceback.format_exc())
            raise e

    def _execute(self) -> None:
        res = self._callable()

        if isinstance(res, HasSequenceState):
            if res.state.errored:
                self._error()
            elif res.state.cancelled:
                self.cancel()
            elif res.state.terminated:
                self._terminate(res.res)
            else:
                res.register_observer(self)
        else:
            self._terminate(res)

    def _error(self) -> None:
        if self.state.started:
            self.state.change_to(SequenceStateEnum.ERRORED)
            self.notify_observers()

    def cancel(self) -> None:
        if self.state.started:
            self.state.change_to(SequenceStateEnum.CANCELLED)
            self.notify_observers()

    def _terminate(self, res: Any) -> None:
        if self.state.cancelled or self.state.errored or self.state.terminated:
            return
        self.res = res
        self.state.change_to(SequenceStateEnum.TERMINATED)
        if self._notify_terminated:
            self.notify_observers()
