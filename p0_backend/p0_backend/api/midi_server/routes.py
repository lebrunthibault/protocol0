from time import sleep
from typing import List, Dict

import requests

from p0_backend.api.midi_server.main import stop_midi_server
from p0_backend.api.settings import Settings
from p0_backend.gui.celery import select_window, notification_window
from p0_backend.lib.ableton.ableton import (
    reload_ableton,
    clear_arrangement,
    save_set,
    hide_plugins,
    show_plugins,
)
from p0_backend.lib.ableton.analyze_clip_jitter import analyze_test_audio_clip_jitter
from p0_backend.lib.ableton.automation import set_envelope_loop_length
from p0_backend.lib.ableton.external_synth_track import activate_rev2_editor, post_activate_rev2_editor
from p0_backend.lib.ableton.interface.browser import preload_sample_category
from p0_backend.lib.ableton.interface.clip import set_clip_file_path, crop_clip
from p0_backend.lib.ableton.interface.sample import load_sample_in_simpler
from p0_backend.lib.ableton.interface.toggle_ableton_button import toggle_ableton_button
from p0_backend.lib.ableton.interface.track import flatten_track, load_instrument_track
from p0_backend.lib.ableton.set_profiling.ableton_set_profiler import AbletonSetProfiler
from p0_backend.lib.ableton_set import AbletonSet
from p0_backend.lib.decorators import throttle
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.explorer import close_samples_windows, close_explorer_window
from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import click, click_vertical_zone, move_to

settings = Settings()


class Routes:
    def ping(self):
        AbletonSetProfiler.end_measurement()

    def notify_set_state(self, set_data: Dict):
        # forward to http server
        requests.post(f"{settings.http_api_url}/set", data=AbletonSet(**set_data).json())

    def close_set(self, id: str):
        requests.delete(f"{settings.http_api_url}/set/{id}")

    def search(self, search: str):
        send_keys("^f")
        sleep(0.1)
        send_keys(search)

    def show_sample_category(self, category: str):
        preload_sample_category(category)

    def click_focused_track(self):
        requests.get(f"{settings.http_api_url}/click_focused_track")

    def tail_logs(self):
        requests.get(f"{settings.http_api_url}/tail_logs")

    def save_track_to_sub_tracks(self):
        requests.get(f"{settings.http_api_url}/save_track_to_sub_tracks")

    def drag_matching_track(self):
        requests.get(f"{settings.http_api_url}/drag_matching_track")

    def show_saved_tracks(self):
        requests.get(f"{settings.http_api_url}/show_saved_tracks")

    def delete_saved_track(self, track_name: str):
        requests.get(f"{settings.http_api_url}/delete_saved_track/{track_name}")

    def flatten_track(self):
        flatten_track()

    def crop_clip(self):
        crop_clip()

    def move_to(self, x: int, y: int):
        move_to((x, y))

    def click(self, x: int, y: int):
        click((x, y))

    def click_vertical_zone(self, x: int, y: int):
        click_vertical_zone((x, y))

    def select_and_copy(self):
        send_keys("^a")
        send_keys("^c")

    def select_and_paste(self):
        send_keys("^a")
        send_keys("^v")

    def analyze_test_audio_clip_jitter(self, clip_path: str):
        analyze_test_audio_clip_jitter(clip_path=clip_path)

    def show_plugins(self):
        show_plugins()

    def show_hide_plugins(self):
        send_keys("^%p")

    def hide_plugins(self):
        hide_plugins()

    def reload_ableton(self):
        reload_ableton()

    def save_set(self):
        save_set()

    def clear_arrangement(self):
        clear_arrangement()

    def toggle_ableton_button(self, x: int, y: int, activate: bool = False):
        toggle_ableton_button((x, y), activate=activate)

    def load_instrument_track(self, instrument_name: str):
        load_instrument_track(instrument_name)

    def load_sample_in_simpler(self, sample_path: str):
        load_sample_in_simpler(sample_path)

    def set_clip_file_path(self, file_path: str):
        set_clip_file_path(file_path)

    def set_envelope_loop_length(self, length: int):
        set_envelope_loop_length(length)

    def activate_rev2_editor(self):
        activate_rev2_editor()

    def post_activate_rev2_editor(self):
        post_activate_rev2_editor()

    def start_set_profiling(self):
        AbletonSetProfiler.start_set_profiling()

    def start_profiling_single_measurement(self):
        AbletonSetProfiler.start_profiling_single_measurement()

    def stop_midi_server(self):
        stop_midi_server()

    def close_samples_windows(self):
        close_samples_windows()

    def close_explorer_window(self, title: str):
        close_explorer_window(title)

    def show_info(self, message: str, centered: bool = False):
        notification_window.delay(message, NotificationEnum.INFO.value, centered)

    def show_success(self, message: str, centered: bool = False):
        notification_window.delay(message, NotificationEnum.SUCCESS.value, centered)

    def show_warning(self, message: str, centered: bool = False):
        notification_window.delay(message, NotificationEnum.WARNING.value, centered)

    @throttle(milliseconds=5000)
    def show_error(self, message: str):
        notification_window.delay(message, NotificationEnum.ERROR.value, centered=True)

    def select(
        self,
        question: str,
        options: List,
        vertical: bool = True,
        color: str = NotificationEnum.INFO.value,
    ):
        select_window.delay(question, options, vertical, color)
