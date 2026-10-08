"""Create the current schema and backfill legacy QR content.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, select
from urllib.parse import urlparse


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def _index_names(bind):
    return {
        index["name"]
        for table_name in inspect(bind).get_table_names()
        for index in inspect(bind).get_indexes(table_name)
    }


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("password", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "qr_codes" not in tables:
        op.create_table(
            "qr_codes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("qr_id", sa.String(), nullable=True),
            sa.Column("content", sa.String(), nullable=True),
            sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=True),
            sa.Column("scans", sa.Integer(), server_default=sa.text("0"), nullable=True),
            sa.Column("risk_score", sa.Integer(), server_default=sa.text("0"), nullable=True),
            sa.Column("ai_status", sa.String(), server_default="UNKNOWN", nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("qr_id"),
        )

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "content_versions" not in tables:
        op.create_table(
            "content_versions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("qr_code_id", sa.Integer(), nullable=False),
            sa.Column("content_type", sa.String(), server_default="URL", nullable=False),
            sa.Column("content", sa.String(), nullable=False),
            sa.Column("version", sa.Integer(), nullable=False),
            sa.Column("is_published", sa.Boolean(), server_default=sa.true(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["qr_code_id"], ["qr_codes.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    indexes = _index_names(bind)
    expected_indexes = {
        "ix_users_id": ("users", ["id"], False),
        "ix_users_email": ("users", ["email"], False),
        "ix_qr_codes_id": ("qr_codes", ["id"], False),
        "ix_qr_codes_qr_id": ("qr_codes", ["qr_id"], False),
        "ix_content_versions_id": ("content_versions", ["id"], False),
        "ix_content_versions_qr_code_id": (
            "content_versions",
            ["qr_code_id"],
            False,
        ),
        "uq_content_versions_qr_version": (
            "content_versions",
            ["qr_code_id", "version"],
            True,
        ),
    }
    for name, (table_name, columns, unique) in expected_indexes.items():
        if name not in indexes:
            op.create_index(name, table_name, columns, unique=unique)

    qr_codes = sa.table(
        "qr_codes",
        sa.column("id", sa.Integer()),
        sa.column("content", sa.String()),
    )
    content_versions = sa.table(
        "content_versions",
        sa.column("qr_code_id", sa.Integer()),
        sa.column("content_type", sa.String()),
        sa.column("content", sa.String()),
        sa.column("version", sa.Integer()),
        sa.column("is_published", sa.Boolean()),
    )

    rows = bind.execute(
        select(qr_codes.c.id, qr_codes.c.content)
        .select_from(qr_codes)
    ).mappings()
    for row in rows:
        existing = bind.execute(
            select(content_versions.c.qr_code_id)
            .where(content_versions.c.qr_code_id == row["id"])
            .limit(1)
        ).first()
        content = row["content"]
        parsed = urlparse(content or "")
        if existing is None and parsed.scheme in {"http", "https"} and parsed.netloc:
            bind.execute(
                content_versions.insert().values(
                    qr_code_id=row["id"],
                    content_type="URL",
                    content=content,
                    version=1,
                    is_published=True,
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "content_versions" in tables:
        op.drop_table("content_versions")
    if "qr_codes" in tables:
        op.drop_table("qr_codes")
    if "users" in tables:
        op.drop_table("users")
