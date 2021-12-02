from ..fragments import FRAGMENT_PRODUCT

QUERY_PRODUCT = (
    """
query Product($productId: Int, $typeId: Int, $name: String) {
  product(productId: $productId, typeId: $typeId, name: $name) {
    ...fragmentProduct
  }
}
"""
    + FRAGMENT_PRODUCT
)
