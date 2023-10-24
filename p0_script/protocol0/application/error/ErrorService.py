import sys
from traceback import extract_tb
from types import TracebackType
from typing import Any
from typing import Optional, List, Type

import Live

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.backend.BackendEvent import BackendEvent
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Config import Config
from protocol0.shared.Undo import Undo
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ErrorService(object):
    _DEBUG = True
    _SET_EXCEPTHOOK = False
    _IGNORED_ERROR_STRINGS = ("Cannot convert MIDI clip",)

    _IGNORED_ERROR_FILENAMES = ("\\venv\\", "\\sequence\\", "\\decorators.py")

    def __init__(self, song: Live.Song.Song) -> None:
        self._song = song

        if self._SET_EXCEPTHOOK:
            sys.excepthook = self._handle_uncaught_exception  # type: ignore[assignment]

        DomainEventBus.subscribe(ErrorRaisedEvent, self._on_error_raised_event)
        DomainEventBus.subscribe(BackendEvent, self._on_backend_event)

    def _on_error_raised_event(self, event: ErrorRaisedEvent) -> None:
        if event.reset:
            Undo.end_undo_step()
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_type and exc_value and tb, "cannot determine exception type and value"
        if issubclass(exc_type, Protocol0Warning) or issubclass(exc_type, AssertionError):
            error_message = str(exc_value or exc_type).strip()
            if issubclass(exc_type, AssertionError) and not error_message:
                error_message = "Unknown assertion error"
            Backend.client().show_error(error_message)
        else:
            self._handle_exception(exc_type, exc_value, tb, event.context, event.reset)

    def _on_backend_event(self, event: BackendEvent) -> None:
        if event.event == "error":
            self._restart()

    def _handle_uncaught_exception(
        self, exc_type: Type[BaseException], exc_value: BaseException, tb: TracebackType
    ) -> None:
        if any([string in str(exc_value) for string in self._IGNORED_ERROR_STRINGS]):
            pass
        Logger.error("unhandled exception caught")
        self._handle_exception(exc_type, exc_value, tb)

    @classmethod
    def log_stack_trace(cls) -> None:
        """This will be logged and displayed nicely by the Service"""

        @handle_errors()
        def raise_exception() -> None:
            raise RuntimeError("debug stack trace")

        raise_exception()

    def _handle_exception(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        tb: TracebackType,
        context: Optional[str] = None,
        reset: bool = True,
    ) -> None:
        entries = [fs for fs in extract_tb(tb) if self._log_file(fs[0])]
        if self._DEBUG:
            entries = extract_tb(tb)
        error_message = "  %s  \n" % exc_value
        error_message += "Exception: %s\n" % exc_type.__name__
        if context:
            error_message += str(context) + "\n"
        error_message += "at " + "".join(self._format_list(entries[-1:], print_line=False)).strip()

        if reset:
            error_message += "\n\n"
            error_message += "----- traceback -----\n"
            error_message += "".join(self._format_list(entries))

        self._log_error(error_message)

        if reset:
            self._restart()

    def _restart(self) -> None:
        Sequence.reset()

        # Scheduler.restart()
        # noinspection PyArgumentList
        self._song.stop_playing()  # prevent more errors coming through

    def _log_file(self, name: str) -> bool:
        if not name:
            return False
        elif not name.startswith(Config.PROJECT_ROOT):
            return False
        elif any([string in name for string in self._IGNORED_ERROR_FILENAMES]):
            return False

        return True

    def _format_list(self, extracted_list: List[Any], print_line: bool = True) -> List[str]:
        """Format a list of traceback entry tuples for printing.

        Given a list of tuples as returned by extract_tb() or
        extract_stack(), return a list of strings ready for printing.
        Each string in the resulting list corresponds to the item with the
        same index in the argument list.  Each string ends in a newline;
        the strings may contain internal newlines as well, for those items
        whose source text line is not None.
        """
        trace_list = []

        for filename, lineno, name, line in extracted_list:  # type: (str, int, str, str)
            item = "  %s, line %d, in %s\n" % (
                filename.replace(Config.PROJECT_ROOT, "../components"),
                lineno,
                name,
            )
            if line and print_line:
                item = item + "    %s\n" % line.strip()
            trace_list.append(item)
        return trace_list

    def _log_error(self, message: str) -> None:
        Logger.error(message, show_notification=False, debug=False)
