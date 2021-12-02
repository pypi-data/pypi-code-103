from ..fragments import FRAGMENT_PRODUCT_RELATION

MUTATION_CREATE_PRODUCT_RELATION = '''
mutation CreateProductRelation($input: CreateProductRelationInput!) {
  createProductRelation(input: $input) {
    ok
    productRelation {
      ...fragmentProductRelation
    }
  }
}
''' + FRAGMENT_PRODUCT_RELATION
