"""empty message

Revision ID: 9b35604b7044
Revises: fb70cb0889ec
Create Date: 2018-03-21 11:56:06.948688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b35604b7044'
down_revision = 'fb70cb0889ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('parkinglot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plname', sa.String(length=255), nullable=False),
    sa.Column('pladdress', sa.String(length=255), nullable=False),
    sa.Column('plcapacity', sa.Integer(), nullable=False),
    sa.Column('pldefaultprice', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('plname')
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('parkinglot')
    # ### end Alembic commands ###
