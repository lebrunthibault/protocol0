from typing import Optional

from protocol0.application.command.SerializableCommand import SerializableCommand


class ToggleReferenceTrackFiltersCommand(SerializableCommand):
    def __init__(self, filter_preset: Optional[str] = None):
        super(ToggleReferenceTrackFiltersCommand, self).__init__()
        self.filter_preset = filter_preset
