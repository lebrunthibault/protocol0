from loguru import logger
from typing import Optional

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.settings import Settings
from p0_backend.lib.ableton.set_profiling.ableton_set_profiling_session import AbletonSetProfilingSession
from p0_backend.lib.window.find_window import find_window_handle_by_enum, SearchTypeEnum
from protocol0.application.command.ShowMessageCommand import ShowMessageCommand


class AbletonSetProfiler:
    NUMBER_OF_TESTS = 3
    last_set_reloaded_at: Optional[float] = None
    current_profiling_session: Optional[AbletonSetProfilingSession] = None

    @classmethod
    def handle_profiling_error(cls, message: str):
        logger.error(message)
        p0_script_client().dispatch(ShowMessageCommand(message))

    @classmethod
    def check_profiling_conditions(cls):
        if (
            find_window_handle_by_enum(Settings().log_window_title, SearchTypeEnum.WINDOW_TITLE)
            != 0
        ):
            cls.handle_profiling_error("Close the log message to start profiling")
            return False
        return True

    @classmethod
    def start_set_profiling(cls, number_of_tests=None, check_profiling_conditions=True):
        number_of_tests = number_of_tests or cls.NUMBER_OF_TESTS
        if check_profiling_conditions and not cls.check_profiling_conditions():
            return

        logger.info(f"Starting profiling, number of measures : {number_of_tests}")
        cls.current_profiling_session = AbletonSetProfilingSession(number_of_tests)
        cls.current_profiling_session.start_measurement()

    @classmethod
    def start_profiling_single_measurement(cls):
        cls.start_set_profiling(number_of_tests=1, check_profiling_conditions=False)

    @classmethod
    def end_measurement(cls):
        if cls.current_profiling_session is None:
            return
        cls.current_profiling_session.end_measurement()
        if cls.current_profiling_session._is_finished:
            cls.current_profiling_session = None
