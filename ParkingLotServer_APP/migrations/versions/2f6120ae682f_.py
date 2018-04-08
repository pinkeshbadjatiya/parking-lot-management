"""empty message

Revision ID: 2f6120ae682f
Revises: 9b35604b7044
Create Date: 2018-03-21 12:23:24.103356

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f6120ae682f'
down_revision = '9b35604b7044'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    sa.Column('plid', sa.Integer(), nullable=False),
    sa.Column('utildate', sa.Date(), nullable=False),
    sa.Column('utilperhour', sa.String(length=175), nullable=False),
    sa.Column('revperhour', sa.String(length=175), nullable=False),
    sa.Column('avgutil', sa.Float(), nullable=False),
    sa.Column('totalrev', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'plid'),
    sa.UniqueConstraint('utildate')
    )
    op.add_column(u'parkinglot', sa.Column('plactive', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'parkinglot', 'plactive')
    op.drop_table('utilization')
    op.drop_table('user')
    # ### end Alembic commands ###