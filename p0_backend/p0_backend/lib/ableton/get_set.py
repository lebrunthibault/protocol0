import os.path
import re
from typing import Optional

from loguru import logger

from p0_backend.settings import Settings

settings = Settings()


def get_launched_set_path() -> Optional[str]:
    with open(settings.log_file_path, "r", encoding="utf-8") as f:
        log_content = f.read()

    regex = re.compile(r"AApplication: CommandLine : \"(.+\.als)\"")
    matches = regex.findall(log_content)

    for path in reversed(matches):
        if os.path.exists(path):
            print("Last .als path found:", path)
            return path

    if matches:
        logger.warning(
            f"None of the {len(matches)} .als paths in the log exist on disk "
            f"(most recent: {matches[-1]})"
        )
    else:
        logger.warning("No .als file paths found in the log.")

    return None
