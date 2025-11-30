"""add tag, position and quadrant to tasks table

Revision ID: 20251129_add_tag_position_quadrant
Revises:
Create Date: 2025-11-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251129_add_tag_position_quadrant"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    try:
        cols = [c["name"] for c in inspector.get_columns("tasks")]
    except Exception:
        cols = []

    if "tag" not in cols:
        op.add_column("tasks", sa.Column("tag", sa.String(), nullable=True))
    if "position" not in cols:
        op.add_column("tasks", sa.Column("position", sa.Integer(), nullable=True))
    if "quadrant" not in cols:
        op.add_column("tasks", sa.Column("quadrant", sa.Integer(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    try:
        cols = [c["name"] for c in inspector.get_columns("tasks")]
    except Exception:
        cols = []

    # Use batch_alter_table to support SQLite safely
    with op.batch_alter_table("tasks") as batch_op:
        if "quadrant" in cols:
            batch_op.drop_column("quadrant")
        if "position" in cols:
            batch_op.drop_column("position")
        if "tag" in cols:
            batch_op.drop_column("tag")
