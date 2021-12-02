import graphene

from . import type_

from ... import ops


class SaveWebconfig(graphene.Mutation):
    class Arguments:
        json = graphene.String(required=True)

    ok = graphene.Boolean()
    web_config = graphene.Field(lambda: type_.WebConfig)

    def mutate(root, info, json):
        model = ops.save_web_config(json=json)
        ops.commit()
        ok = True
        return SaveWebconfig(web_config=model, ok=ok)
