"""Application factory."""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .config import settings
from .database import init_db
from .routers import admin, attachments, auth, portal, reports, tickets, users
from .services.errors import ServiceError


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    init_db()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title=settings.app_name, version=__version__)

    # The SPA and the marketing site run on several customer-branded domains.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ServiceError)
    async def service_error_handler(_: Request, exc: ServiceError):
        return JSONResponse({"detail": exc.message}, status_code=exc.status_code)

    for module in (auth, users, tickets, attachments, admin, reports, portal):
        app.include_router(module.router)

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok", "version": __version__}

    return app


app = create_app()
