from protocol0.shared.AbstractEnum import AbstractEnum


class OutputRoutingTypeEnum(AbstractEnum):
    EXT_OUT = "Ext. Out"
    MASTER = "Master"
    SENDS_ONLY = "Sends Only"

    @property
    def label(self) -> str:
        return self.value
