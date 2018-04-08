"""empty message

Revision ID: 7489f3f18da3
Revises: 27ee3092f453
Create Date: 2018-04-05 11:16:33.386859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7489f3f18da3'
down_revision = '27ee3092f453'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hourly_util',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('util_date', sa.Date(), nullable=False),
    sa.Column('util_hour', sa.Integer(), nullable=False),
    sa.Column('util', sa.Float(), nullable=False),
    sa.Column('rev', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hourly_util')
    # ### end Alembic commands ###
