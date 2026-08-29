"""Shift schema correction: one open shift per store, unlimited closed history."""
from alembic import op
import sqlalchemy as sa

revision = "0004_shift_open_partial_unique"
down_revision = "0003_shifts_and_cash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("uq_shift_store_state", "shifts", type_="unique")
    op.create_index(
        "uq_shift_store_open",
        "shifts",
        ["store_id"],
        unique=True,
        postgresql_where=sa.text("state = 'open'"),
    )


def downgrade() -> None:
    op.drop_index("uq_shift_store_open", table_name="shifts")
    op.create_unique_constraint("uq_shift_store_state", "shifts", ["store_id", "state"])
