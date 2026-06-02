"""Unit tests for the request/response Pydantic schemas."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.schemas.test_case import (
    GenerateRequest,
    HealthResponse,
    Priority,
    TestCase,
    TestGenerationResponse,
    TestGenerationSummary,
)


class TestGenerateRequest:
    def test_accepts_a_normal_requirement(self):
        req = GenerateRequest(requirement="Verify login")
        assert req.requirement == "Verify login"

    def test_strips_no_whitespace_by_default(self):
        req = GenerateRequest(requirement="  Verify login  ")
        assert req.requirement == "  Verify login  "

    @pytest.mark.parametrize("value", ["", " ", "  ", "a", "ab"])
    def test_rejects_too_short_requirements(self, value: str):
        with pytest.raises(ValidationError):
            GenerateRequest(requirement=value)

    def test_rejects_overlong_requirements(self):
        with pytest.raises(ValidationError):
            GenerateRequest(requirement="x" * 2001)


class TestTestCase:
    def test_round_trips_a_well_formed_case(self):
        case = TestCase(
            test_case_id="TC001",
            title="Verify login",
            priority="High",
            steps=["Open page", "Enter credentials", "Submit"],
            expected_result="Dashboard shown",
            edge_cases=["Empty password"],
        )
        as_dict = case.model_dump()
        again = TestCase.model_validate(as_dict)
        assert again == case

    @pytest.mark.parametrize(
        "raw,expected",
        [("low", "Low"), ("LOW", "Low"), ("Medium", "Medium"), ("critical", "Critical")],
    )
    def test_normalises_priority_case(self, raw: str, expected: Priority):
        case = TestCase(
            test_case_id="TC001",
            title="t",
            priority=raw,
            steps=["s"],
            expected_result="r",
        )
        assert case.priority == expected

    def test_invalid_priority_is_kept_as_is(self):
        with pytest.raises(ValidationError):
            TestCase(
                test_case_id="TC001",
                title="t",
                priority="urgent",  # not in Literal
                steps=["s"],
                expected_result="r",
            )

    def test_requires_at_least_one_step(self):
        with pytest.raises(ValidationError):
            TestCase(
                test_case_id="TC001",
                title="t",
                priority="High",
                steps=[],
                expected_result="r",
            )

    def test_edge_cases_default_to_empty_list(self):
        case = TestCase(
            test_case_id="TC001",
            title="t",
            priority="High",
            steps=["s"],
            expected_result="r",
        )
        assert case.edge_cases == []


class TestTestGenerationResponse:
    def test_serialization_round_trip(self):
        now = datetime(2026, 6, 3, 10, 0, tzinfo=timezone.utc)
        response = TestGenerationResponse(
            id=7,
            requirement="Verify login",
            test_cases=[
                TestCase(
                    test_case_id="TC001",
                    title="t",
                    priority="High",
                    steps=["s"],
                    expected_result="r",
                )
            ],
            created_at=now,
        )
        as_dict = response.model_dump(mode="json")
        again = TestGenerationResponse.model_validate(as_dict)
        assert again.id == 7
        assert len(again.test_cases) == 1
        assert again.created_at == now


class TestSummaryAndHealth:
    def test_summary_minimum_fields(self):
        now = datetime(2026, 6, 3, 10, 0, tzinfo=timezone.utc)
        summary = TestGenerationSummary(
            id=1,
            requirement="r",
            created_at=now,
            test_case_count=3,
        )
        assert summary.test_case_count == 3

    def test_health_default_status_is_ok(self):
        h = HealthResponse(version="1.0.0")
        assert h.status == "ok"
        assert h.database == "unknown"
        assert h.gemini_key_configured is False
        assert h.version == "1.0.0"
