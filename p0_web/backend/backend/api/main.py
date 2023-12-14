import traceback

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from loguru import logger
from ratelimit import RateLimitException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles

from backend.api.routes.routes import router
from backend.lib.notification import notify
from backend.settings import Settings, PROJECT_DIRECTORY, SETS_DIRECTORY

settings = Settings()

app = FastAPI(debug=True, title="p0_web_backend", version="1.0.0")

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

            if request.method != "PUT":
                notify(str(e))

        return PlainTextResponse(str(e), status_code=500)


app.mount("/static", StaticFiles(directory=SETS_DIRECTORY), name="static")


def start():
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_config="backend/api/logging-config.yaml",
        reload_dirs=PROJECT_DIRECTORY,
        workers=1,
    )


if __name__ == "__main__":
    start()
