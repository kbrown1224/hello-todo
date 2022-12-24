import logging
from pprint import pformat

import fastapi
import starlette
import uvicorn
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
from rich.logging import RichHandler


class InterceptHandler(logging.Handler):
    """Loguru logging handler for FastAPI"""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = logging.currentframe()
        depth = 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    """Custom format for loguru loggers"""

    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"],
            indent=4,
            compact=True,
            width=88,
        )
        format_string += "{exception}\n"

        return format_string


def init_logging():
    """Replace default logging handlers with custom handler"""

    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    logger.configure(
        handlers=[
            {
                "sink": RichHandler(
                    markup=True,
                    omit_repeated_times=False,
                    show_level=True,
                    show_path=True,
                    rich_tracebacks=True,
                    tracebacks_suppress=[fastapi, starlette, uvicorn],
                ),
                "level": logging.DEBUG,
                "format": "{message}",
            }
        ]
    )