"""rename table

Revision ID: 12cc2bed191c
Revises: a4105346b478
Create Date: 2021-09-22 15:04:45.975408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12cc2bed191c'
down_revision = 'a4105346b478'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('attribute_text', 'attribute_unicode_text')

def downgrade():
    op.rename_table('attribute_unicode_text', 'attribute_text')
