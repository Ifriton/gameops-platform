import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings, get_settings
from app.database import Base, build_database
from app.routers.servers import router as servers_router
from app.schemas import StatusResponse

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    logging.basicConfig(
        level=getattr(logging, app_settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    engine, session_factory = build_database(app_settings.database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        Base.metadata.create_all(engine)
        logger.info("GameOps Platform starting", extra={"app_env": app_settings.app_env})
        yield
        engine.dispose()
        logger.info("GameOps Platform stopped")

    application = FastAPI(
        title="GameOps Platform",
        description="Portfolio API for multiplayer game-server inventory and status.",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.state.settings = app_settings
    application.state.engine = engine
    application.state.session_factory = session_factory
    application.include_router(servers_router)

    @application.get("/healthz", response_model=StatusResponse, tags=["health"])
    def health() -> StatusResponse:
        return StatusResponse(status="ok")

    @application.get("/readyz", response_model=StatusResponse, tags=["health"])
    def readiness(request: Request) -> StatusResponse:
        try:
            with request.app.state.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            logger.error("Database readiness check failed", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable",
            ) from exc
        return StatusResponse(status="ready")

    return application


app = create_app()
