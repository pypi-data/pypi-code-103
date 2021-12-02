MUTATION_DELETE_PRODUCT = '''
mutation DeleteProduct($productId: Int!) {
  deleteProduct(productId: $productId) {
    ok
  }
}
'''
