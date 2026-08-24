"""Add persistent users/roles and offline sync command ledger."""
from alembic import op
import sqlalchemy as sa

revision = "0002_auth_and_sync"
down_revision = "0001_initial_pos_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("store_id", sa.String(36), sa.ForeignKey("stores.id"), nullable=False),
        sa.Column("username", sa.String(200), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("roles", sa.String(500), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "username", name="uq_user_tenant_username"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_store_id", "users", ["store_id"])
    op.create_table(
        "sync_commands",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("store_id", sa.String(36), nullable=False),
        sa.Column("command_id", sa.String(100), nullable=False),
        sa.Column("operation", sa.String(100), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "store_id", "command_id", name="uq_sync_command_scope"),
    )


def downgrade() -> None:
    op.drop_table("sync_commands")
    op.drop_index("ix_users_store_id", table_name="users")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_table("users")
