"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.config import get_settings
from backend.database.session import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="AI Test Case Generator API",
    version="1.0.0",
    description="Generate structured software test cases from natural-language requirements.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _on_startup() -> None:
    """Create database tables on startup (idempotent)."""
    init_db()


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Lightweight root response so the server can be pinged from a browser."""
    return {
        "name": "AI Test Case Generator API",
        "docs": "/docs",
        "health": "/api/health",
    }


app.include_router(api_router)
