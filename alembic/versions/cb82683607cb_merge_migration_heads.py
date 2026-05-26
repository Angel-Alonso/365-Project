"""Compatibility no-op for previously deployed merge revision.

Revision ID: cb82683607cb
Revises: a4a6e9d8af8d
Create Date: 2026-05-05 00:11:58.830985

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "cb82683607cb"
down_revision: Union[str, None] = "a4a6e9d8af8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recognize databases that already recorded this historical revision."""
    pass


def downgrade() -> None:
    """No schema changes were introduced by this compatibility revision."""
    pass
