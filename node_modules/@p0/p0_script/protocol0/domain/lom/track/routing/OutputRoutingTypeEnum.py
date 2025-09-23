from enum import Enum


class OutputRoutingTypeEnum(Enum):
    EXT_OUT = "Ext. Out"
    MASTER = "Master"
    SENDS_ONLY = "Sends Only"

    @property
    def label(self) -> str:
        return self.value
