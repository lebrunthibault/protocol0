import os
from os.path import dirname, realpath

from protocol0.domain.track_recorder.recording_bar_length.RecordingBarLengthEnum import (
    RecordingBarLengthEnum,
)
from protocol0.shared.logging.LogLevelEnum import LogLevelEnum


class Config(object):
    # DIRECTORIES
    PROJECT_ROOT = dirname(dirname(realpath(__file__)))
    REMOTE_SCRIPTS_ROOT = dirname(PROJECT_ROOT)
    SAMPLE_DIRECTORY = str(os.getenv("SAMPLE_DIRECTORY"))

    # MISC
    DEFAULT_RECORDING_BAR_LENGTH = RecordingBarLengthEnum.ONE

    LOG_LEVEL = LogLevelEnum.DEV

    CLIP_MAX_LENGTH = 63072000

    DUMMY_CLIP_NAME = "dummy clip"

    FX_TRACK_NAMES = ("riser", "exhaust", "transition", "roll")
