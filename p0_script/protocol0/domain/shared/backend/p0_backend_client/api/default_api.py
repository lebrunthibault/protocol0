# coding: utf-8

"""
    p0_backend

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import absolute_import

import json


# noinspection Mypy,DuplicatedCode
class P0BackendClient(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, send_midi):
        self._send_midi = send_midi

    def _send_dict_as_midi(self, dict):
        # type: (dict) -> None
        message = json.dumps(dict)
        b = bytearray(message.encode())
        b.insert(0, 0xF0)
        b.append(0xF7)
        self._send_midi(tuple(b))

    def actions(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Actions  # noqa: E501
        """

        payload = {"method": "GET", "path": "/actions", "params": {}}

        self._send_dict_as_midi(payload)

    def active_set(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Active Set  # noqa: E501
        """

        payload = {"method": "GET", "path": "/set/active", "params": {}}

        self._send_dict_as_midi(payload)

    def add_track_to_selection(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Add Track To Selection  # noqa: E501
        """

        payload = {"method": "GET", "path": "/track/add_track_to_selection", "params": {}}

        self._send_dict_as_midi(payload)

    def analyze_test_audio_clip_jitter(
        self,
        clip_path,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Analyze Test Audio Clip Jitter  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/analyze_test_audio_clip_jitter",
            "params": {
                "clip_path": clip_path,
            },
        }

        self._send_dict_as_midi(payload)

    def arm(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Arm  # noqa: E501
        """

        payload = {"method": "GET", "path": "/track/arm", "params": {}}

        self._send_dict_as_midi(payload)

    def capture_midi(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Capture Midi  # noqa: E501
        """

        payload = {"method": "GET", "path": "/record/capture_midi", "params": {}}

        self._send_dict_as_midi(payload)

    def capture_midi_validate(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Capture Midi Validate  # noqa: E501
        """

        payload = {"method": "GET", "path": "/record/capture_midi/validate", "params": {}}

        self._send_dict_as_midi(payload)

    def clear_muted_notes(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Clear Muted Notes  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/clear_muted_notes", "params": {}}

        self._send_dict_as_midi(payload)

    def clear_state(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Clear State  # noqa: E501
        """

        payload = {"method": "POST", "path": "/set/clear_state", "params": {}}

        self._send_dict_as_midi(payload)

    def click(
        self,
        x,
        y,
    ):  # noqa: E501
        # type: (int, int, ) -> None
        """
        Click  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/keyboard/click",
            "params": {
                "x": x,
                "y": y,
            },
        }

        self._send_dict_as_midi(payload)

    def click_vertical_zone(
        self,
        x,
        y,
    ):  # noqa: E501
        # type: (int, int, ) -> None
        """
        Click Vertical Zone  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/keyboard/click_vertical_zone",
            "params": {
                "x": x,
                "y": y,
            },
        }

        self._send_dict_as_midi(payload)

    def close_explorer_window(
        self,
        title,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Close Explorer Window  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/close_explorer_window",
            "params": {
                "title": title,
            },
        }

        self._send_dict_as_midi(payload)

    def close_samples_windows(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Close Samples Windows  # noqa: E501
        """

        payload = {"method": "GET", "path": "/close_samples_windows", "params": {}}

        self._send_dict_as_midi(payload)

    def close_set(
        self,
        filename,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Close Set  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/set/close",
            "params": {
                "filename": filename,
            },
        }

        self._send_dict_as_midi(payload)

    def collapse_selected(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Collapse Selected  # noqa: E501
        """

        payload = {"method": "GET", "path": "/track/collapse_selected", "params": {}}

        self._send_dict_as_midi(payload)

    def color_clip_with_automation(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Color Clip With Automation  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/color_with_automation", "params": {}}

        self._send_dict_as_midi(payload)

    def crop_clip(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Crop Clip  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/crop", "params": {}}

        self._send_dict_as_midi(payload)

    def delete_track(
        self,
        track_name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Delete Track  # noqa: E501
        """

        payload = {
            "method": "DELETE",
            "path": "/set/track",
            "params": {
                "track_name": track_name,
            },
        }

        self._send_dict_as_midi(payload)

    def drum_rack_to_simpler(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Drum Rack To Simpler  # noqa: E501
        """

        payload = {"method": "GET", "path": "/drum_rack_to_simpler", "params": {}}

        self._send_dict_as_midi(payload)

    def duplicate_scene(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Duplicate Scene  # noqa: E501
        """

        payload = {"method": "GET", "path": "/scene/duplicate", "params": {}}

        self._send_dict_as_midi(payload)

    def edit_automation_value(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Edit Automation Value  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/edit_automation_value", "params": {}}

        self._send_dict_as_midi(payload)

    def execute_action(
        self,
        group_id,
        action_id,
    ):  # noqa: E501
        # type: (int, int, ) -> None
        """
        Execute Action  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/actions/{group_id}/{action_id}",
            "params": {
                "group_id": group_id,
                "action_id": action_id,
            },
        }

        self._send_dict_as_midi(payload)

    def export(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Export  # noqa: E501
        """

        payload = {"method": "GET", "path": "/export/", "params": {}}

        self._send_dict_as_midi(payload)

    def export_audio(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Export Audio  # noqa: E501
        """

        payload = {"method": "GET", "path": "/export/audio", "params": {}}

        self._send_dict_as_midi(payload)

    def fire_scene_to_last_position(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Fire Scene To Last Position  # noqa: E501
        """

        payload = {"method": "GET", "path": "/scene/fire_to_last_position", "params": {}}

        self._send_dict_as_midi(payload)

    def fire_scene_to_position(self, bar_length):  # noqa: E501
        # type: (int, ) -> None
        """
        Fire Scene To Position  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/scene/fire_to_position",
            "params": {
                "bar_length": bar_length,
            },
        }

        self._send_dict_as_midi(payload)

    def fire_selected_scene(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Fire Selected Scene  # noqa: E501
        """

        payload = {"method": "GET", "path": "/scene/fire_selected", "params": {}}

        self._send_dict_as_midi(payload)

    def flatten_track(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Flatten Track  # noqa: E501
        """

        payload = {"method": "GET", "path": "/track/flatten", "params": {}}

        self._send_dict_as_midi(payload)

    def freeze_track(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Freeze Track  # noqa: E501
        """

        payload = {"method": "GET", "path": "/track/freeze", "params": {}}

        self._send_dict_as_midi(payload)

    def get_connections(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Get Connections  # noqa: E501
        """

        payload = {"method": "GET", "path": "/ws/connections", "params": {}}

        self._send_dict_as_midi(payload)

    def hide_plugins(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Hide Plugins  # noqa: E501
        """

        payload = {"method": "GET", "path": "/hide_plugins", "params": {}}

        self._send_dict_as_midi(payload)

    def home(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Home  # noqa: E501
        """

        payload = {"method": "GET", "path": "/", "params": {}}

        self._send_dict_as_midi(payload)

    def load_device(
        self,
        name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Load Device  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/device/load",
            "params": {
                "name": name,
            },
        }

        self._send_dict_as_midi(payload)

    def load_instrument_track(
        self,
        instrument_name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Load Instrument Track  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/track/load_instrument_track",
            "params": {
                "instrument_name": instrument_name,
            },
        }

        self._send_dict_as_midi(payload)

    def load_sample_in_simpler(
        self,
        sample_path,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Load Sample In Simpler  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/load_sample_in_simpler",
            "params": {
                "sample_path": sample_path,
            },
        }

        self._send_dict_as_midi(payload)

    def log_selected(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Log Selected  # noqa: E501
        """

        payload = {"method": "GET", "path": "/log_selected", "params": {}}

        self._send_dict_as_midi(payload)

    def log_song_stats(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Log Song Stats  # noqa: E501
        """

        payload = {"method": "GET", "path": "/log_song_stats", "params": {}}

        self._send_dict_as_midi(payload)

    def loop_selected(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Loop Selected  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/loop_selected", "params": {}}

        self._send_dict_as_midi(payload)

    def measure_cpu_usage(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Measure Cpu Usage  # noqa: E501
        """

        payload = {"method": "GET", "path": "/process/measure_cpu_usage", "params": {}}

        self._send_dict_as_midi(payload)

    def move_loop(self, forward, bar):  # noqa: E501
        # type: (bool, bool, ) -> None
        """
        Move Loop  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/clip/move_loop",
            "params": {
                "forward": forward,
                "bar": bar,
            },
        }

        self._send_dict_as_midi(payload)

    def move_to(
        self,
        x,
        y,
    ):  # noqa: E501
        # type: (int, int, ) -> None
        """
        Move To  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/keyboard/move_to",
            "params": {
                "x": x,
                "y": y,
            },
        }

        self._send_dict_as_midi(payload)

    def open_in_explorer(
        self,
        path,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Open In Explorer  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/set/open_in_explorer",
            "params": {
                "path": path,
            },
        }

        self._send_dict_as_midi(payload)

    def open_set(
        self,
        path,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Open Set  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/set/open",
            "params": {
                "path": path,
            },
        }

        self._send_dict_as_midi(payload)

    def open_set_by_type(
        self,
        name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Open Set By Type  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/set/open_by_type",
            "params": {
                "name": name,
            },
        }

        self._send_dict_as_midi(payload)

    def ping(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Ping  # noqa: E501
        """

        payload = {"method": "GET", "path": "/ping", "params": {}}

        self._send_dict_as_midi(payload)

    def play_pause(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Play Pause  # noqa: E501
        """

        payload = {"method": "GET", "path": "/play_pause", "params": {}}

        self._send_dict_as_midi(payload)

    def post_current_state(
        self,
        post_current_state_payload,
    ):  # noqa: E501
        # type: (PostCurrentStatePayload, ) -> None
        """
        Post Current State  # noqa: E501
        """

        payload = {
            "method": "POST",
            "path": "/set/current_state",
            "params": {
                "post_current_state_payload": post_current_state_payload,
            },
        }

        self._send_dict_as_midi(payload)

    def post_scene_stats(
        self,
        post_scene_stats_payload,
    ):  # noqa: E501
        # type: (PostSceneStatsPayload, ) -> None
        """
        Post Scene Stats  # noqa: E501
        """

        payload = {
            "method": "POST",
            "path": "/set/scene_stats",
            "params": {
                "post_scene_stats_payload": post_scene_stats_payload,
            },
        }

        self._send_dict_as_midi(payload)

    def prepare_for_soundcloud(
        self,
        path,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Prepare For Soundcloud  # noqa: E501
        """

        payload = {
            "method": "POST",
            "path": "/set/prepare_for_soundcloud",
            "params": {
                "path": path,
            },
        }

        self._send_dict_as_midi(payload)

    def record_unlimited(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Record Unlimited  # noqa: E501
        """

        payload = {"method": "GET", "path": "/record/unlimited", "params": {}}

        self._send_dict_as_midi(payload)

    def reload_ableton(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Reload Ableton  # noqa: E501
        """

        payload = {"method": "GET", "path": "/reload_ableton", "params": {}}

        self._send_dict_as_midi(payload)

    def reload_god_particle(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Reload God Particle  # noqa: E501
        """

        payload = {"method": "GET", "path": "/device/reload_god_particle", "params": {}}

        self._send_dict_as_midi(payload)

    def reload_script(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Reload Script  # noqa: E501
        """

        payload = {"method": "GET", "path": "/reload_script", "params": {}}

        self._send_dict_as_midi(payload)

    def remove_arrangement_muted_clips(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Remove Arrangement Muted Clips  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/remove_arrangement_muted_clips", "params": {}}

        self._send_dict_as_midi(payload)

    def restart_ableton_audio(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Restart Ableton Audio  # noqa: E501
        """

        payload = {"method": "GET", "path": "/audio/restart_ableton_audio", "params": {}}

        self._send_dict_as_midi(payload)

    def save_set(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Save Set  # noqa: E501
        """

        payload = {"method": "GET", "path": "/set/save", "params": {}}

        self._send_dict_as_midi(payload)

    def save_set_as_template(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Save Set As Template  # noqa: E501
        """

        payload = {"method": "GET", "path": "/set/save_as_template", "params": {}}

        self._send_dict_as_midi(payload)

    def scroll_presets(
        self,
        direction,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Scroll Presets  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/scroll_presets",
            "params": {
                "direction": direction,
            },
        }

        self._send_dict_as_midi(payload)

    def scroll_scene_position(
        self,
        direction,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Scroll Scene Position  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/scene/scroll_position",
            "params": {
                "direction": direction,
            },
        }

        self._send_dict_as_midi(payload)

    def scroll_scene_position_fine(
        self,
        direction,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Scroll Scene Position Fine  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/scene/scroll_position_fine",
            "params": {
                "direction": direction,
            },
        }

        self._send_dict_as_midi(payload)

    def scroll_scene_tracks(
        self,
        direction,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Scroll Scene Tracks  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/scene/scroll_tracks",
            "params": {
                "direction": direction,
            },
        }

        self._send_dict_as_midi(payload)

    def scroll_scenes(
        self,
        direction,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Scroll Scenes  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/scene/scroll",
            "params": {
                "direction": direction,
            },
        }

        self._send_dict_as_midi(payload)

    def search(
        self,
        text,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Search  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/keyboard/search",
            "params": {
                "text": text,
            },
        }

        self._send_dict_as_midi(payload)

    def search_track(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Search Track  # noqa: E501
        """

        payload = {"method": "GET", "path": "/search/track", "params": {}}

        self._send_dict_as_midi(payload)

    def select(
        self,
        name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Select  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/track/select",
            "params": {
                "name": name,
            },
        }

        self._send_dict_as_midi(payload)

    def select_and_copy(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Select And Copy  # noqa: E501
        """

        payload = {"method": "GET", "path": "/keyboard/select_and_copy", "params": {}}

        self._send_dict_as_midi(payload)

    def select_and_paste(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Select And Paste  # noqa: E501
        """

        payload = {"method": "GET", "path": "/keyboard/select_and_paste", "params": {}}

        self._send_dict_as_midi(payload)

    def select_clip(
        self,
        track_name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Select Clip  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/clip/select",
            "params": {
                "track_name": track_name,
            },
        }

        self._send_dict_as_midi(payload)

    def serum_bulk_edit(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Serum Bulk Edit  # noqa: E501
        """

        payload = {"method": "GET", "path": "/device/serum_bulk_edit", "params": {}}

        self._send_dict_as_midi(payload)

    def set_clip_file_path(
        self,
        file_path,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Set Clip File Path  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/clip/set_file_path",
            "params": {
                "file_path": file_path,
            },
        }

        self._send_dict_as_midi(payload)

    def set_envelope_loop_length(
        self,
        length,
    ):  # noqa: E501
        # type: (int, ) -> None
        """
        Set Envelope Loop Length  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/set_envelope_loop_length",
            "params": {
                "length": length,
            },
        }

        self._send_dict_as_midi(payload)

    def set_loop_length(
        self,
        bar_length,
    ):  # noqa: E501
        # type: (int, ) -> None
        """
        Set Loop Length  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/clip/set_loop_length",
            "params": {
                "bar_length": bar_length,
            },
        }

        self._send_dict_as_midi(payload)

    def show_automation(
        self,
        direction,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Show Automation  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/clip/show_automation",
            "params": {
                "direction": direction,
            },
        }

        self._send_dict_as_midi(payload)

    def show_error(
        self,
        message,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Show Error  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/show_error",
            "params": {
                "message": message,
            },
        }

        self._send_dict_as_midi(payload)

    def show_hide_plugins(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Show Hide Plugins  # noqa: E501
        """

        payload = {"method": "GET", "path": "/show_hide_plugins", "params": {}}

        self._send_dict_as_midi(payload)

    def show_info(
        self,
        message,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Show Info  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/show_info",
            "params": {
                "message": message,
            },
        }

        self._send_dict_as_midi(payload)

    def show_instrument(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Show Instrument  # noqa: E501
        """

        payload = {"method": "GET", "path": "/show_instrument", "params": {}}

        self._send_dict_as_midi(payload)

    def show_plugins(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Show Plugins  # noqa: E501
        """

        payload = {"method": "GET", "path": "/show_plugins", "params": {}}

        self._send_dict_as_midi(payload)

    def show_success(
        self,
        message,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Show Success  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/show_success",
            "params": {
                "message": message,
            },
        }

        self._send_dict_as_midi(payload)

    def show_warning(
        self,
        message,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Show Warning  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/show_warning",
            "params": {
                "message": message,
            },
        }

        self._send_dict_as_midi(payload)

    def solo(self, solo_type, bus_name):  # noqa: E501
        # type: (str, str, ) -> None
        """
        Solo  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/monitoring/solo",
            "params": {
                "solo_type": solo_type,
                "bus_name": bus_name,
            },
        }

        self._send_dict_as_midi(payload)

    def start_profiling_single_measurement(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Start Profiling Single Measurement  # noqa: E501
        """

        payload = {"method": "GET", "path": "/start_profiling_single_measurement", "params": {}}

        self._send_dict_as_midi(payload)

    def start_set_profiling(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Start Set Profiling  # noqa: E501
        """

        payload = {"method": "GET", "path": "/start_set_profiling", "params": {}}

        self._send_dict_as_midi(payload)

    def tail_logs(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Tail Logs  # noqa: E501
        """

        payload = {"method": "GET", "path": "/tail_logs", "params": {}}

        self._send_dict_as_midi(payload)

    def tail_logs_raw(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Tail Logs Raw  # noqa: E501
        """

        payload = {"method": "GET", "path": "/tail_logs_raw", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_ableton_button(self, x, y, activate):  # noqa: E501
        # type: (int, int, bool, ) -> None
        """
        Toggle Ableton Button  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/toggle_ableton_button",
            "params": {
                "x": x,
                "y": y,
                "activate": activate,
            },
        }

        self._send_dict_as_midi(payload)

    def toggle_bus(
        self,
        bus_name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Toggle Bus  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/monitoring/toggle_bus",
            "params": {
                "bus_name": bus_name,
            },
        }

        self._send_dict_as_midi(payload)

    def toggle_clip(
        self,
        track_name,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Toggle Clip  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/clip/toggle",
            "params": {
                "track_name": track_name,
            },
        }

        self._send_dict_as_midi(payload)

    def toggle_clip_notes(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Clip Notes  # noqa: E501
        """

        payload = {"method": "GET", "path": "/clip/toggle_notes", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_cpu_heavy(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Cpu Heavy  # noqa: E501
        """

        payload = {"method": "GET", "path": "/device/toggle_cpu_heavy", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_ext_out(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Ext Out  # noqa: E501
        """

        payload = {"method": "GET", "path": "/monitoring/toggle_ext_out", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_mono(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Mono  # noqa: E501
        """

        payload = {"method": "GET", "path": "/monitoring/toggle_mono", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_rack_chain(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Rack Chain  # noqa: E501
        """

        payload = {"method": "GET", "path": "/device/toggle_rack_chain", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_reference(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Reference  # noqa: E501
        """

        payload = {"method": "GET", "path": "/monitoring/toggle_reference", "params": {}}

        self._send_dict_as_midi(payload)

    def toggle_reference_filters(self, preset):  # noqa: E501
        # type: (str, ) -> None
        """
        Toggle Reference Filters  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/monitoring/toggle_reference_filters",
            "params": {
                "preset": preset,
            },
        }

        self._send_dict_as_midi(payload)

    def toggle_reference_stereo_mode(
        self,
        stereo_mode,
    ):  # noqa: E501
        # type: (str, ) -> None
        """
        Toggle Reference Stereo Mode  # noqa: E501
        """

        payload = {
            "method": "GET",
            "path": "/monitoring/toggle_reference_stereo_mode",
            "params": {
                "stereo_mode": stereo_mode,
            },
        }

        self._send_dict_as_midi(payload)

    def toggle_scene_loop(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Toggle Scene Loop  # noqa: E501
        """

        payload = {"method": "GET", "path": "/scene/toggle_loop", "params": {}}

        self._send_dict_as_midi(payload)

    def un_group(
        self,
    ):  # noqa: E501
        # type: () -> None
        """
        Un Group  # noqa: E501
        """

        payload = {"method": "GET", "path": "/track/un_group", "params": {}}

        self._send_dict_as_midi(payload)
