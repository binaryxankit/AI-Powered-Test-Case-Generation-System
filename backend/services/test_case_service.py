"""Persistence and orchestration layer for test case generations."""
from __future__ import annotations

import logging
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.test_generation import TestGeneration
from backend.schemas.test_case import TestCase, TestGenerationResponse, TestGenerationSummary
from backend.services.gemini_service import GeminiService, GeminiServiceError

logger = logging.getLogger(__name__)


class TestCaseService:
    """High-level operations combining Gemini + the database."""

    def __init__(self, db: Session, gemini: GeminiService | None = None) -> None:
        self._db = db
        self._gemini = gemini

    def generate_and_store(self, requirement: str) -> TestGenerationResponse:
        """Run the model, persist the result, and return the full record."""
        gemini = self._gemini or GeminiService()
        try:
            payload = gemini.generate_test_cases(requirement)
        except GeminiServiceError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected error from Gemini service")
            raise GeminiServiceError(f"Unexpected error: {exc}") from exc

        record = TestGeneration(
            requirement=payload["requirement"],
            generated_output_json=payload,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)

        return self._to_response(record)

    def list_generations(self, limit: int = 100) -> List[TestGenerationSummary]:
        """Return a lightweight list of past generations, newest first."""
        stmt = (
            select(TestGeneration)
            .order_by(TestGeneration.created_at.desc())
            .limit(limit)
        )
        records = self._db.execute(stmt).scalars().all()

        summaries: list[TestGenerationSummary] = []
        for record in records:
            cases = record.generated_output_json.get("test_cases", []) or []
            summaries.append(
                TestGenerationSummary(
                    id=record.id,
                    requirement=record.requirement,
                    created_at=record.created_at,
                    test_case_count=len(cases),
                )
            )
        return summaries

    def get_generation(self, generation_id: int) -> TestGenerationResponse | None:
        """Return a single generation, or ``None`` if not found."""
        record = self._db.get(TestGeneration, generation_id)
        if record is None:
            return None
        return self._to_response(record)

    @staticmethod
    def _to_response(record: TestGeneration) -> TestGenerationResponse:
        """Convert an ORM record into a Pydantic response model."""
        cases = [
            TestCase.model_validate(case)
            for case in record.generated_output_json.get("test_cases", [])
        ]
        return TestGenerationResponse(
            id=record.id,
            requirement=record.requirement,
            test_cases=cases,
            created_at=record.created_at,
        )
