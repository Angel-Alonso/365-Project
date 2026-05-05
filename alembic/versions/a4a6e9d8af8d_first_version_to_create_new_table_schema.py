"""First version to create new table schema

Revision ID: a4a6e9d8af8d
Revises: e91d0c24f7d0
Create Date: 2026-05-04 17:48:16.838651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4a6e9d8af8d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_table",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
    )

    op.create_table(
        "portfolio_table",
        sa.Column("portfolio_id", sa.Integer, sa.Identity(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("portfolio_name", sa.String, nullable=False),
        sa.Column("date_created", sa.DateTime, server_default='now()'),
    )
    
    op.create_table(
        "asset_table",
        sa.Column("stock_id", sa.Integer, sa.Identity(), primary_key=True, autoincrement=True),
        sa.Column("stock_name", sa.String, nullable=False),
        sa.Column("price", sa.Integer, nullable=False),
    )

    op.create_table(
        "holdings_table",
        sa.Column("holdings_id", sa.Integer, sa.Identity(), primary_key=True, autoincrement=True),
        sa.Column("stock_id", sa.Integer, sa.ForeignKey("asset_table.stock_id"), nullable=False),
        sa.Column("portfolio_id", sa.Integer, sa.ForeignKey("portfolio_table.portfolio_id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
    )

    op.create_table(
        "transaction_table",
        sa.Column("transaction_id", sa.Integer, sa.Identity(), primary_key=True, autoincrement=True),
        sa.Column("portfolio_id", sa.Integer, nullable=False),
        sa.Column("stock_id", sa.Integer, nullable=False),
        sa.Column("time_traded", sa.DateTime, server_default='now()'),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("portfolio_name", sa.String, nullable=False),
    )

    # fake data so V1 has something to GET immediately
    op.execute(sa.text("INSERT INTO user_table (name, email) VALUES ('admin', 'admin@admin.com')"))
    op.execute(sa.text("INSERT INTO portfolio_table (user_id, portfolio_name) VALUES (1, 'Default Portfolio')"))
    op.execute(sa.text("INSERT INTO asset_table (stock_name, price) VALUES ('AAPL', 100), ('MSFT', 200)"))
    op.execute(sa.text("INSERT INTO holdings_table (stock_id, portfolio_id, quantity) VALUES (1, 1, 10), (2, 1, 5)"))


def downgrade() -> None:
    op.drop_table("transaction_table")
    op.drop_table("holdings_table")
    op.drop_table("asset_table")
    op.drop_table("portfolio_table")
    op.drop_table("user_table")

    
