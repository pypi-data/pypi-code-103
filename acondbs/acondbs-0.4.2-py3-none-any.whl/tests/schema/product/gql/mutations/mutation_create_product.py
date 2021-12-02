from ..fragments import FRAGMENT_PRODUCT

MUTATION_CREATE_PRODUCT = '''
mutation CreateProduct($input: CreateProductInput!) {
  createProduct(input: $input) {
    ok
    product {
      ...fragmentProduct
    }
  }
}
''' + FRAGMENT_PRODUCT
