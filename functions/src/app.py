"""FastAPI application factory for the CivikSutra election coach."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.booth import router as booth_router
from src.api.assistant import router as assistant_router
from src.api.candidate import router as candidate_router
from src.api.manifesto import router as manifesto_router
from src.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)

DEFAULT_ORIGINS: tuple[str, ...] = (
    "http://localhost:5173",
    "http://localhost:5000",
    "https://civiksutra-2604261729.web.app",
    "https://civiksutra-2604261729.firebaseapp.com",
)


def _allowed_origins() -> list[str]:
    raw = os.getenv("EP_CORS_ORIGINS")
    if not raw:
        return list(DEFAULT_ORIGINS)
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or list(DEFAULT_ORIGINS)


def _rate_limit_settings() -> tuple[int, int]:
    try:
        window = int(os.getenv("EP_RATE_LIMIT_WINDOW_SECONDS", "60"))
        max_requests = int(os.getenv("EP_RATE_LIMIT_MAX_REQUESTS", "30"))
    except ValueError:
        window, max_requests = 60, 30
    return window, max_requests


app = FastAPI(
    title="CivikSutra API",
    description="Election process education APIs.",
    version="0.3.0",
)

app.add_middleware(SecurityHeadersMiddleware)

_window, _max_requests = _rate_limit_settings()
app.add_middleware(
    RateLimitMiddleware,
    window_seconds=_window,
    max_requests=_max_requests,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(assistant_router)
app.include_router(booth_router)
app.include_router(candidate_router)
app.include_router(manifesto_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness/readiness probe used by Cloud Run."""
    return {"status": "ok"}
