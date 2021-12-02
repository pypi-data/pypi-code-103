import graphene

from .. import type_

from .... import ops


##__________________________________________________________________||
class CommonInputFields:
    indef_article = graphene.String(
        description=(
            'The indefinite article placed before the singular noun "'
            'i.e., "a" or "an". '
        )
    )
    singular = graphene.String(
        description=("The singular noun, the relation type name in singular.")
    )
    plural = graphene.String(
        description=("The plural noun, the relation type name in plural.")
    )


class CreateProductRelationTypeInput(
    graphene.InputObjectType, CommonInputFields
):
    """An input to createProductRelationTypes()"""

    name = graphene.String(
        required=True, description=("The name of the relation type")
    )


class UpdateProductRelationTypeInput(
    graphene.InputObjectType, CommonInputFields
):
    """An input to updateProductRelationType()"""


##__________________________________________________________________||
class CreateProductRelationTypes(graphene.Mutation):
    """Create a pair of product relation types"""

    class Arguments:
        type = CreateProductRelationTypeInput(
            required=True, description=("A relation type")
        )
        reverse = CreateProductRelationTypeInput(
            description=("The reverse relation type")
        )
        self_reverse = graphene.Boolean(
            description=("true if the reverse type is the same")
        )

    ok = graphene.Boolean()
    product_relation_type = graphene.Field(lambda: type_.ProductRelationType)

    def mutate(root, info, type, reverse=None, self_reverse=False):
        model = ops.create_product_relation_type(type, reverse, self_reverse)
        ops.commit()
        ok = True
        return CreateProductRelationTypes(product_relation_type=model, ok=ok)


class UpdateProductRelationType(graphene.Mutation):
    """Update a product relation type"""

    class Arguments:
        type_id = graphene.Int(
            required=True,
            description=("The typeId of the product relation type"),
        )
        input = UpdateProductRelationTypeInput(required=True)

    ok = graphene.Boolean()
    product_relation_type = graphene.Field(lambda: type_.ProductRelationType)

    def mutate(root, info, type_id, input):
        model = ops.update_product_relation_type(type_id, **input)
        ops.commit()
        ok = True
        return UpdateProductRelationType(product_relation_type=model, ok=ok)


class DeleteProductRelationTypes(graphene.Mutation):
    """Delete a pair of product relation types"""

    class Arguments:
        type_id = graphene.Int(
            required=True,
            description=(
                "The typeId of a relation type. The reverse relation "
                "type will automatically be deleted."
            ),
        )

    ok = graphene.Boolean()

    def mutate(root, info, type_id):
        ops.delete_product_relation_type(type_id)
        ops.commit()
        ok = True
        return DeleteProductRelationTypes(ok=ok)


##__________________________________________________________________||
