"""ORM model for stored test case generations."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base


class TestGeneration(Base):
    """A single request + AI response stored as JSON.

    Using the generic ``JSON`` type keeps the model portable across
    PostgreSQL and SQLite (used for unit tests). On PostgreSQL the column
    is transparently stored as native ``jsonb`` thanks to SQLAlchemy's
    dialect-aware compiler.
    """

    __tablename__ = "test_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    requirement: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    generated_output_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<TestGeneration id={self.id} requirement={self.requirement[:40]!r}>"
