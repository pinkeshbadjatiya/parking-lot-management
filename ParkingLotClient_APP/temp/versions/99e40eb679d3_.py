"""empty message

Revision ID: 99e40eb679d3
Revises: 4f2bc6ab89a3
Create Date: 2018-03-27 19:40:25.088830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99e40eb679d3'
down_revision = '4f2bc6ab89a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('charge',
    sa.Column('charge_id', sa.Integer(), nullable=False),
    sa.Column('pl_id', sa.Integer(), nullable=False),
    sa.Column('price_snapshot', sa.String(length=2500), nullable=False),
    sa.Column('ch_active', sa.Boolean(), nullable=False),
    sa.Column('update_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('charge_id')
    )
    op.create_table('parkinglot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pl_name', sa.String(length=255), nullable=False),
    sa.Column('pl_address', sa.String(length=255), nullable=False),
    sa.Column('pl_capacity', sa.Integer(), nullable=False),
    sa.Column('pl_default_price', sa.Float(), nullable=False),
    sa.Column('pl_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('pl_name')
    )
    op.create_table('token',
    sa.Column('token_id', sa.Integer(), nullable=False),
    sa.Column('charge_id', sa.Integer(), nullable=False),
    sa.Column('vehicle_no', sa.String(length=200), nullable=False),
    sa.Column('computed_charge', sa.Float(), nullable=True),
    sa.Column('pay_method', sa.String(length=200), nullable=True),
    sa.Column('entry_date', sa.DateTime(), nullable=False),
    sa.Column('exit_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('token_id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('utilization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pl_id', sa.Integer(), nullable=True),
    sa.Column('util_date', sa.Date(), nullable=False),
    sa.Column('util_per_hour', sa.String(length=175), nullable=False),
    sa.Column('rev_per_hour', sa.String(length=175), nullable=False),
    sa.Column('avg_util', sa.Float(), nullable=False),
    sa.Column('total_rev', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['pl_id'], ['parkinglot.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('util_date')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('utilization')
    op.drop_table('user')
    op.drop_table('token')
    op.drop_table('parkinglot')
    op.drop_table('charge')
    # ### end Alembic commands ###