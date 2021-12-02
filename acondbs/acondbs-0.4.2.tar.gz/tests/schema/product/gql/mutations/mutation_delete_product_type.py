MUTATION_DELETE_PRODUCT_TYPE = '''
mutation DeleteProductType($typeId: Int!) {
  deleteProductType(typeId: $typeId) {
    ok
  }
}
'''
