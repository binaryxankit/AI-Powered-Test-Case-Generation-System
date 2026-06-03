"""Persistence and orchestration layer for test case generations."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.test_generation import TestGeneration
from backend.schemas.test_case import TestCase, TestGenerationResponse, TestGenerationSummary
from backend.services.cache import GenerationCache
from backend.services.exceptions import LlmServiceError
from backend.services.gemini_service import GeminiService
from backend.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class TestCaseService:
    """High-level operations combining an LLM provider + the database."""

    def __init__(
        self,
        db: Session,
        llm_provider: Any = None,
        cache: Optional[GenerationCache] = None,
    ) -> None:
        self._db = db
        self._provider = llm_provider
        self._cache = cache or GenerationCache()

    def _resolve_provider(self) -> Any:
        """Return a configured LLM provider based on settings.

        Resolution order (controlled by ``LLM_PROVIDER`` in env):
          - ``"gemini"``  → ``GeminiService`` (raises if no key)
          - ``"ollama"``  → ``OllamaService`` (raises if unreachable)
          - ``"auto"``    → try Gemini, fallback to Ollama
        """
        settings = get_settings()
        choice = settings.llm_provider.lower()

        if choice == "gemini":
            return GeminiService()

        if choice == "ollama":
            return OllamaService()

        # auto: try Gemini first, then Ollama
        if settings.gemini_api_key:
            try:
                return GeminiService()
            except LlmServiceError:
                logger.info("Gemini key found but init failed; falling back to Ollama")

        return OllamaService()

    def generate_and_store(self, requirement: str) -> TestGenerationResponse:
        """Run the model, persist the result, and return the full record."""
        cached = self._cache.get(requirement)
        if cached is not None:
            logger.info("Cache hit for requirement (len=%d)", len(requirement))
            payload = cached
        else:
            provider = self._provider or self._resolve_provider()
            try:
                payload = provider.generate_test_cases(requirement)
            except LlmServiceError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Unexpected error from LLM provider")
                raise LlmServiceError(f"Unexpected error: {exc}") from exc
            self._cache.set(requirement, payload)

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
