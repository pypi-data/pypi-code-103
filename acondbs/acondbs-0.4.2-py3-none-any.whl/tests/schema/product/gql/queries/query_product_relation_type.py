from ..fragments import FRAGMENT_PRODUCT_RELATION_TYPE

QUERY_PRODUCT_RELATION_TYPE = """
query ProductRelationType($typeId: Int, $name: String) {
  productRelationType(typeId: $typeId, name: $name) {
    ...fragmentProductRelationType
  }
}
""" + FRAGMENT_PRODUCT_RELATION_TYPE
