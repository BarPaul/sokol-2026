"""add categories, article views, uploads support

Revision ID: 4a2c8e7d1f30
Revises: 7f3a9c1e2b40
Create Date: 2026-08-10 19:15:02.903435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4a2c8e7d1f30'
down_revision: Union[str, None] = '7f3a9c1e2b40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("views", sa.Integer(), nullable=False, server_default="0"))
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")
    op.drop_column("articles", "views")