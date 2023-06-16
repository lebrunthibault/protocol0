class RecordStartedEvent(object):
    def __init__(self, scene_index: int, full_record: bool, has_count_in: bool) -> None:
        self.scene_index = scene_index
        self.full_record = full_record
        self.has_count_in = has_count_in
