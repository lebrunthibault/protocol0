class RecordStartedEvent(object):
    def __init__(self, scene_index: int, has_count_in: bool) -> None:
        self.scene_index = scene_index
        self.has_count_in = has_count_in
