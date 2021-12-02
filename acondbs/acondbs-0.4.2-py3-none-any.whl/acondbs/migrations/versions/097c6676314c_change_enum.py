"""change enum

Revision ID: 097c6676314c
Revises: 12cc2bed191c
Create Date: 2021-09-22 15:43:27.796307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "097c6676314c"
down_revision = "12cc2bed191c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("field", schema=None) as batch_op:
        batch_op.alter_column(
            "type_",
            type_=sa.Enum(
                "UnicodeText",
                "Boolean",
                "Integer",
                "Float",
                "Date",
                "DateTime",
                "Time",
                name="fieldtype",
            ),
            existing_type=sa.Enum(
                "UnicodeText",
                "Boolean",
                "Int",
                "Float",
                "Date",
                "DateTime",
                "Time",
                name="fieldtype",
            ),
        )


def downgrade():
    pass
