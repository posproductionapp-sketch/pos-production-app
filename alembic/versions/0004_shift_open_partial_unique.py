"""Compatibility migration for the corrected shift open-state invariant."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0004_shift_open_partial_unique"
down_revision = "0003_shifts_and_cash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    constraints = {c["name"] for c in inspector.get_unique_constraints("shifts")}
    indexes = {i["name"] for i in inspector.get_indexes("shifts")}
    if "uq_shift_store_state" in constraints:
        op.drop_constraint("uq_shift_store_state", "shifts", type_="unique")
    if "uq_shift_store_open" not in indexes:
        op.create_index("uq_shift_store_open", "shifts", ["store_id"], unique=True, postgresql_where=sa.text("state = 'open'"))


def downgrade() -> None:
    # Safe rollback deliberately preserves the corrected invariant. Recreating
    # the historical blanket unique would make valid closed-shift history
    # impossible and could fail or require destructive data changes.
    return None
