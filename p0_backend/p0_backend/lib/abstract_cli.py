import asyncclick as click
from loguru import logger

from p0_backend.lib.log import configure_logging


@click.group()
async def cli() -> None:
    configure_logging()
    logger.info("launching cli command")
