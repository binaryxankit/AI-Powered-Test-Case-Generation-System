"""Request-id middleware.

Adds a unique ``X-Request-ID`` header to every response and stores the
same value on ``request.state.request_id`` so exception handlers and
custom logging can correlate events for a single request.
"""
from __future__ import annotations

import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "X-Request-ID"


def _generate_request_id() -> str:
    """Return a short, unique request identifier."""
    return uuid.uuid4().hex[:16]


class RequestIDMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that propagates an inbound or generated request id."""

    def __init__(self, app: ASGIApp, header: str = REQUEST_ID_HEADER) -> None:
        super().__init__(app)
        self._header = header

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        incoming = request.headers.get(self._header)
        request_id = incoming.strip() if incoming else _generate_request_id()
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[self._header] = request_id
        return response
