from ..fragments import FRAGMENT_PRODUCT_SHALLOW

QUERY_PRODUCT_SHALLOW = (
    """
query ProductShallow($productId: Int, $typeId: Int, $name: String) {
  product(productId: $productId, typeId: $typeId, name: $name) {
    ...fragmentProductShallow
  }
}
"""
    + FRAGMENT_PRODUCT_SHALLOW
)
