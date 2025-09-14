"""Initial

Revision ID: d2adcbce86b8
Revises:
Create Date: 2025-09-12 21:57:23.305638

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2adcbce86b8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "banners",
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("redirect_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("count_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_banners")),
    )
    op.create_table(
        "events",
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("event_date", sa.DateTime(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_events")),
    )
    op.create_table(
        "feedbacks",
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("middle_name", sa.Text(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_answered", sa.Boolean(), nullable=False),
        sa.Column("response", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feedbacks")),
    )
    op.create_table(
        "news_types",
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news_types")),
    )
    op.create_table(
        "partners",
        sa.Column("logo_url", sa.Text(), nullable=False),
        sa.Column("partner_name", sa.Text(), nullable=False),
        sa.Column("partner_url", sa.Text(), nullable=True),
        sa.Column("count_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_partners")),
    )
    op.create_table(
        "polls",
        sa.Column("theme", sa.String(length=100), nullable=False),
        sa.Column("yandex_poll_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_polls")),
    )
    op.create_table(
        "projects",
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("keywords", sa.ARRAY(sa.String(length=100)), nullable=False),
        sa.Column("theme", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
    )
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=20), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
        sa.Column("hashed_password", sa.LargeBinary(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "news",
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("keywords", sa.ARRAY(sa.String(length=100)), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("min_text", sa.Text(), nullable=False),
        sa.Column("news_date", sa.Date(), nullable=False),
        sa.Column("type_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["type_id"], ["news_types.id"], name=op.f("fk_news_type_id_news_types")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_news")),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("jti", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_refresh_tokens_user_id_users")
        ),
        sa.PrimaryKeyConstraint("jti", name=op.f("pk_refresh_tokens")),
    )
    op.create_table(
        "subscribers",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "subscribed_at",
            sa.Date(),
            server_default=sa.text("CURRENT_DATE"),
            nullable=False,
        ),
        sa.Column("is_confirmed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("type_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["news_types.id"],
            name=op.f("fk_subscribers_type_id_news_types"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscribers")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("subscribers")
    op.drop_table("refresh_tokens")
    op.drop_table("news")
    op.drop_table("users")
    op.drop_table("projects")
    op.drop_table("polls")
    op.drop_table("partners")
    op.drop_table("news_types")
    op.drop_table("feedbacks")
    op.drop_table("events")
    op.drop_table("banners")
