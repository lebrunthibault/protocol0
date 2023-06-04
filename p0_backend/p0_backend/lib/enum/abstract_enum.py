from enum import Enum
from typing import Any, Dict

from p0_backend.lib.errors.Protocol0Error import Protocol0Error


class AbstractEnum(Enum):
    def get_value_from_mapping(self, mapping: Dict["AbstractEnum", Any]):
        if self not in mapping:
            raise Protocol0Error("Couldn't find enum %s in mapping" % self)
        return mapping[self]
