from ..fragments import FRAGMENT_PRODUCT_TYPE_CONNECTION

QUERY_ALL_PRODUCT_TYPES = (
    """
query AllProductTypes($sort: [ProductTypeSortEnum] = [ORDER_ASC]) {
  allProductTypes(sort: $sort) {
    ...fragmentProductTypeConnection
  }
}
"""
    + FRAGMENT_PRODUCT_TYPE_CONNECTION
)
