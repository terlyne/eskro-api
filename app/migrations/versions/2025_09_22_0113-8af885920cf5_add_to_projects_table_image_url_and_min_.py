"""add to projects table image_url and min_text for main page

Revision ID: 8af885920cf5
Revises: 2b01677fff9f
Create Date: 2025-09-22 01:13:00.296419

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8af885920cf5"
down_revision: Union[str, Sequence[str], None] = "2b01677fff9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "news",
        "keywords",
        existing_type=postgresql.ARRAY(sa.VARCHAR(length=100)),
        type_=sa.ARRAY(sa.Text()),
        existing_nullable=False,
    )
    op.add_column("projects", sa.Column("min_text", sa.Text(), nullable=False))
    op.add_column("projects", sa.Column("image_url", sa.Text(), nullable=False))
    op.alter_column(
        "projects",
        "keywords",
        existing_type=postgresql.ARRAY(sa.VARCHAR(length=100)),
        type_=sa.ARRAY(sa.Text()),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "projects",
        "keywords",
        existing_type=sa.ARRAY(sa.Text()),
        type_=postgresql.ARRAY(sa.VARCHAR(length=100)),
        existing_nullable=False,
    )
    op.drop_column("projects", "image_url")
    op.drop_column("projects", "min_text")
    op.alter_column(
        "news",
        "keywords",
        existing_type=sa.ARRAY(sa.Text()),
        type_=postgresql.ARRAY(sa.VARCHAR(length=100)),
        existing_nullable=False,
    )
