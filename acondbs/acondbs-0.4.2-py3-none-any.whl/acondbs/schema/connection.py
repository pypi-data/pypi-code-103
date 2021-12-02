from graphene import Int, NonNull
from graphene.relay import Connection


##__________________________________________________________________||
class CountedConnection(Connection):
    """

    copied from https://github.com/graphql-python/graphene-sqlalchemy/issues/153#issuecomment-501949939

    """

    class Meta:
        # Being abstract is important because we can't reference the
        # node type here without creating a circular reference. Also, it
        # makes reuse easy.
        #
        # The node type will be populated later with
        # `CountedConnection.create_class()` in `Foo`'s
        # `__init_subclass_with_meta__()`.
        abstract = True

    total_count = NonNull(Int)

    def resolve_total_count(self, info, **kwargs):
        return self.length


##__________________________________________________________________||
