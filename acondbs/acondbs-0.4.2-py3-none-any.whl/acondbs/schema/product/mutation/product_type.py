import graphene

from .. import type_

from .... import ops


##__________________________________________________________________||
class CommonInputFields:
    order = graphene.Int(
        description=(
            "The order in which the type is displayed, for example, "
            "in navigation bars."
        )
    )
    indef_article = graphene.String(
        description=(
            'The indefinite article placed before the singular noun "'
            'i.e., "a" or "an". '
        )
    )
    singular = graphene.String(
        description=("The singular noun, the product type name in singular.")
    )
    plural = graphene.String(
        description=("The plural noun, the product type name in plural.")
    )
    icon = graphene.String(
        description=(
            "A name of the icon from https://materialdesignicons.com/"
        )
    )
    field_ids = graphene.List(
        graphene.Int,
        description=("The field IDs")
    )


class CreateProductTypeInput(graphene.InputObjectType, CommonInputFields):
    """Input to createProductType()"""

    name = graphene.String(
        required=True, description="The name of the product type"
    )


class UpdateProductTypeInput(graphene.InputObjectType, CommonInputFields):
    """Input to updateProductType()"""

    name = graphene.String(description="The name of the product type")


##__________________________________________________________________||
class CreateProductType(graphene.Mutation):
    """Create a product type"""

    class Arguments:
        input = CreateProductTypeInput(required=True)

    ok = graphene.Boolean()
    product_type = graphene.Field(lambda: type_.ProductType)

    def mutate(root, info, input):
        model = ops.create_product_type(**input)
        ops.commit()
        ok = True
        return CreateProductType(product_type=model, ok=ok)


class UpdateProductType(graphene.Mutation):
    """Update a product type"""

    class Arguments:
        type_id = graphene.Int(required=True)
        input = UpdateProductTypeInput(required=True)

    ok = graphene.Boolean()
    product_type = graphene.Field(lambda: type_.ProductType)

    def mutate(root, info, type_id, input):
        model = ops.update_product_type(type_id, **input)
        ops.commit()
        ok = True
        return UpdateProductType(product_type=model, ok=ok)


class DeleteProductType(graphene.Mutation):
    """Delete a product type"""

    class Arguments:
        type_id = graphene.Int(description="The typeId of the product type")

    ok = graphene.Boolean()

    def mutate(root, info, type_id):
        ops.delete_product_type(type_id)
        ops.commit()
        ok = True
        return DeleteProductType(ok=ok)


##__________________________________________________________________||
