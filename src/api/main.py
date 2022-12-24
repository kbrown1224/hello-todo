from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware

from api.cards.routes import router as cards_router
from api.root.routes import router as root_router
from api.database import database
from loguru import logger


def create_app():
    """App factory function"""

    def init_routers(app_: FastAPI):
        """Add all routers to the application"""
        app_.include_router(cards_router, prefix="/api")
        app_.include_router(root_router, prefix="/api")

    def init_middlewares(app_: FastAPI):
        """Add all middlewares to the application"""
        app_.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def init_event_handlers(app_: FastAPI):
        logger.info("Initializing event handlers")

        @app_.on_event("startup")
        async def connect_database():
            logger.info("[bold green]Connecting to database")
            await database.connect()

        @app_.on_event("shutdown")
        async def disconnect_database():
            if database.is_connected:
                logger.info("[bold green]Disconnecting from database")
                await database.disconnect()

    def custom_generate_unique_id(route: APIRoute):
        """Generate unique id for cleaner client names"""
        return route.name

    def tags_metadata():
        """Metadata for our route tags. These show up in the generated docs"""
        return [
            {
                "name": "Cards",
                "description": "Operations for Cards",
            },
        ]

    app = FastAPI(
        title="Cards API",
        version="0.1.0",
        redoc_url=None,
        generate_unique_id_function=custom_generate_unique_id,
        openapi_tags=tags_metadata(),
        description="""
        Service for cards.
        """,
    )

    init_routers(app)
    init_middlewares(app)
    init_event_handlers(app)

    return app
