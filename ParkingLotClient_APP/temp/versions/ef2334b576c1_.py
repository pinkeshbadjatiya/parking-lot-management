"""empty message

Revision ID: ef2334b576c1
Revises: 1c87381de94e
Create Date: 2018-03-26 00:19:10.669709

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ef2334b576c1'
down_revision = '1c87381de94e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token', 'computed_charge',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.alter_column('token', 'pay_method',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token', 'pay_method',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    op.alter_column('token', 'computed_charge',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    # ### end Alembic commands ###
