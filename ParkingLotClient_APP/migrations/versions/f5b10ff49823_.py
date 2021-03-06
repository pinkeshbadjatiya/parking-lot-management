"""empty message

Revision ID: f5b10ff49823
Revises: 9a98ad5c3bd3
Create Date: 2018-04-10 17:49:09.883917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5b10ff49823'
down_revision = '9a98ad5c3bd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('charge', 'pl_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'charge', 'parkinglot', ['pl_id'], ['id'])
    op.add_column('token', sa.Column('entry_operator_id', sa.String(length=50), nullable=False))
    op.add_column('token', sa.Column('exit_operator_id', sa.String(length=50), nullable=True))
    op.alter_column('token', 'charge_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'token', 'charge', ['charge_id'], ['charge_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'token', type_='foreignkey')
    op.alter_column('token', 'charge_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('token', 'exit_operator_id')
    op.drop_column('token', 'entry_operator_id')
    op.drop_constraint(None, 'charge', type_='foreignkey')
    op.alter_column('charge', 'pl_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
