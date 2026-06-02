"""Initial schema: ``test_generations`` table.

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-03 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "test_generations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("requirement", sa.Text(), nullable=False),
        sa.Column(
            "generated_output_json",
            sa.JSON().with_variant(
                sa.dialects.postgresql.JSONB(), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_test_generations_requirement",
        "test_generations",
        ["requirement"],
    )
    op.create_index(
        "ix_test_generations_created_at",
        "test_generations",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_generations_created_at", table_name="test_generations")
    op.drop_index("ix_test_generations_requirement", table_name="test_generations")
    op.drop_table("test_generations")
