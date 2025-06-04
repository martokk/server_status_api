import uvicorn

from app import logger


def start_server() -> None:
    """
    Start Uvicorn server using the configuration from settings.
    """
    logger.debug("Starting uvicorn server...")
    uvicorn.run(
        "app.core.app:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        workers=1,
        app_dir="",
    )
