"""add user biography

Revision ID: 27920f03ed04
Revises: 711bbb2cd282
Create Date: 2024-01-22 23:41:18.473078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27920f03ed04'
down_revision: Union[str, None] = '711bbb2cd282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'biography')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('biography', sa.TEXT(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###