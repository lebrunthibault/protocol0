from protocol0.shared.AbstractEnum import AbstractEnum


class OutputRoutingTypeEnum(AbstractEnum):
    MASTER = "Master"
    SENDS_ONLY = "Sends Only"

    @property
    def label(self) -> str:
        return self.value
