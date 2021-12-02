"""rename table web_config

Revision ID: 63790f65e724
Revises: 3f804a98ab06
Create Date: 2021-10-26 19:33:50.756208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "63790f65e724"
down_revision = "3f804a98ab06"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("web_config", "web_config_old")


def downgrade():
    op.rename_table("web_config_old", "web_config")
