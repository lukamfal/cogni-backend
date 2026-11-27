"""add care_links

Revision ID: b3c1a7d2e9f4
Revises: 91fbfbcbdbe8
Create Date: 2026-11-27 15:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3c1a7d2e9f4'
down_revision: Union[str, None] = '91fbfbcbdbe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'care_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('caregiver_id', sa.Integer(), nullable=False),
        sa.Column('elder_email', sa.String(length=200), nullable=False),
        sa.Column('elder_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', name='carelinkstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['caregiver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['elder_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('caregiver_id', 'elder_email', name='uq_care_link'),
    )
    op.create_index(op.f('ix_care_links_id'), 'care_links', ['id'], unique=False)
    op.create_index(op.f('ix_care_links_caregiver_id'), 'care_links', ['caregiver_id'], unique=False)
    op.create_index(op.f('ix_care_links_elder_email'), 'care_links', ['elder_email'], unique=False)
    op.create_index(op.f('ix_care_links_elder_id'), 'care_links', ['elder_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_care_links_elder_id'), table_name='care_links')
    op.drop_index(op.f('ix_care_links_elder_email'), table_name='care_links')
    op.drop_index(op.f('ix_care_links_caregiver_id'), table_name='care_links')
    op.drop_index(op.f('ix_care_links_id'), table_name='care_links')
    op.drop_table('care_links')
    sa.Enum(name='carelinkstatus').drop(op.get_bind(), checkfirst=True)
