"""ASGI middleware that hardens responses with CSP and other headers.

The middleware writes a strict, defence-in-depth header set on every API
response. The :class:`RateLimitMiddleware` companion implements a sliding
window per-client limiter to cap chat / search abuse from a single IP.
"""

from __future__ import annotations

import time
import asyncio
from collections import deque
from collections.abc import Callable, Iterable, Awaitable, MutableMapping

from starlette.types import Send, Scope, ASGIApp, Message, Receive

SECURITY_HEADERS: tuple[tuple[bytes, bytes], ...] = (
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (
        b"permissions-policy",
        (
            b"geolocation=(self), microphone=(), camera=(), payment=()"
        ),
    ),
    (b"cross-origin-opener-policy", b"same-origin"),
    (b"cross-origin-resource-policy", b"same-origin"),
    (
        b"strict-transport-security",
        b"max-age=31536000; includeSubDomains; preload",
    ),
    (
        b"content-security-policy",
        (
            b"default-src 'self'; script-src 'self'; style-src 'self' "
            b"'unsafe-inline'; img-src 'self' data: https:; font-src "
            b"'self' data:; connect-src 'self' "
            b"https://generativelanguage.googleapis.com "
            b"https://maps.googleapis.com; frame-ancestors 'none'; "
            b"base-uri 'self'; form-action 'self'"
        ),
    ),
)


class SecurityHeadersMiddleware:
    """Inject CSP and other hardening headers on every response.

    The middleware is intentionally implemented at the ASGI layer so it
    runs ahead of CORS rewriting and so it can apply to every router and
    static-asset response without per-handler boilerplate.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Wrap an ASGI application with the security headers middleware."""
        self._app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """ASGI entry point that injects security headers on the response."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        async def _send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {key.lower() for key, _ in headers}
                for key, value in SECURITY_HEADERS:
                    if key not in existing:
                        headers.append((key, value))
                message["headers"] = headers
            await send(message)

        await self._app(scope, receive, _send_with_headers)


class RateLimitMiddleware:
    """Per-IP sliding-window rate limiter for chat & search routes.

    The middleware is in-memory only — sufficient for a single instance and
    deterministic in tests. Production should swap this for a Redis-backed
    implementation when scaled to multiple replicas.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        window_seconds: int = 60,
        max_requests: int = 30,
        protected_prefixes: Iterable[str] = (
            "/assistant/chat",
            "/candidate/search",
            "/booth/nearby",
        ),
    ) -> None:
        """Wrap ``app`` with a sliding-window per-IP rate limiter."""
        self._app = app
        self._window_seconds = window_seconds
        self._max_requests = max_requests
        self._protected_prefixes = tuple(protected_prefixes)
        self._buckets: dict[str, deque[float]] = {}
        self._lock = asyncio.Lock()

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """ASGI entry point enforcing the rate-limit on protected routes."""
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        path = scope.get("path", "")
        if not any(path.startswith(prefix) for prefix in self._protected_prefixes):
            await self._app(scope, receive, send)
            return

        client_ip = _extract_client_ip(scope)
        if await self._is_rate_limited(client_ip):
            await _send_429(send)
            return

        await self._app(scope, receive, send)

    async def _is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self._window_seconds
        async with self._lock:
            bucket = self._buckets.setdefault(client_ip, deque())
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self._max_requests:
                return True
            bucket.append(now)
        return False


def _extract_client_ip(scope: Scope) -> str:
    headers: MutableMapping[bytes, bytes] = dict(scope.get("headers", []))
    forwarded = headers.get(b"x-forwarded-for")
    if forwarded:
        return forwarded.decode("latin-1").split(",")[0].strip()
    client = scope.get("client")
    if client:
        return str(client[0])
    return "unknown"


async def _send_429(send: Send) -> None:
    body = b'{"detail":"Too many requests. Please slow down."}'
    headers: list[tuple[bytes, bytes]] = [
        (b"content-type", b"application/json"),
        (b"retry-after", b"60"),
        (b"content-length", str(len(body)).encode("ascii")),
    ]
    headers.extend(SECURITY_HEADERS)
    await send(
        {
            "type": "http.response.start",
            "status": 429,
            "headers": headers,
        }
    )
    await send(
        {"type": "http.response.body", "body": body, "more_body": False}
    )


SendCallable = Callable[[Message], Awaitable[None]]
