"""merge migration heads

Revision ID: cb82683607cb
Revises: a4a6e9d8af8d, e91d0c24f7d0
Create Date: 2026-05-05 00:11:58.830985

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb82683607cb'
down_revision: Union[str, None] = ('a4a6e9d8af8d', 'e91d0c24f7d0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
