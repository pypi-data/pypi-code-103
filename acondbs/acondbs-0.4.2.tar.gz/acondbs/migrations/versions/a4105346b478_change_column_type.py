"""change column type

Revision ID: a4105346b478
Revises: e077a31ad00b
Create Date: 2021-09-22 14:57:25.293805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4105346b478"
down_revision = "e077a31ad00b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("attribute_text", schema=None) as batch_op:
        batch_op.alter_column(
            "value", type_=sa.UnicodeText(), existing_type=sa.Text()
        )


def downgrade():
    pass
