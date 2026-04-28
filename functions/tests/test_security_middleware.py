from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app import app as production_app
from src.middleware.security import (
    SECURITY_HEADERS,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)


def test_security_headers_are_attached_to_health() -> None:
    client = TestClient(production_app)
    response = client.get("/health")
    assert response.status_code == 200
    for key, value in SECURITY_HEADERS:
        header_name = key.decode("ascii")
        assert header_name in response.headers
        assert response.headers[header_name] == value.decode("ascii")


def test_security_headers_present_on_timeline_endpoint() -> None:
    client = TestClient(production_app)
    response = client.get("/assistant/timeline")
    assert response.status_code == 200
    assert "content-security-policy" in response.headers
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_rate_limit_blocks_excess_requests() -> None:
    test_app = FastAPI()

    @test_app.post("/assistant/chat")
    async def chat() -> dict[str, str]:
        return {"ok": "true"}

    test_app.add_middleware(SecurityHeadersMiddleware)
    test_app.add_middleware(
        RateLimitMiddleware,
        window_seconds=60,
        max_requests=3,
        protected_prefixes=("/assistant/chat",),
    )

    client = TestClient(test_app)
    for _ in range(3):
        response = client.post("/assistant/chat", json={})
        assert response.status_code == 200

    blocked = client.post("/assistant/chat", json={})
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "60"


def test_rate_limit_does_not_apply_to_unprotected_paths() -> None:
    test_app = FastAPI()

    @test_app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    test_app.add_middleware(
        RateLimitMiddleware,
        window_seconds=60,
        max_requests=1,
        protected_prefixes=("/assistant/chat",),
    )

    client = TestClient(test_app)
    for _ in range(5):
        assert client.get("/health").status_code == 200
