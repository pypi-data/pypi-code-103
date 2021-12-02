import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from ...models import Log as LogModel

from ..connection import CountedConnection


##__________________________________________________________________||
class Log(SQLAlchemyObjectType):
    """Record of errors, etc."""

    class Meta:
        model = LogModel
        interfaces = (graphene.relay.Node,)
        connection_class = CountedConnection


##__________________________________________________________________||
