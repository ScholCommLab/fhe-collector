"""add url creation attributes to Doi()

Revision ID: 4ee0b4c33912
Revises: 1298d4abb0d2
Create Date: 2019-08-02 16:28:49.063556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ee0b4c33912'
down_revision = '1298d4abb0d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=512), nullable=False),
    sa.Column('request_url', sa.String(length=512), nullable=True),
    sa.Column('request_type', sa.String(length=32), nullable=True),
    sa.Column('response', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['url'], ['url.url'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('doi', sa.Column('doi_lp', sa.Boolean(), nullable=True))
    op.add_column('doi', sa.Column('doi_new', sa.Boolean(), nullable=True))
    op.add_column('doi', sa.Column('doi_old', sa.Boolean(), nullable=True))
    op.add_column('doi', sa.Column('ncbi', sa.Boolean(), nullable=True))
    op.add_column('doi', sa.Column('unpaywall', sa.Boolean(), nullable=True))
    op.alter_column('url', 'url_type',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('url', 'url_type',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    op.drop_column('doi', 'unpaywall')
    op.drop_column('doi', 'ncbi')
    op.drop_column('doi', 'doi_old')
    op.drop_column('doi', 'doi_new')
    op.drop_column('doi', 'doi_lp')
    op.drop_table('api_request')
    # ### end Alembic commands ###