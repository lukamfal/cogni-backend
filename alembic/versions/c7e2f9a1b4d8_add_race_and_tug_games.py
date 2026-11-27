"""add race and tug game types

Revision ID: c7e2f9a1b4d8
Revises: b3c1a7d2e9f4
Create Date: 2026-11-27 16:00:00

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c7e2f9a1b4d8'
down_revision: Union[str, None] = 'b3c1a7d2e9f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # O tipo gametype guarda os nomes do enum (MEMORY, MATH...).
    op.execute("ALTER TYPE gametype ADD VALUE IF NOT EXISTS 'RACE'")
    op.execute("ALTER TYPE gametype ADD VALUE IF NOT EXISTS 'TUG'")


def downgrade() -> None:
    # O Postgres não remove valores de um enum; ficam sem uso.
    pass
