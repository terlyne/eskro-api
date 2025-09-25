"""Change poll table and add poll questions and poll answers table

Revision ID: 915fe8bdb2f6
Revises: 8af885920cf5
Create Date: 2025-09-25 19:18:25.900566

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "915fe8bdb2f6"
down_revision: Union[str, Sequence[str], None] = "8af885920cf5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "poll_questions",
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("poll_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["poll_id"], ["polls.id"], name=op.f("fk_poll_questions_poll_id_polls")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_poll_questions")),
    )
    op.create_table(
        "poll_answers",
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["poll_questions.id"],
            name=op.f("fk_poll_answers_question_id_poll_questions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_poll_answers")),
    )
    op.drop_column("polls", "yandex_poll_url")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "polls",
        sa.Column("yandex_poll_url", sa.TEXT(), autoincrement=False, nullable=False),
    )
    op.drop_table("poll_answers")
    op.drop_table("poll_questions")
