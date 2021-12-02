from ..fragments import FRAGMENT_PRODUCT_CONNECTION

QUERY_ALL_PRODUCTS = (
    """
query AllProducts {
  allProducts {
    ...fragmentProductConnection
  }
}
"""
    + FRAGMENT_PRODUCT_CONNECTION
)
