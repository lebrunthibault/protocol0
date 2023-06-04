""" http / websocket gateway server to the midi server. Hit by ahk and the stream deck. """
import asyncio
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.errors.Protocol0Error import Protocol0Error

load_dotenv()

from p0_backend.gui.celery import notification_window
from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.http_server.routes import router  # noqa
from p0_backend.api.http_server.ws import ws_router  # noqa
from protocol0.application.command.GetSetStateCommand import GetSetStateCommand  # noqa
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)

app = FastAPI(debug=True)

origins = [
    "http://localhost",
    "http://localhost:5173",
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
async def validation_exception_handler(request, exc: Exception):
    """Have verbose errors"""
    logger.info(str(exc))
    return PlainTextResponse(str(exc), status_code=400)


@app.middleware("http")
async def _catch_protocol0_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(e)
        traceback.print_tb(e.__traceback__)

        notification_level = NotificationEnum.ERROR.value
        if isinstance(e, (Protocol0Error, AssertionError)):
            notification_level = NotificationEnum.WARNING.value

        notification_window.delay(str(e), notification_enum=notification_level, centered=True)

        p0_script_client().dispatch(EmitBackendEventCommand("error"))
        return PlainTextResponse(str(e), status_code=500)


async def _get_state():
    """Delaying so the http and midi servers are up to receive set data"""
    await asyncio.sleep(3)
    p0_script_client().dispatch(GetSetStateCommand())


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(_get_state())
