MUTATION_DELETE_PRODUCT_RELATION_TYPES = '''
mutation DeleteProductRelationTypes($typeId: Int!) {
  deleteProductRelationTypes(typeId: $typeId) {
    ok
  }
}
'''
