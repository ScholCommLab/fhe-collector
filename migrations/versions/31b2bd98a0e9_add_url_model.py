"""add Url model

Revision ID: 31b2bd98a0e9
Revises: f0e98c6a7fba
Create Date: 2019-01-22 21:58:19.905725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31b2bd98a0e9'
down_revision = '7eb1ec7367a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('url',
    sa.Column('url', sa.String(length=256), nullable=False),
    sa.Column('doi', sa.String(length=64), nullable=False),
    sa.Column('url_type', sa.String(length=64), nullable=True),
    sa.Column('url_source', sa.String(length=256), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['doi'], ['doi.doi'], ),
    sa.PrimaryKeyConstraint('url')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('url')
    # ### end Alembic commands ###
