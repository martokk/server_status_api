from typing import Any

from loguru import logger as _logger

from app.paths import ERROR_LOG_FILE, LOG_FILE


def setup_logger() -> Any:
    """Configure and return the application logger."""

    # Configure loggers for file output
    _logger.add(
        LOG_FILE,
        filter=lambda record: record["extra"].get("name") == "logger",
        level="INFO",
        rotation="10 MB",
    )
    _logger.add(
        ERROR_LOG_FILE,
        filter=lambda record: record["extra"].get("name") == "logger",
        level="ERROR",
        rotation="10 MB",
    )
    # Create bound logger
    logger = _logger.bind(name="logger")
    logger.info("Log level set by .env to 'INFO'")

    return logger
