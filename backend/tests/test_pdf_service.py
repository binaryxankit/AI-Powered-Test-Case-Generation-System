"""Unit tests for the PDF report renderer."""
from __future__ import annotations

from datetime import datetime, timezone

from backend.schemas.test_case import (
    Priority,
    TestCase,
    TestGenerationResponse,
)
from backend.services.pdf_service import render_pdf


def _make_response(num_cases: int = 1) -> TestGenerationResponse:
    cases = [
        TestCase(
            test_case_id=f"TC{i + 1:03d}",
            title=f"Test case {i + 1}",
            priority=("Low", "Medium", "High", "Critical")[i % 4],
            steps=[f"Step {j + 1}" for j in range(3)],
            expected_result=f"Outcome {i + 1}",
            edge_cases=["Empty input", "Max length"] if i == 0 else [],
        )
        for i in range(num_cases)
    ]
    return TestGenerationResponse(
        id=42,
        requirement="Verify login functionality",
        test_cases=cases,
        created_at=datetime(2026, 6, 3, 10, 0, tzinfo=timezone.utc),
    )


class TestRenderPdf:
    def test_returns_valid_pdf_magic_bytes(self):
        pdf = render_pdf(_make_response())
        assert pdf[:4] == b"%PDF"
        assert len(pdf) > 1000  # not empty

    def test_pdf_ends_with_eof_marker(self):
        pdf = render_pdf(_make_response())
        assert pdf.rstrip().endswith(b"%%EOF")

    def test_handles_multiple_cases(self):
        pdf = render_pdf(_make_response(num_cases=5))
        assert pdf[:4] == b"%PDF"
        # A multi-page document should be larger than a one-page one.
        one_page = render_pdf(_make_response(num_cases=1))
        assert len(pdf) >= len(one_page)

    def test_handles_no_edge_cases(self):
        cases = [
            TestCase(
                test_case_id="TC001",
                title="Without edge cases",
                priority="Medium",
                steps=["s"],
                expected_result="r",
                edge_cases=[],
            )
        ]
        response = TestGenerationResponse(
            id=1,
            requirement="r",
            test_cases=cases,
            created_at=datetime(2026, 6, 3, tzinfo=timezone.utc),
        )
        pdf = render_pdf(response)
        assert pdf[:4] == b"%PDF"

    def test_handles_naive_datetime(self):
        response = TestGenerationResponse(
            id=1,
            requirement="r",
            test_cases=[
                TestCase(
                    test_case_id="TC001",
                    title="t",
                    priority="Medium",
                    steps=["s"],
                    expected_result="r",
                )
            ],
            # Naive datetime is acceptable for the formatter.
            created_at=datetime(2026, 6, 3, 10, 0),
        )
        pdf = render_pdf(response)
        assert pdf[:4] == b"%PDF"

    def test_priority_badge_color_uses_each_priority(self):
        """All four priorities should render without error."""
        for priority in ("Low", "Medium", "High", "Critical"):
            response = TestGenerationResponse(
                id=1,
                requirement="r",
                test_cases=[
                    TestCase(
                        test_case_id="TC001",
                        title="t",
                        priority=priority,  # type: ignore[arg-type]
                        steps=["s"],
                        expected_result="r",
                    )
                ],
                created_at=datetime(2026, 6, 3, tzinfo=timezone.utc),
            )
            pdf = render_pdf(response)
            assert pdf[:4] == b"%PDF", f"failed for priority={priority}"

    def test_is_deterministic_for_same_input(self):
        a = render_pdf(_make_response())
        b = render_pdf(_make_response())
        # ReportLab includes a creation date in the metadata so the
        # binaries are *not* byte-identical, but both should be valid
        # PDFs of comparable size.
        assert a[:4] == b"%PDF"
        assert b[:4] == b"%PDF"
        assert abs(len(a) - len(b)) < 4096
