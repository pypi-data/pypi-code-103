import graphene

from ...funcs import get_git_hub_viewer_from_info
from .. import type_

from .... import ops


##__________________________________________________________________||
def _reshape_arg_attributes(attributes):
    ret = {e["field_id"]: e["value"] for t, v in attributes.items() for e in v}
    return ret


##__________________________________________________________________||
class RelationInputFields(graphene.InputObjectType):
    """A relation to another product"""

    product_id = graphene.Int(
        required=True,
        description="The product ID of the other product",
    )
    type_id = graphene.Int(
        required=True,
        description="The relation type ID",
    )


class AttributeUnicodeTextInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.String(
        description="The value of the attribute",
    )


class AttributeBooleanInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.Boolean(
        description="The value of the attribute",
    )


class AttributeIntegerInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.Int(
        description="The value of the attribute",
    )


class AttributeFloatInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.Float(
        description="The value of the attribute",
    )


class AttributeDateInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.Date(
        description="The value of the attribute",
    )


class AttributeDateTimeInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.DateTime(
        description="The value of the attribute",
    )


class AttributeTimeInputFields(graphene.InputObjectType):
    field_id = graphene.Int(
        required=True,
        description="The field ID of the attribute",
    )
    value = graphene.Time(
        description="The value of the attribute",
    )


class AttributesInputFields(graphene.InputObjectType):
    unicode_text = graphene.InputField(
        graphene.List(AttributeUnicodeTextInputFields),
        description=("Attributes of type unicode text"),
    )
    boolean = graphene.InputField(
        graphene.List(AttributeBooleanInputFields),
        description=("Attributes of type boolean"),
    )
    integer = graphene.InputField(
        graphene.List(AttributeIntegerInputFields),
        description=("Attributes of type integer"),
    )
    float = graphene.InputField(
        graphene.List(AttributeFloatInputFields),
        description=("Attributes of type float"),
    )
    date = graphene.InputField(
        graphene.List(AttributeDateInputFields),
        description=("Attributes of type date"),
    )
    date_time = graphene.InputField(
        graphene.List(AttributeDateTimeInputFields),
        description=("Attributes of type date time"),
    )
    time = graphene.InputField(
        graphene.List(AttributeTimeInputFields),
        description=("Attributes of type time"),
    )


class CommonInputFields:
    """Common input fields of mutations for creating and updating products"""

    note = graphene.String(
        description="Note about the product in MarkDown.",
    )
    paths = graphene.List(
        graphene.String,
        description="Paths to the products. e.g., nersc:/go/to/my/product_v3",
    )
    relations = graphene.InputField(
        graphene.List(RelationInputFields),
        description=("Relations to other products"),
    )
    attributes = graphene.InputField(
        AttributesInputFields,
        description="Attributes",
    )


class CreateProductInput(graphene.InputObjectType, CommonInputFields):
    """Input to createProduct()"""

    type_id = graphene.Int(
        required=True,
        description="The product type ID",
    )
    name = graphene.String(
        required=True,
        description="The name of the product",
    )


class UpdateProductInput(graphene.InputObjectType, CommonInputFields):
    """Input to updateProduct()"""

    name = graphene.String(
        description="The name of the product",
    )


##__________________________________________________________________||
class CreateProduct(graphene.Mutation):
    """Create a product"""

    class Arguments:
        input = CreateProductInput(
            required=True,
            description="the input to createProduct()",
        )

    ok = graphene.Boolean()
    product = graphene.Field(lambda: type_.Product)

    def mutate(root, info, input):

        viewer = get_git_hub_viewer_from_info(info)
        posting_git_hub_user_id = viewer.user_id

        attributes = input.pop("attributes", {})
        attributes = _reshape_arg_attributes(attributes)

        model = ops.create_product(
            attributes=attributes,
            posting_git_hub_user_id=posting_git_hub_user_id,
            **input
        )

        ops.commit()
        ok = True
        return CreateProduct(product=model, ok=ok)


class UpdateProduct(graphene.Mutation):
    """Update a product.

    Note: This is to update the DB entry about a product. If the
    product itself has been updated, a new entry should be added by
    createProduct()
    """

    class Arguments:
        product_id = graphene.Int(
            required=True,
            description="The productId of a product to be updated.",
        )
        input = UpdateProductInput(
            required=True,
            description="an input to updateProduct()",
        )

    ok = graphene.Boolean()
    product = graphene.Field(lambda: type_.Product)

    def mutate(root, info, product_id, input):

        viewer = get_git_hub_viewer_from_info(info)
        updating_git_hub_user_id = viewer.user_id

        attributes = input.pop("attributes", {})
        attributes = _reshape_arg_attributes(attributes)

        model = ops.update_product(
            product_id=product_id,
            attributes=attributes,
            updating_git_hub_user_id=updating_git_hub_user_id,
            **input
        )
        ops.commit()
        ok = True
        return UpdateProduct(product=model, ok=ok)


class DeleteProduct(graphene.Mutation):
    """Delete a product"""

    class Arguments:
        product_id = graphene.Int(
            required=True,
            description="The productId of a product to be deleted.",
        )

    ok = graphene.Boolean()

    def mutate(root, info, product_id):
        ops.delete_product(product_id)
        ops.commit()
        ok = True
        return DeleteProduct(ok=ok)


##__________________________________________________________________||
class ConvertProductType(graphene.Mutation):
    """Convert the product type of a product"""

    class Arguments:
        product_id = graphene.Int(
            required=True,
            description="The productId of a product to be converted.",
        )
        type_id = graphene.Int(
            required=True,
            description="The typeId of new product type.",
        )

    ok = graphene.Boolean()
    product = graphene.Field(lambda: type_.Product)

    def mutate(root, info, product_id, type_id):
        viewer = get_git_hub_viewer_from_info(info)
        updating_git_hub_user_id = viewer.user_id
        model = ops.convert_product_type(
            product_id,
            type_id,
            updating_git_hub_user_id=updating_git_hub_user_id,
        )
        ops.commit()
        ok = True
        return ConvertProductType(ok=ok, product=model)


##__________________________________________________________________||
