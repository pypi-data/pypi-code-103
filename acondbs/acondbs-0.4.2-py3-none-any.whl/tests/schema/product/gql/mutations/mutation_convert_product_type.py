from ..fragments import FRAGMENT_PRODUCT

MUTATION_CONVERT_PRODUCT_TYPE = (
    """
mutation($productId: Int!, $typeId: Int!) {
  convertProductType(productId: $productId, typeId: $typeId) {
    ok
    product {
      ...fragmentProduct
    }
  }
}
"""
    + FRAGMENT_PRODUCT
)
