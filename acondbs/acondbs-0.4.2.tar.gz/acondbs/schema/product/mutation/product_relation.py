import graphene

from .. import type_
from .... import ops


##__________________________________________________________________||
class CreateProductRelationInput(graphene.InputObjectType):
    """An input to createProductRelation()"""

    type_id = graphene.Int(
        required=True,
        description=(
            "The typeId of the product relation type of the relation "
            'from "self" to the "other"'
        ),
    )
    self_product_id = graphene.Int(
        required=True, description=("The productId of the self product")
    )
    other_product_id = graphene.Int(
        required=True, description=("The productId of the other product")
    )


##__________________________________________________________________||
class CreateProductRelation(graphene.Mutation):
    """Add relations between two products. The arguments only specify the relation
    from one product to the other. The reverse relation will be also added.

    """

    class Arguments:
        input = CreateProductRelationInput(required=True)

    ok = graphene.Boolean()
    product_relation = graphene.Field(lambda: type_.ProductRelation)

    def mutate(root, info, input):
        model = ops.create_product_relation(**input)
        ops.commit()
        ok = True
        return CreateProductRelation(product_relation=model, ok=ok)


class DeleteProductRelation(graphene.Mutation):
    """Remove relations from two products."""

    class Arguments:
        relation_id = graphene.Int(
            required=True,
            description=(
                "The relationId of a relation. The reverse relation "
                "will automatically be removed."
            ),
        )

    ok = graphene.Boolean()

    def mutate(root, info, relation_id):
        ops.delete_product_relation(relation_id)
        ops.commit()
        ok = True
        return DeleteProductRelation(ok=ok)


##__________________________________________________________________||
