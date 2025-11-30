"""add subtasks and recurrence

Revision ID: dbb6eede6d13
Revises: 20251129_add_tag_position_quadrant
Create Date: 2025-11-29

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dbb6eede6d13"
down_revision = "20251129_add_tag_position_quadrant"
branch_labels = None
depends_on = None


def upgrade():
    # Add recurrence fields to tasks table
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("recurrence_pattern", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("recurrence_end_date", sa.Date(), nullable=True))

    # Create subtasks table
    op.create_table(
        "subtasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subtasks_id"), "subtasks", ["id"], unique=False)


def downgrade():
    # Drop subtasks table
    op.drop_index(op.f("ix_subtasks_id"), table_name="subtasks")
    op.drop_table("subtasks")

    # Remove recurrence fields from tasks
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_column("recurrence_end_date")
        batch_op.drop_column("recurrence_pattern")
