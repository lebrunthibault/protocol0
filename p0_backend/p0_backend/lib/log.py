import json
import sys

from loguru import logger

from p0_backend.api.settings import Settings


def configure_logging() -> None:
    with open(f"{Settings().project_directory}/lib/logging_config.json") as config_file:
        logging_config = json.load(config_file)

    logger.remove()
    logger.add(
        sys.stdout,
        level=logging_config.get("level"),
        format=logging_config.get("format_stdout"),
    )
