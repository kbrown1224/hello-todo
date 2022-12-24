import logging
import textwrap

from loguru import logger
from rich.console import Console
from uvicorn import Config, Server

from api.config import get_settings
from api.logger import init_logging

settings = get_settings()
console = Console(markup=True, emoji=True)


def generate_startup_message():
    """Startup message"""
    return textwrap.dedent(
        r"""
        [bold red]
         ██████╗ █████╗ ██████╗ ██████╗ ███████╗
        ██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
        ██║     ███████║██████╔╝██║  ██║███████╗
        ██║     ██╔══██║██╔══██╗██║  ██║╚════██║
        ╚██████╗██║  ██║██║  ██║██████╔╝███████║
         ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
        [/bold red]
        Welcome to [bold red]Cards[/bold red]! .
        """
    )


if __name__ == "__main__":
    console.print(generate_startup_message())
    console.rule("Starting Web Application")

    server = Server(
        Config(
            "api.main:create_app",
            host=settings.server.HOST,
            port=settings.server.PORT,
            log_level=logging.getLevelName("DEBUG"),
            reload=True,
            factory=True,
        )
    )

    init_logging()
    logger.info(
        "Starting API Docs at http://{host}:{port}/docs",
        host=settings.server.HOST,
        port=settings.server.PORT,
    )

    server.run()

    console.rule("Stopping Web Application")
