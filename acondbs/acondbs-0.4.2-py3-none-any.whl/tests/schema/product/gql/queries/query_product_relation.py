from ..fragments import FRAGMENT_PRODUCT_RELATION

QUERY_PRODUCT_RELATION = """
query ProductRelation($relationId: Int) {
  productRelation(relationId: $relationId) {
    ...fragmentProductRelation
  }
}
""" + FRAGMENT_PRODUCT_RELATION
