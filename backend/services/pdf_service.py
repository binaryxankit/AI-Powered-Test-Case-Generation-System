"""PDF report generation for stored test case generations."""
from __future__ import annotations

import io
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.schemas.test_case import Priority, TestCase, TestGenerationResponse


_PRIORITY_COLORS: dict[Priority, colors.Color] = {
    "Low": colors.HexColor("#10b981"),
    "Medium": colors.HexColor("#0ea5e9"),
    "High": colors.HexColor("#f59e0b"),
    "Critical": colors.HexColor("#ef4444"),
}


def _build_styles() -> dict[str, ParagraphStyle]:
    """Create the paragraph styles used across the PDF."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#475569"),
            spaceAfter=18,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=4,
            spaceAfter=6,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor("#475569"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#0f172a"),
            leading=14,
            alignment=TA_LEFT,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#64748b"),
        ),
    }


def _priority_badge(priority: Priority) -> Table:
    """Return a small colored badge for a priority value."""
    color = _PRIORITY_COLORS.get(priority, colors.HexColor("#64748b"))
    badge = Table(
        [[Paragraph(f"&nbsp;{priority}&nbsp;", _build_styles()["body"])]],
        colWidths=[0.7 * inch],
    )
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROUNDEDCORNERS", [6, 6, 6, 6]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return badge


def _section_label(text: str) -> Paragraph:
    return Paragraph(text.upper(), _build_styles()["label"])


def _numbered_steps(steps: List[str]) -> List[Paragraph]:
    return [
        Paragraph(f"{i + 1}. {step}", _build_styles()["body"])
        for i, step in enumerate(steps)
    ]


def _bullet_list(items: List[str]) -> List[Paragraph]:
    return [
        Paragraph(f"&bull; {item}", _build_styles()["body"]) for item in items
    ]


def _build_test_case_flow(case: TestCase) -> List:
    """Build the reportlab flowables for a single test case."""
    styles = _build_styles()
    flow: list = []

    header = Table(
        [[Paragraph(case.test_case_id, styles["h2"]), _priority_badge(case.priority)]],
        colWidths=[5.5 * inch, 1.0 * inch],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flow.append(header)
    flow.append(Paragraph(case.title, styles["h2"]))
    flow.append(Spacer(1, 4))

    flow.append(_section_label("Test Steps"))
    flow.extend(_numbered_steps(case.steps))
    flow.append(Spacer(1, 8))

    flow.append(_section_label("Expected Result"))
    flow.append(Paragraph(case.expected_result, styles["body"]))
    flow.append(Spacer(1, 8))

    if case.edge_cases:
        flow.append(_section_label("Edge Cases"))
        flow.extend(_bullet_list(case.edge_cases))
        flow.append(Spacer(1, 8))

    flow.append(HRFlowable(width="100%", color=colors.HexColor("#e2e8f0"), thickness=0.6))
    flow.append(Spacer(1, 10))
    return flow


def render_pdf(generation: TestGenerationResponse) -> bytes:
    """Render a TestGenerationResponse as a PDF and return the raw bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Test Case Report",
        author="AI Test Case Generator",
    )

    styles = _build_styles()
    story: list = []

    story.append(Paragraph("AI-Generated Test Case Report", styles["title"]))
    story.append(
        Paragraph(
            f"Generated on {generation.created_at.strftime('%B %d, %Y at %H:%M UTC')}"
            if generation.created_at.tzinfo
            else f"Generated on {generation.created_at.strftime('%B %d, %Y at %H:%M')}",
            styles["subtitle"],
        )
    )

    story.append(_section_label("Requirement"))
    story.append(Paragraph(generation.requirement, styles["body"]))
    story.append(Spacer(1, 12))

    story.append(HRFlowable(width="100%", color=colors.HexColor("#cbd5e1"), thickness=0.8))
    story.append(Spacer(1, 12))

    for index, case in enumerate(generation.test_cases):
        story.extend(_build_test_case_flow(case))
        if index < len(generation.test_cases) - 1:
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            f"Total test cases: <b>{len(generation.test_cases)}</b> &middot; "
            f"Report ID: <b>#{generation.id}</b>",
            styles["meta"],
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
