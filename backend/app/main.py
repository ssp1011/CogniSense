"""
CogniSense — FastAPI Application Factory.

Creates and configures the FastAPI application instance with middleware,
CORS, routers, and startup/shutdown event handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import setup_logging
from app.api.v1.router import api_v1_router
from app.db.engine import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL, settings.LOG_DIR)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Multimodal Cognitive Load Detection System — "
            "Real-time cognitive load estimation using behavioral, "
            "visual, and audio biometrics."
        ),
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
