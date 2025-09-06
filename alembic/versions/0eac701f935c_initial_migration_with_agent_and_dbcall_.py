"""Initial migration with Agent and DBCall models

Revision ID: 0eac701f935c
Revises:
Create Date: 2025-09-04 22:56:45.121595

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0eac701f935c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create agents table
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agents_agent_id"), "agents", ["agent_id"], unique=True)
    op.create_index(op.f("ix_agents_id"), "agents", ["id"], unique=False)

    # Create calls table
    op.create_table(
        "calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("agent_talk_ratio", sa.Float(), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("embedding", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_calls_call_id"), "calls", ["call_id"], unique=True)
    op.create_index(
        op.f("ix_calls_customer_id"), "calls", ["customer_id"], unique=False
    )
    op.create_index(op.f("ix_calls_id"), "calls", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop calls table
    op.drop_index(op.f("ix_calls_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_customer_id"), table_name="calls")
    op.drop_index(op.f("ix_calls_call_id"), table_name="calls")
    op.drop_table("calls")

    # Drop agents table
    op.drop_index(op.f("ix_agents_id"), table_name="agents")
    op.drop_index(op.f("ix_agents_agent_id"), table_name="agents")
    op.drop_table("agents")
