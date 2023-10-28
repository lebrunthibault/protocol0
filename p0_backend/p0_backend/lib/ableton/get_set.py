import os
import re
from typing import List

from p0_backend.lib.window.find_window import get_windows_list
from p0_backend.settings import Settings

settings = Settings()


def get_ableton_window_titles() -> List[str]:
    set_infos = filter(lambda i: i["app_name"] == settings.ableton_process_name, get_windows_list())

    return [i["name"] for i in set_infos]


def get_launched_set_path() -> str:
    launched_set = next(w for w in get_ableton_window_titles() if "ableton projects" in w)

    set_title = re.match(r"([^*]*)", launched_set).group(1).split(" [")[0].strip()

    file_paths = []

    filename = f"{set_title}.als"

    for root, _, files in os.walk(settings.ableton_set_directory):
        for file in files:
            if file == filename:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    assert len(file_paths) <= 1, f"Duplicate sets found : '{filename}' : {file_paths}"
    assert len(file_paths) == 1, f"Couldn't find '{filename}' in {settings.ableton_set_directory}"

    return file_paths[0]
