class PresetProgramSelectedEvent(object):
    def __init__(self, preset_index: int) -> None:
        self.preset_index = preset_index
