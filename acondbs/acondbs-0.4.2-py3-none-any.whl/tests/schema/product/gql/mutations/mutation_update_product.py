from ..fragments import FRAGMENT_PRODUCT

MUTATION_UPDATE_PRODUCT = '''
mutation($productId: Int!, $input: UpdateProductInput!) {
  updateProduct(productId: $productId, input: $input) {
    ok
    product {
      ...fragmentProduct
    }
  }
}
''' + FRAGMENT_PRODUCT
