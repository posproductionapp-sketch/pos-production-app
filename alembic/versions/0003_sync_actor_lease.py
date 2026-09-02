"""Bind offline commands to their actor and add replay lease metadata."""
from alembic import op
import sqlalchemy as sa

revision = "0003_sync_actor_lease"
down_revision = "0002_auth_and_sync"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sync_commands", sa.Column("actor_id", sa.String(36), nullable=True))
    op.add_column("sync_commands", sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("sync_commands", sa.Column("lease_until", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_sync_commands_actor_id", "sync_commands", ["actor_id"])

    # Existing receipt-only rows have no trustworthy originating principal.
    # Keep them explicitly unresolved instead of attributing them to a new actor.
    op.execute(sa.text("UPDATE sync_commands SET actor_id = 'legacy-unbound' WHERE actor_id IS NULL"))
    op.alter_column("sync_commands", "actor_id", nullable=False)


def downgrade() -> None:
    op.drop_index("ix_sync_commands_actor_id", table_name="sync_commands")
    op.drop_column("sync_commands", "lease_until")
    op.drop_column("sync_commands", "attempt_count")
    op.drop_column("sync_commands", "actor_id")
