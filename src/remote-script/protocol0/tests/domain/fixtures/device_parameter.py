from _Framework.SubjectSlot import Subject


class AbletonDeviceParameter(Subject):
    __subject_events__ = ("value", "automation_state")

    def __init__(
        self,
        name: str,
        default_value: float = 0.0,
        min: float = 0.0,  # noqa: A002 (Live API attribute names)
        max: float = 1.0,  # noqa: A002
    ) -> None:
        self._live_ptr = id(self)
        self.name = name
        self.is_enabled = True
        self.default_value = default_value
        self.min = min
        self.max = max
        self.value = default_value
        self.is_quantized = False
        self.automation_state = 0

    def __repr__(self) -> str:
        return "AbletonDeviceParameter(%s=%s)" % (self.name, self.value)
