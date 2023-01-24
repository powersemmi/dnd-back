"""init

Revision ID: 2484733f7822
Revises:
Create Date: 2023-01-24 04:10:52.352932

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2484733f7822"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("username", sa.String(length=256), nullable=False),
        sa.Column("full_name", sa.String(length=256), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", postgresql.BYTEA(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(
        op.f("ix_users_username"), "users", ["username"], unique=True
    )
    op.create_table(
        "gamesets",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("short_url", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_gamesets_short_url"), "gamesets", ["short_url"], unique=True
    )
    op.create_table(
        "gamesets_meta",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("gameset_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["gameset_id"],
            ["gamesets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "maps",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("gameset_meta_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["gameset_meta_id"],
            ["gamesets_meta.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pawns",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("gameset_meta_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["gameset_meta_id"],
            ["gamesets_meta.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "gameset_pawns_position",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("gameset_meta_id", sa.BigInteger(), nullable=True),
        sa.Column("pawn_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["gameset_meta_id"],
            ["gamesets_meta.id"],
        ),
        sa.ForeignKeyConstraint(
            ["pawn_id"],
            ["pawns.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "maps_meta",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("map_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("len_x", sa.Integer(), nullable=False),
        sa.Column("len_y", sa.Integer(), nullable=False),
        sa.Column("image", postgresql.BYTEA(), nullable=True),
        sa.ForeignKeyConstraint(
            ["map_id"],
            ["maps.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pawns_meta",
        sa.Column(
            "id", sa.BigInteger(), sa.Identity(always=True), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("pawn_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column(
            "color",
            sqlalchemy_utils.types.color.ColorType(length=20),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["pawn_id"],
            ["pawns.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("pawns_meta")
    op.drop_table("maps_meta")
    op.drop_table("gameset_pawns_position")
    op.drop_table("pawns")
    op.drop_table("maps")
    op.drop_table("gamesets_meta")
    op.drop_index(op.f("ix_gamesets_short_url"), table_name="gamesets")
    op.drop_table("gamesets")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###