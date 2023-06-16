from typing import Any, Optional, Callable

from protocol0.shared.sequence.Sequence import Sequence
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface


class CallbackValidator(ValidatorInterface):
    def __init__(self, obj: Any, callback_validator: Callable, callback_fixer: Optional[Callable] = None, error_message: Optional[str] = None) -> None:
        self._obj = obj
        self._callback_validator = callback_validator
        self._callback_fixer = callback_fixer
        self._error_message = error_message

    def get_error_message(self) -> Optional[str]:
        if self.is_valid():
            return None
        else:
            return self._error_message or "callback failed for %s" % self._obj

    def is_valid(self) -> bool:
        return self._callback_validator(self._obj)

    def fix(self) -> Optional[Sequence]:
        if self._callback_fixer is not None:
            return self._callback_fixer(self._obj)
        else:
            return None
