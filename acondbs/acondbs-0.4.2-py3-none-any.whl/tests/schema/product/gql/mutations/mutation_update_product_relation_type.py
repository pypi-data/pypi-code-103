from ..fragments import FRAGMENT_PRODUCT_RELATION_TYPE

MUTATION_UPDATE_PRODUCT_RELATION_TYPE = '''
mutation UpdateProductRelationType(
  $typeId: Int!
  $input: UpdateProductRelationTypeInput!
) {
  updateProductRelationType(typeId: $typeId, input: $input) {
    ok
    productRelationType {
      ...fragmentProductRelationType
    }
  }
}
''' + FRAGMENT_PRODUCT_RELATION_TYPE
