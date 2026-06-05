class SceneFiredEvent(object):
    """Event emitted **before** the scene starts playing"""

    def __init__(self, scene_index: int) -> None:
        self.scene_index = scene_index
