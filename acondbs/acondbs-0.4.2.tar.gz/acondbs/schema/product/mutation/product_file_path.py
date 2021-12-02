import graphene

from .. import type_
from .... import ops


##__________________________________________________________________||
class CommonInputFields:
    """Common input fields of mutations for creating and updating file paths"""

    path = graphene.String()
    note = graphene.String()


class CreateProductFilePathInput(graphene.InputObjectType, CommonInputFields):
    product_id = graphene.Int()


class UpdateProductFilePathInput(graphene.InputObjectType, CommonInputFields):
    pass


##__________________________________________________________________||
class CreateProductFilePath(graphene.Mutation):
    class Arguments:
        input = CreateProductFilePathInput(required=True)

    ok = graphene.Boolean()
    productFilePath = graphene.Field(lambda: type_.ProductFilePath)

    def mutate(root, info, input):
        model = ops.create_product_file_path(**input)
        ops.commit()
        ok = True
        return CreateProductFilePath(productFilePath=model, ok=ok)


class UpdateProductFilePath(graphene.Mutation):
    class Arguments:
        path_id = graphene.Int()
        input = UpdateProductFilePathInput(required=True)

    ok = graphene.Boolean()
    productFilePath = graphene.Field(lambda: type_.ProductFilePath)

    def mutate(root, info, path_id, input):
        model = ops.update_product_file_path(path_id, **input)
        ops.commit()
        ok = True
        return UpdateProductFilePath(productFilePath=model, ok=ok)


class DeleteProductFilePath(graphene.Mutation):
    class Arguments:
        path_id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(root, info, path_id):
        ops.delete_product_file_path(path_id)
        ops.commit()
        ok = True
        return DeleteProductFilePath(ok=ok)


##__________________________________________________________________||
