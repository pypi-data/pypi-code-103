from ..fragments import FRAGMENT_PRODUCT_TYPE

MUTATION_UPDATE_PRODUCT_TYPE = '''
mutation UpdateProductType($typeId: Int!, $input: UpdateProductTypeInput!) {
  updateProductType(typeId: $typeId,input: $input) {
    ok
    productType {
      ...fragmentProductType
    }
  }
}
''' + FRAGMENT_PRODUCT_TYPE

