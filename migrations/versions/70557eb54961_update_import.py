"""update import

Revision ID: 70557eb54961
Revises: 0d85a668b602
Create Date: 2020-10-09 01:55:15.384110

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '70557eb54961'
down_revision = '0d85a668b602'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doi', sa.String(length=64), nullable=False),
    sa.Column('request_url', sa.String(length=512), nullable=True),
    sa.Column('request_type', sa.String(length=32), nullable=True),
    sa.Column('response_content', sa.Text(), nullable=True),
    sa.Column('response_status', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['doi'], ['doi.doi'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('api_request')
    op.add_column('import', sa.Column('import_end', sa.DateTime(), nullable=True))
    op.add_column('import', sa.Column('import_start', sa.DateTime(), nullable=False))
    op.drop_column('import', 'imported_at')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('import', sa.Column('imported_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('import', 'import_start')
    op.drop_column('import', 'import_end')
    op.create_table('api_request',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('doi', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('request_url', sa.VARCHAR(length=512), autoincrement=False, nullable=True),
    sa.Column('request_type', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('response_content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('response_status', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['doi'], ['doi.doi'], name='api_request_doi_fkey'),
    sa.PrimaryKeyConstraint('id', name='api_request_pkey')
    )
    op.drop_table('request')
    # ### end Alembic commands ###