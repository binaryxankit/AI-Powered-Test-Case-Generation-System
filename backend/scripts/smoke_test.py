"""Local smoke test for the backend.

Run with the project's venv active and the dependencies installed:

    python -m backend.scripts.smoke_test

The script:

* Spins up an isolated in-memory SQLite database.
* Stubs the ``GeminiService`` so no real API key is required.
* Exercises ``/api/generate``, ``/api/history``, ``/api/history/{id}`` and
  ``/api/history/{id}/pdf`` end-to-end.
* Prints a concise PASS / FAIL summary.
"""
from __future__ import annotations

import io
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.session import Base, get_db
from backend.main import app
from backend.models import test_generation  # noqa: F401  (register model)
from backend.services import test_case_service as service_module


# A reproducible response that mimics a real Gemini payload.
STUB_PAYLOAD: dict[str, Any] = {
    "requirement": "Verify login functionality and dashboard access",
    "test_cases": [
        {
            "test_case_id": "TC001",
            "title": "Verify successful login with valid credentials",
            "priority": "High",
            "steps": [
                "Open the login page",
                "Enter a valid username",
                "Enter a valid password",
                "Click Login",
            ],
            "expected_result": "User is redirected to the dashboard.",
            "edge_cases": ["Empty username", "Empty password", "Invalid credentials"],
        },
        {
            "test_case_id": "TC002",
            "title": "Verify login fails with wrong password",
            "priority": "Medium",
            "steps": [
                "Open the login page",
                "Enter a valid username",
                "Enter an incorrect password",
                "Click Login",
            ],
            "expected_result": "An error message is shown and the user remains on the login page.",
            "edge_cases": ["SQL injection in password"],
        },
    ],
}


class StubGemini:
    """In-memory replacement for :class:`GeminiService`."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def generate_test_cases(self, requirement: str) -> dict[str, Any]:
        self.calls.append(requirement)
        return {
            "requirement": requirement,
            "test_cases": [dict(case) for case in STUB_PAYLOAD["test_cases"]],
        }


@contextmanager
def _isolated_app() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)


def _check(label: str, condition: bool) -> bool:
    marker = "PASS" if condition else "FAIL"
    print(f"  [{marker}] {label}")
    return condition


def main() -> int:
    print("Running backend smoke test...")

    # Save the real ctor so we can restore it.
    real_init = service_module.TestCaseService.__init__

    def patched_init(self, db, gemini=None):  # type: ignore[no-redef]
        real_init(self, db, gemini=StubGemini())

    service_module.TestCaseService.__init__ = patched_init  # type: ignore[assignment]
    try:
        with _isolated_app() as client:
            failures: list[str] = []

            # Health
            r = client.get("/api/health")
            if not _check("/api/health returns 200", r.status_code == 200):
                failures.append("health")

            # Generate
            r = client.post(
                "/api/generate",
                json={"requirement": STUB_PAYLOAD["requirement"]},
            )
            if not _check(
                "/api/generate returns 201 with payload",
                r.status_code == 201 and r.json()["test_cases"],
            ):
                failures.append("generate")

            generation_id = r.json()["id"] if r.status_code == 201 else -1

            # Validation
            r = client.post("/api/generate", json={"requirement": "a"})
            if not _check(
                "/api/generate rejects short input (422)",
                r.status_code == 422,
            ):
                failures.append("validation")

            # History list
            r = client.get("/api/history")
            if not _check(
                "/api/history returns the new generation",
                r.status_code == 200 and any(
                    item["id"] == generation_id for item in r.json()
                ),
            ):
                failures.append("history list")

            # History detail
            r = client.get(f"/api/history/{generation_id}")
            if not _check(
                "/api/history/{id} returns the generation",
                r.status_code == 200
                and r.json()["requirement"] == STUB_PAYLOAD["requirement"],
            ):
                failures.append("history detail")

            # 404
            r = client.get("/api/history/99999")
            if not _check("/api/history/{missing} returns 404", r.status_code == 404):
                failures.append("history 404")

            # PDF
            r = client.get(f"/api/history/{generation_id}/pdf")
            pdf_ok = (
                r.status_code == 200
                and r.headers.get("content-type") == "application/pdf"
                and r.content[:4] == b"%PDF"
            )
            if not _check(
                "/api/history/{id}/pdf returns a valid PDF",
                pdf_ok,
            ):
                failures.append("pdf")

            if pdf_ok:
                # Write a copy next to this script for manual inspection.
                out = Path(tempfile.gettempdir()) / "smoke_test_output.pdf"
                out.write_bytes(r.content)
                print(f"  [INFO] PDF preview saved to {out} ({len(r.content)} bytes)")
    finally:
        service_module.TestCaseService.__init__ = real_init  # type: ignore[assignment]

    if failures:
        print(f"\nFAILED checks: {', '.join(failures)}")
        return 1
    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
