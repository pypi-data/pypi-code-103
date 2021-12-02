import graphene

from alembic.migration import MigrationContext

from ..db.conn import get_db_connection


##__________________________________________________________________||
def resolve_version(parent, info):
    from .. import __version__

    return __version__


version_field = graphene.Field(
    graphene.String,
    description="The version of Acondbs",
    resolver=resolve_version,
)


##__________________________________________________________________||
def resolve_alembic_version(parent, info):
    conn = get_db_connection()
    context = MigrationContext.configure(conn)
    ret = context.get_current_revision()
    # e.g., "35e6ddccd22a"
    return ret


alembic_version_field = graphene.Field(
    graphene.String,
    description="The version of Alembic migration",
    resolver=resolve_alembic_version,
)

##__________________________________________________________________||
