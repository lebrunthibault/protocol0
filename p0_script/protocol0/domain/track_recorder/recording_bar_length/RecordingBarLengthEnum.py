from enum import Enum


class RecordingBarLengthEnum(Enum):
    _order_ = "ONE, TWO, FOUR, EIGHT, SIXTEEN, TWENTY_FOUR, THIRTY_TWO, SIXTY_FOUR"

    ONE = 1
    TWO = 2
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
    TWENTY_FOUR = 24
    THIRTY_TWO = 32
    SIXTY_FOUR = 64

    @property
    def bar_length_value(self) -> int:
        return self.value

    def __str__(self) -> str:
        return "%s bar%s" % (self.value, "s" if abs(self.value) != 1 else "")
