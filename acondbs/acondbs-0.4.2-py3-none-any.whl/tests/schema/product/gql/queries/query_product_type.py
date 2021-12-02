from ..fragments import FRAGMENT_PRODUCT_TYPE

QUERY_PRODUCT_TYPE = (
    """
query ProductType($typeId: Int, $name: String) {
  productType(typeId: $typeId, name: $name) {
    ...fragmentProductType
  }
}
"""
    + FRAGMENT_PRODUCT_TYPE
)
