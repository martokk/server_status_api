from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app import logger, version
from app.paths import STATIC_PATH
from app.routes.api import api_router


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for export endpoint
        if request.url.path.endswith("/api/v1/export"):
            return await call_next(request)
        return await call_next(request)


async def startup_event() -> None:
    """
    Event handler that gets called when the application starts.
    Logs application start and creates database and tables if they do not exist.

    Args:
        db (Session): Database session.
    """
    logger.info("--- Start FastAPI ---")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    await startup_event()

    # Start task scheduler
    # task_scheduler = TaskScheduler(app=app)
    # await task_scheduler.register_startup_event()

    yield

    # Shutdown
    # scheduler_task.cancel()
    # with suppress(asyncio.CancelledError):
    # await scheduler_task


# Initialize FastAPI App
app = FastAPI(
    title="Server Status API",
    version=version,
    openapi_url="/openapi.json",
    debug=True,
    lifespan=lifespan,
)

# Add auth middleware that skips export endpoint
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Mount static and uploads directories
STATIC_PATH.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_PATH))
