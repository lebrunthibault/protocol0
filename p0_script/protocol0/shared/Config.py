import os
from os.path import dirname, realpath

import Live

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
    # DEFAULT_RECORDING_BAR_LENGTH = RecordingBarLengthEnum.EIGHT

    EXPERIMENTAL_FEATURES = False

    LOG_LEVEL = LogLevelEnum.DEV

    TRACK_VOLUME_MONITORING = False

    DEFAULT_WARP_MODE = Live.Clip.WarpMode.beats

    CLIP_MAX_LENGTH = 63072000

    # VOLUME CONSTANTS
    ZERO_VOLUME = 0.850000023842
    ZERO_VOLUME_DB = -60.9928
    CLIPPING_TRACK_VOLUME = 0.91

    DUMMY_CLIP_NAME = "dummy clip"

    FX_TRACK_NAMES = ("riser", "exhaust", "transition", "roll")
