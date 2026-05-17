""" http / websocket gateway server. Hit by ahk, the stream deck, and the Ableton remote script. """
import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager

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
from starlette.staticfiles import StaticFiles

from p0_backend.lib.notification import notify
from p0_backend.settings import Settings

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
        target.propagate = False

from p0_backend.api.http_server.routes.routes import router  # noqa
from p0_backend.api.http_server.ws import ws_router  # noqa
from p0_backend.api.client.p0_script_api_client import p0_script_client

settings = Settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        p0_script_client().get_set_state()
    except Exception as e:
        logger.warning(f"lifespan get_set_state failed: {e}")
    yield


app = FastAPI(lifespan=lifespan, debug=True, title="p0_backend", version="1.0.0")

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
app.include_router(ws_router)


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

            if request.method != "PUT":
                notify(str(e))

        return PlainTextResponse(str(e), status_code=500)


"""
Simplify operation IDs so that generated API clients have simpler function
names.

Should be called only after all routes have been added.
"""
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name

app.mount("/static", StaticFiles(directory=settings.ableton_set_directory), name="static")


def start():
    _configure_logging()
    uvicorn.run(
        "p0_backend.api.http_server.main:app",
        host="0.0.0.0",
        port=Settings().p0_backend_port,
        log_config="p0_backend/api/http_server/logging-config.yaml",
        workers=1,
    )
