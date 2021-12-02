MUTATION_DELETE_PRODUCT_RELATION = '''
mutation DeleteProductRelation($relationId: Int!) {
  deleteProductRelation(relationId: $relationId) {
    ok
  }
}
'''
