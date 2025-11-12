"""Add in_progress and reviewed to OrderStatus enum

Revision ID: 4cf07126a25f
Revises: 809a5ff95ac3
Create Date: 2025-10-09 11:56:29.029161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cf07126a25f'
down_revision: Union[str, Sequence[str], None] = '809a5ff95ac3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add in_progress and reviewed to ENUM column
    op.execute(
        "ALTER TABLE orders MODIFY status ENUM('pending','accepted','in_progress','completed','reviewed','cancelled')"
    )


def downgrade() -> None:
    # Remove in_progress and reviewed on rollback
    op.execute(
        "ALTER TABLE orders MODIFY status ENUM('pending','accepted','completed','cancelled')"
    )
