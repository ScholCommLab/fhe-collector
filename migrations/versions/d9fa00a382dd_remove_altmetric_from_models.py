"""remove altmetric from models

Revision ID: d9fa00a382dd
Revises: 1a7a23887ebf
Create Date: 2018-10-17 16:25:32.748017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9fa00a382dd'
down_revision = '1a7a23887ebf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('altmetrics_response')
    op.add_column('publication', sa.Column('date_added', sa.DateTime(), nullable=True))
    op.add_column('publication', sa.Column('origin', sa.String(length=256), nullable=True))
    op.add_column('publication', sa.Column('pub_date', sa.DateTime(), nullable=True))
    op.drop_index('ix_publication_doi', table_name='publication')
    op.drop_column('publication', 'doi_resolve_status')
    op.drop_column('publication', 'pmc')
    op.drop_column('publication', 'pmid')
    op.drop_column('publication', 'date')
    op.drop_column('publication', 'url')
    op.drop_column('publication', 'doi_resolve_ts')
    op.drop_column('publication', 'doi_resolve_error')
    op.drop_column('publication', 'ncbi_ts')
    op.drop_column('publication', 'doi_url')
    op.drop_column('publication', 'id')
    op.drop_column('publication', 'ncbi_errmsg')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('publication', sa.Column('ncbi_errmsg', sa.VARCHAR(length=128), nullable=True))
    op.add_column('publication', sa.Column('id', sa.INTEGER(), nullable=False))
    op.add_column('publication', sa.Column('doi_url', sa.VARCHAR(length=128), nullable=True))
    op.add_column('publication', sa.Column('ncbi_ts', sa.DATE(), nullable=True))
    op.add_column('publication', sa.Column('doi_resolve_error', sa.VARCHAR(length=128), nullable=True))
    op.add_column('publication', sa.Column('doi_resolve_ts', sa.DATE(), nullable=True))
    op.add_column('publication', sa.Column('url', sa.VARCHAR(length=128), nullable=True))
    op.add_column('publication', sa.Column('date', sa.DATETIME(), nullable=True))
    op.add_column('publication', sa.Column('pmid', sa.VARCHAR(length=128), nullable=True))
    op.add_column('publication', sa.Column('pmc', sa.VARCHAR(length=128), nullable=True))
    op.add_column('publication', sa.Column('doi_resolve_status', sa.VARCHAR(length=128), nullable=True))
    op.create_index('ix_publication_doi', 'publication', ['doi'], unique=False)
    op.drop_column('publication', 'pub_date')
    op.drop_column('publication', 'origin')
    op.drop_column('publication', 'date_added')
    op.create_table('altmetrics_response',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###