"""Custom FastAPI exception handlers.

Goal: every error path returns a JSON body shaped like ``{"detail": ...,
"error_id": ...}`` so the frontend can render a consistent message and
operators can correlate logs with the failing request.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _error_response(
    *,
    status_code: int,
    message: str,
    request: Request,
    extra: Dict[str, Any] | None = None,
) -> JSONResponse:
    body: Dict[str, Any] = {"detail": message}
    request_id = getattr(request.state, "request_id", None)
    if request_id:
        body["error_id"] = request_id
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach exception handlers to a FastAPI application instance."""

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        if isinstance(exc.detail, str):
            message = exc.detail
        else:
            message = "Request failed."
        return _error_response(
            status_code=exc.status_code,
            message=message,
            request=request,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        first = errors[0] if errors else {"msg": "Invalid request."}
        location = ".".join(str(p) for p in first.get("loc", [])[1:]) or "body"
        message = f"Invalid `{location}`: {first.get('msg', 'invalid value')}."
        logger.info("Validation error: %s", errors)
        return _error_response(
            status_code=422,
            message=message,
            request=request,
            extra={"errors": errors},
        )

    @app.exception_handler(Exception)
    async def _unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _error_response(
            status_code=500,
            message="An unexpected error occurred. Please try again.",
            request=request,
        )
