from ..fragments import FRAGMENT_PRODUCT_RELATION_TYPE

MUTATION_CREATE_PRODUCT_RELATION_TYPES = '''
mutation CreateProductRelationTypes(
  $type: CreateProductRelationTypeInput!
  $reverse: CreateProductRelationTypeInput
  $selfReverse: Boolean
) {
  createProductRelationTypes(
    type: $type
    reverse: $reverse
    selfReverse: $selfReverse
  ) {
    ok
    productRelationType {
      ...fragmentProductRelationType
    }
  }
}
''' + FRAGMENT_PRODUCT_RELATION_TYPE
