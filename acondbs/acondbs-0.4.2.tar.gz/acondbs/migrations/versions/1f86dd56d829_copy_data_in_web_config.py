"""copy data in web_config

Revision ID: 1f86dd56d829
Revises: 3746a752f344
Create Date: 2021-10-27 16:22:41.444462

"""
from alembic import op

from sqlalchemy.orm.session import Session

from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

# revision identifiers, used by Alembic.
revision = "1f86dd56d829"
down_revision = "3746a752f344"
branch_labels = None
depends_on = None


#
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

sa = SQLAlchemy(metadata=metadata)


class WebConfig(sa.Model):
    __tablename__ = "web_config"
    id_ = sa.Column(sa.Integer(), primary_key=True)
    json = sa.Column(sa.Text())


class WebConfigOld(sa.Model):
    __tablename__ = "web_config_old"
    config_id = sa.Column(sa.Integer(), primary_key=True)
    head_title = sa.Column(sa.Text())
    toolbar_title = sa.Column(sa.Text())
    devtool_loadingstate = sa.Column(sa.Boolean())
    product_creation_dialog = sa.Column(sa.Boolean())
    product_update_dialog = sa.Column(sa.Boolean())
    product_deletion_dialog = sa.Column(sa.Boolean())


def upgrade():
    import json

    session = Session(bind=op.get_bind())

    with session.no_autoflush:
        olds = session.query(WebConfigOld).all()

        for o in olds:
            config_json = json.dumps(
                {
                    "headTitle": o.head_title,
                    "toolbarTitle": o.toolbar_title,
                    "devtoolLoadingstate": o.devtool_loadingstate,
                    "productCreationDialog": o.product_deletion_dialog,
                    "productUpdateDialog": o.product_update_dialog,
                    "productDeletionDialog": o.product_deletion_dialog,
                }
            )
            n = WebConfig(id_=o.config_id, json=config_json)
            session.add(n)
    session.commit()


def downgrade():
    session = Session(bind=op.get_bind())
    session.query(WebConfig).delete()
    session.commit()
