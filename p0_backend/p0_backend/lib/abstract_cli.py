import asyncclick as click
from loguru import logger

from p0_backend.lib.log import configure_logging
from p0_backend.lib.terminal import clear_terminal


@click.group()
async def cli() -> None:
    configure_logging()
    clear_terminal()
    logger.info("launching cli command")
