"""Command-line interface for one-off test case generation.

Useful for ad-hoc QA work or batch testing without spinning up the
HTTP server. The CLI talks to the same database and Gemini client the
web app uses, so behaviour is identical.

Examples
--------

Generate and pretty-print to stdout::

    python -m backend.scripts.cli generate "Verify login functionality"

Generate and store to history (requires database)::

    python -m backend.scripts.cli generate "Verify login" --store

Render the most recent history entry as a PDF::

    python -m backend.scripts.cli pdf --last --output report.pdf
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from backend.config import get_settings
from backend.services.gemini_service import GeminiService, GeminiServiceError
from backend.services.pdf_service import render_pdf
from backend.schemas.test_case import TestCase, TestGenerationResponse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m backend.scripts.cli",
        description="CLI for the AI Test Case Generator.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate test cases for a requirement.")
    gen.add_argument("requirement", help="Plain-English requirement text.")
    gen.add_argument(
        "--store",
        action="store_true",
        help="Persist the result to the database (requires PostgreSQL).",
    )
    gen.add_argument(
        "--output",
        "-o",
        choices=("json", "pretty", "pdf"),
        default="pretty",
        help="Output format (default: pretty).",
    )

    pdf = sub.add_parser("pdf", help="Render a stored generation as a PDF.")
    pdf.add_argument("--id", type=int, help="Generation ID to render.")
    pdf.add_argument(
        "--last",
        action="store_true",
        help="Render the most recent generation (requires PostgreSQL).",
    )
    pdf.add_argument(
        "--output",
        "-o",
        default="report.pdf",
        help="Path to write the PDF (default: report.pdf).",
    )

    return parser


def _format_pretty(payload: dict) -> str:
    requirement = payload.get("requirement", "")
    cases: list = payload.get("test_cases", [])
    out: list[str] = [f"Requirement: {requirement}", ""]
    for case in cases:
        out.append(f"[{case['test_case_id']}] {case['title']}  (Priority: {case['priority']})")
        out.append("  Steps:")
        for i, step in enumerate(case.get("steps", []), start=1):
            out.append(f"    {i}. {step}")
        out.append(f"  Expected: {case.get('expected_result', '')}")
        edges = case.get("edge_cases") or []
        if edges:
            out.append("  Edge cases:")
            for edge in edges:
                out.append(f"    - {edge}")
        out.append("")
    return "\n".join(out)


def _cmd_generate(args: argparse.Namespace) -> int:
    gemini = GeminiService()
    try:
        payload = gemini.generate_test_cases(args.requirement)
    except GeminiServiceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.store:
        try:
            from backend.database.session import SessionLocal
            from backend.models.test_generation import TestGeneration

            with SessionLocal() as db:
                record = TestGeneration(
                    requirement=payload["requirement"],
                    generated_output_json=payload,
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                print(
                    f"Stored as generation #{record.id}.",
                    file=sys.stderr,
                )
        except Exception as exc:  # noqa: BLE001
            print(
                f"warning: failed to persist to database: {exc}",
                file=sys.stderr,
            )

    if args.output == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.output == "pdf":
        cases = [TestCase.model_validate(c) for c in payload["test_cases"]]
        response = TestGenerationResponse(
            id=0,
            requirement=payload["requirement"],
            test_cases=cases,
            created_at=None,  # type: ignore[arg-type]
        )
        # ``created_at`` is required by the schema; patch the response model
        # to accept ``None`` by replacing with ``datetime.utcnow`` for the
        # CLI use-case.
        from datetime import datetime

        response = response.model_copy(
            update={"id": 0, "created_at": datetime.utcnow()}
        )
        pdf_bytes = render_pdf(response)
        sys.stdout.buffer.write(pdf_bytes)
    else:
        print(_format_pretty(payload))
    return 0


def _cmd_pdf(args: argparse.Namespace) -> int:
    if not args.id and not args.last:
        print("error: provide --id or --last", file=sys.stderr)
        return 2

    from datetime import datetime

    from backend.database.session import SessionLocal
    from backend.models.test_generation import TestGeneration
    from backend.schemas.test_case import TestCase as TestCaseSchema
    from backend.schemas.test_case import TestGenerationResponse

    with SessionLocal() as db:
        record: Optional[TestGeneration] = None
        if args.id:
            record = db.get(TestGeneration, args.id)
        else:
            record = (
                db.query(TestGeneration)
                .order_by(TestGeneration.created_at.desc())
                .first()
            )
        if record is None:
            print("error: generation not found", file=sys.stderr)
            return 1

        response = TestGenerationResponse(
            id=record.id,
            requirement=record.requirement,
            test_cases=[TestCaseSchema.model_validate(c) for c in record.generated_output_json.get("test_cases", [])],
            created_at=record.created_at or datetime.utcnow(),
        )

    pdf_bytes = render_pdf(response)
    with open(args.output, "wb") as fp:
        fp.write(pdf_bytes)
    print(f"Wrote {len(pdf_bytes)} bytes to {args.output}", file=sys.stderr)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        get_settings()
    except Exception as exc:  # noqa: BLE001
        print(f"error: failed to load configuration: {exc}", file=sys.stderr)
        return 1

    if args.command == "generate":
        return _cmd_generate(args)
    if args.command == "pdf":
        return _cmd_pdf(args)

    parser.error(f"unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
