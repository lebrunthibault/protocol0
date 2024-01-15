import os
import re
from typing import List

from loguru import logger

from p0_backend.lib.window.find_window import get_windows_list
from p0_backend.settings import Settings

settings = Settings()


def get_ableton_window_titles() -> List[str]:
    set_infos = filter(lambda i: i["app_name"] == settings.ableton_process_name, get_windows_list())

    return [i["name"] for i in set_infos]


def get_launched_set_path() -> str:
    windows = get_ableton_window_titles()
    launched_set = next((w for w in windows if "ableton projects" in w), None)

    assert launched_set, f"Couldn't find launched set in {windows}"

    set_title = re.match(r"([^*]*)", launched_set).group(1).split(" [")[0].strip()

    file_paths = []

    set_filename = f"{set_title}.als"

    for root, _, files in os.walk(settings.ableton_set_directory):
        for file in files:
            if file == set_filename:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
            elif file == set_title:
                logger.info(f"found folder {file}")

    assert len(file_paths) <= 1, f"Duplicate sets found : '{set_filename}' : {file_paths}"
    assert (
        len(file_paths) == 1
    ), f"Couldn't find '{set_filename}' in {settings.ableton_set_directory}"

    return file_paths[0]
