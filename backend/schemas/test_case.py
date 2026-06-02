"""Pydantic schemas for request validation and API responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


Priority = Literal["Low", "Medium", "High", "Critical"]


class TestCase(BaseModel):
    """A single structured test case returned by the AI."""

    model_config = ConfigDict(extra="ignore")

    test_case_id: str = Field(..., min_length=1, max_length=32)
    title: str = Field(..., min_length=1, max_length=300)
    priority: Priority = "Medium"
    steps: List[str] = Field(..., min_length=1)
    expected_result: str = Field(..., min_length=1)
    edge_cases: List[str] = Field(default_factory=list)

    @field_validator("priority", mode="before")
    @classmethod
    def _normalize_priority(cls, value: object) -> object:
        """Accept any case (``"high"``) and pick a valid literal."""
        if isinstance(value, str):
            cleaned = value.strip().capitalize()
            if cleaned in {"Low", "Medium", "High", "Critical"}:
                return cleaned
        return value


class GenerateRequest(BaseModel):
    """Body of ``POST /api/generate``."""

    requirement: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Plain-English software testing requirement.",
    )


class TestGenerationResponse(BaseModel):
    """Full response returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    requirement: str
    test_cases: List[TestCase]
    created_at: datetime


class TestGenerationSummary(BaseModel):
    """Lightweight payload for the history list endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    requirement: str
    created_at: datetime
    test_case_count: int


class HealthResponse(BaseModel):
    """Health-check response."""

    status: Literal["ok", "degraded"] = "ok"
    version: str
    model: Optional[str] = None
    database: Literal["ok", "unreachable", "unknown"] = "unknown"
    gemini_key_configured: bool = False
