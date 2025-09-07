"""initial migration (scaffold)

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-07
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated ###
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('users')
