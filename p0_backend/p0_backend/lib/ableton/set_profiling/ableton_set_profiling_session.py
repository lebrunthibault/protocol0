import time
from loguru import logger
from typing import Optional, List

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import reload_ableton
from p0_backend.lib.utils import copy_to_clipboard
from protocol0.application.command.ShowMessageCommand import ShowMessageCommand


class AbletonSetProfilingSession:
    """we skip the first test as it is not in the average"""

    def __init__(self, number_of_tests):
        self.number_of_tests = number_of_tests
        self.last_set_reloaded_at: Optional[float] = None
        self.measurements: List[float] = []

    def __repr__(self):
        if len(self.measurements) > 0:
            return self._to_csv
        else:
            return "<empty>"

    def show_message(self, message: str):
        p0_script_client().dispatch(ShowMessageCommand(message))

    @property
    def _single_test(self):
        return self.number_of_tests == 1

    @property
    def _to_csv(self):
        """Skip the first measurement"""
        return ",".join(["%.2f" % m for m in self.measurements[1:]])

    @property
    def _to_google_sheet_formula(self):
        return f'=SPLIT("{self._to_csv}", ",")'

    @property
    def _is_finished(self) -> bool:
        return len(self.measurements) >= self.number_of_tests + 1

    def start_measurement(self):
        self.last_set_reloaded_at = time.time()
        reload_ableton()

    def end_measurement(self):
        reload_duration = time.time() - self.last_set_reloaded_at
        self.show_message("set reloaded in %.2f s" % reload_duration)

        if self._single_test:
            return

        self.measurements.append(reload_duration)

        if self._is_finished:
            copy_to_clipboard(self._to_google_sheet_formula)
            logger.info(f"{self._to_google_sheet_formula} copied to clipboard")
            self.show_message(f"set profiling over : {self._to_csv}")
        else:
            logger.info(
                f"Measurement {len(self.measurements)}/{self.number_of_tests + 1} finished, got %.2f s"
                % reload_duration
            )
            self.start_measurement()
