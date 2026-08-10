"""add audience and documents to articles

Revision ID: 7f3a9c1e2b40
Revises: 5931e94244bb
Create Date: 2026-08-10 15:54:45.388338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7f3a9c1e2b40'
down_revision: Union[str, None] = '5931e94244bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("articles", sa.Column("audience", sa.Text(), nullable=False, server_default=""))
    op.add_column("articles", sa.Column("documents", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("articles", "documents")
    op.drop_column("articles", "audience")