""" http / websocket server. """
import logging
import os
import sys
import traceback

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from loguru import logger
from ratelimit import RateLimitException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from backend.settings import Settings
from backend.version import __version__

load_dotenv()


class _InterceptHandler(logging.Handler):
    """Forward stdlib logging records (uvicorn, etc.) into loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def _configure_logging() -> None:
    """Route uvicorn/stdlib + loguru into a single rotating log file.

    Active only when P0_LOG_FILE is set (the scheduled-task launcher sets it);
    `poetry run backend` in a terminal keeps its plain stderr behavior.
    """
    log_file = os.environ.get("P0_LOG_FILE")
    if not log_file:
        return

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(log_file, rotation="10 MB", retention=5, level="INFO", enqueue=True)

    intercept = _InterceptHandler()
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        target = logging.getLogger(name)
        target.handlers = [intercept]
        target.setLevel(logging.INFO)
        target.propagate = False


from backend.api.http_server.routes.routes import router  # noqa

settings = Settings()


app = FastAPI(debug=True, title="backend", version=__version__)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: Exception):
    """Have verbose errors"""
    logger.info(str(exc))
    return PlainTextResponse(str(exc), status_code=400)


@app.middleware("http")
async def _catch_protocol0_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        if not isinstance(e, RateLimitException):
            traceback.print_tb(e.__traceback__)
            logger.error(e)

        return PlainTextResponse(str(e), status_code=500)


"""
Simplify operation IDs so that generated API clients have simpler function
names.

Should be called only after all routes have been added.
"""
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name


def start():
    _configure_logging()
    log_file = os.environ.get("P0_LOG_FILE")
    uvicorn.run(
        "backend.api.http_server.main:app",
        host="0.0.0.0",
        port=Settings().p0_backend_port,
        log_config=None if log_file else "backend/api/http_server/logging-config.yaml",
        workers=1,
    )
