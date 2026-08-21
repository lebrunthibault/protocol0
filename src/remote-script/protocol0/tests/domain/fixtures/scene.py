from _Framework.SubjectSlot import Subject


class AbletonScene(Subject):
    __subject_events__ = ("name", "is_triggered", "color")

    def __init__(self):
        self._live_ptr = id(self)
        self.name = "test scene"
        self.clip_slots = []
        self.is_triggered = False

    def fire(self):
        self.is_triggered = True
        for clip_slot in self.clip_slots:
            clip_slot.fire()
