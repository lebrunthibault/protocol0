from abc import ABCMeta, abstractmethod

from typing import Optional

from protocol0.shared.sequence.Sequence import Sequence


class ValidatorInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_error_message(self) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def fix(self) -> Optional[Sequence]:
        raise NotImplementedError
