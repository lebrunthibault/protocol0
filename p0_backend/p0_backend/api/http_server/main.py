""" http / websocket gateway server to the midi server. Hit by ahk and the stream deck. """
import asyncio
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
from starlette.staticfiles import StaticFiles

from p0_backend.lib.notification import notify
from p0_backend.settings import Settings

load_dotenv()

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.http_server.routes.routes import router  # noqa
from p0_backend.api.http_server.ws import ws_router  # noqa
from protocol0.application.command.GetSetStateCommand import GetSetStateCommand  # noqa

settings = Settings()

app = FastAPI(debug=True, title="p0_backend", version="1.0.0")

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


async def _get_state():
    """Delaying so the http and midi servers are up to receive set data"""
    await asyncio.sleep(2)
    p0_script_client().dispatch(GetSetStateCommand())


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(_get_state())


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
    uvicorn.run(
        "p0_backend.api.http_server.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_config="p0_backend/api/http_server/logging-config.yaml",
        reload_dirs=settings.project_directory,
        workers=1,
    )
