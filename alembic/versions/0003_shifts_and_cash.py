"""Shift and cash-control schema.

Revision ID: 0003_shifts_and_cash
Revises: 0002_auth_and_sync
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_shifts_and_cash"
down_revision = "0002_auth_and_sync"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shifts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("opened_by", sa.String(36), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("opening_cash", sa.Numeric(18, 2), nullable=False),
        sa.Column("closing_cash", sa.Numeric(18, 2), nullable=True),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("closed_by", sa.String(36), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_shifts_tenant_id", "shifts", ["tenant_id"])
    op.create_index("ix_shifts_store_opened", "shifts", ["store_id", "opened_at"])
    op.create_index("uq_shift_store_open", "shifts", ["store_id"], unique=True, postgresql_where=sa.text("state = 'open'"))

    op.create_table(
        "cash_movements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("shift_id", sa.String(36), sa.ForeignKey("shifts.id"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("reason", sa.String(200), nullable=False),
        sa.Column("actor_id", sa.String(36), nullable=False),
        sa.Column("correlation_id", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cash_movements_shift_created", "cash_movements", ["shift_id", "created_at"])


def downgrade() -> None:
    op.drop_table("cash_movements")
    op.drop_table("shifts")
