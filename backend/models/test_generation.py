"""ORM model for stored test case generations."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base


class TestGeneration(Base):
    """A single request + AI response stored as JSONB."""

    __tablename__ = "test_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requirement: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    generated_output_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<TestGeneration id={self.id} requirement={self.requirement[:40]!r}>"
