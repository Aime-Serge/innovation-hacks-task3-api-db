"""Task 4-compatible registration details and profile photo sources.

The Task 3 API remains backward compatible with its original `name` registration payload, while
new registrations retain the full professional block from the final integration.  A JSON column is
intentional here: Task 3 is the database milestone; the final platform normalises this profile into
its dedicated `profiles` and `profile_skills` tables.

Revision ID: 0005
Revises: 0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("given_name", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("family_name", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("profile", sa.JSON(), nullable=True))
    op.create_check_constraint(
        op.f("ck_users_given_name_length"),
        "users",
        "given_name IS NULL OR (char_length(given_name) BETWEEN 1 AND 60 "
        "AND given_name = btrim(given_name))",
    )
    op.create_check_constraint(
        op.f("ck_users_family_name_length"),
        "users",
        "family_name IS NULL OR (char_length(family_name) BETWEEN 1 AND 60 "
        "AND family_name = btrim(family_name))",
    )
    op.drop_constraint(op.f("ck_users_avatar_url"), "users", type_="check")
    op.create_check_constraint(
        op.f("ck_users_avatar_url"),
        "users",
        "avatar_url IS NULL OR (avatar_url LIKE 'https://%' AND char_length(avatar_url) <= 2048) "
        "OR (avatar_url ~ '^data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}$' "
        "AND char_length(avatar_url) <= 700000)",
    )


def downgrade() -> None:
    # Downgrading must restore the old HTTPS-only invariant before removing the new columns.
    op.execute("UPDATE users SET avatar_url = NULL WHERE avatar_url LIKE 'data:%'")
    op.drop_constraint(op.f("ck_users_avatar_url"), "users", type_="check")
    op.create_check_constraint(
        op.f("ck_users_avatar_url"),
        "users",
        "avatar_url IS NULL OR (avatar_url LIKE 'https://%' AND char_length(avatar_url) <= 2048)",
    )
    op.drop_constraint(op.f("ck_users_family_name_length"), "users", type_="check")
    op.drop_constraint(op.f("ck_users_given_name_length"), "users", type_="check")
    op.drop_column("users", "profile")
    op.drop_column("users", "family_name")
    op.drop_column("users", "given_name")
