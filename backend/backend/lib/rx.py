from typing import Any

from loguru import logger


def rx_error(val: Any) -> None:
    logger.exception(val)


def rx_nop(*_):
    pass
