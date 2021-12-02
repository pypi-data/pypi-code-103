import graphene

from . import type_

from ... import ops


class CreateLogInput(graphene.InputObjectType):
    """Input to createLog()"""

    id_ = graphene.Int()
    level = graphene.String(description="The log level")
    message = graphene.String(description="The message")


class CreateLog(graphene.Mutation):
    """Create a log"""

    class Arguments:
        input = CreateLogInput(required=True)

    ok = graphene.Boolean()
    log = graphene.Field(lambda: type_.Log)

    def mutate(root, info, input):
        model = ops.create_log(**input)
        ops.commit()
        ok = True
        return CreateLog(log=model, ok=ok)


class DeleteLog(graphene.Mutation):
    """Delete a log"""

    class Arguments:
        id_ = graphene.Int(description="The id of the log")

    ok = graphene.Boolean()

    def mutate(root, info, id_):
        ops.delete_log(id_=id_)
        ops.commit()
        ok = True
        return DeleteLog(ok=ok)
