"""change transaction structure. send_from instead wallet collumn

Revision ID: 396f9ed9bcd1
Revises: 5477c397567a
Create Date: 2024-04-13 13:21:01.071750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '396f9ed9bcd1'
down_revision: Union[str, None] = '5477c397567a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('send_from', sa.String(length=100), nullable=False))
    op.alter_column('transaction', 'send_to',
               existing_type=sa.VARCHAR(length=70),
               type_=sa.String(length=100),
               existing_nullable=False)
    op.drop_constraint('transaction_wallet_id_fkey', 'transaction', type_='foreignkey')
    op.drop_column('transaction', 'wallet_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('wallet_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('transaction_wallet_id_fkey', 'transaction', 'wallet', ['wallet_id'], ['id'])
    op.alter_column('transaction', 'send_to',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=70),
               existing_nullable=False)
    op.drop_column('transaction', 'send_from')
    # ### end Alembic commands ###