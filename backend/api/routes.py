"""FastAPI route definitions for the test case generator."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.test_case import (
    GenerateRequest,
    HealthResponse,
    TestGenerationResponse,
    TestGenerationSummary,
)
from backend.services.gemini_service import GeminiServiceError
from backend.services.pdf_service import render_pdf
from backend.services.test_case_service import TestCaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["test-cases"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Return a simple health response including DB reachability."""
    from backend.config import get_settings

    settings = get_settings()

    db_status: str = "unknown"
    try:
        from sqlalchemy import text  # local import to avoid pulling when unused

        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:  # noqa: BLE001
        db_status = "unreachable"

    overall: str = "ok" if db_status == "ok" else "degraded"
    return HealthResponse(
        status=overall,  # type: ignore[arg-type]
        version="1.0.0",
        model=settings.gemini_model,
        database=db_status,  # type: ignore[arg-type]
        gemini_key_configured=bool(settings.gemini_api_key),
    )


@router.post(
    "/generate",
    response_model=TestGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate test cases from a requirement",
)
def generate_test_cases(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
) -> TestGenerationResponse:
    """Run the AI model and persist the result."""
    service = TestCaseService(db)
    try:
        return service.generate_and_store(payload.requirement)
    except GeminiServiceError as exc:
        logger.warning("Generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.get(
    "/history",
    response_model=list[TestGenerationSummary],
    summary="List past generations",
)
def list_history(db: Session = Depends(get_db)) -> list[TestGenerationSummary]:
    """Return a list of previously generated test case runs."""
    service = TestCaseService(db)
    return service.list_generations()


@router.get(
    "/history/{generation_id}",
    response_model=TestGenerationResponse,
    summary="Retrieve a single generation",
)
def get_history_item(
    generation_id: int,
    db: Session = Depends(get_db),
) -> TestGenerationResponse:
    """Return one stored generation by ID."""
    service = TestCaseService(db)
    record = service.get_generation(generation_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation {generation_id} not found.",
        )
    return record


@router.get(
    "/history/{generation_id}/pdf",
    summary="Download a PDF report for a generation",
    response_class=Response,
)
def download_pdf(
    generation_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Stream a PDF report of a single generation."""
    service = TestCaseService(db)
    record = service.get_generation(generation_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation {generation_id} not found.",
        )

    pdf_bytes = render_pdf(record)
    filename = f"test-cases-{generation_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )
