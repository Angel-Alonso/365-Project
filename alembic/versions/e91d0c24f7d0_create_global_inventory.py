"""create global inventory

Revision ID: e91d0c24f7d0
Revises:
Create Date: 2025-03-30 11:23:36.782933

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e91d0c24f7d0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Potion-shop leftover migration (intentionally a no-op for the stock portfolio app).
    pass


def downgrade():
    pass
