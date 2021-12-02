from ..fragments import FRAGMENT_PRODUCT_TYPE

MUTATION_CREATE_PRODUCT_TYPE = '''
mutation CreateProductType($input: CreateProductTypeInput!) {
  createProductType(input: $input) {
    ok
    productType {
      ...fragmentProductType
    }
  }
}
''' + FRAGMENT_PRODUCT_TYPE
