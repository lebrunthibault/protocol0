import os
from typing import List

from loguru import logger

from p0_backend.lib.notification import notify
from p0_backend.lib.ableton.clip_parsing import Clip
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.errors.Protocol0Error import Protocol0Error


def analyze_test_audio_clip_jitter(clip_path: str):
    logger.warning("analyzing %s" % clip_path)
    clip_path = f"{clip_path}.asd"

    if not os.path.exists(clip_path):
        raise Protocol0Error(
            f"{clip_path} does not exist, are analysis files configured in " f"Ableton ?"
        )
    clip = Clip(clip_path, 44100, 44100)
    # NB at 44100 the sample rate induced max jitter is 0.023 ms
    notes_count = 8 - 1

    beat_offsets = _get_beat_offsets(clip, notes_count)
    _process_results(beat_offsets, notes_count)


def _get_beat_offsets(clip: Clip, notes_count: int) -> List[float]:
    # skipping start and end markers, excepting notes_count markers
    warp_markers = [wm for wm in clip.warp_markers if wm.seconds >= 0.125 and wm.seconds <= 1.875][
        0:notes_count
    ]

    if len(warp_markers) != notes_count:
        raise Protocol0Error(
            f"couldn't analyze jitter, got {len(warp_markers)} central warp_markers, expected {notes_count}"
        )

    beat_offsets = []
    # we ignore warp markers set on note end
    # 1 in case the recording started before 1.1.1
    for i, warp_marker in enumerate(warp_markers):
        beat_offsets.append((warp_marker.seconds - (i + 1) * 0.25) * 1000)

    return beat_offsets


def _process_results(beat_offsets: List[float], notes_count: int):
    average_latency = sum(beat_offsets) / notes_count
    total_jitter = sum(abs(b - average_latency) for b in beat_offsets)
    average_jitter = total_jitter / notes_count
    message = f"average jitter {average_jitter:.2f} ms\naverage latency {average_latency:.2f} ms"
    logger.info(message)
    notification_type = NotificationEnum.SUCCESS
    if average_jitter > 1 or average_latency < 0 or average_latency > 1:
        # average_latency < 0 because we cannot have transients clipped
        notification_type = NotificationEnum.WARNING

    notify(message, notification_type)
