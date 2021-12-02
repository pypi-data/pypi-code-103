from ..fragments import FRAGMENT_PRODUCT_CONNECTION_SHALLOW

QUERY_ALL_PRODUCTS_SHALLOW = (
    """
query AllProductsShallow(
  $filters: ProductFilter
  $sort: [ProductSortEnum]
  $first: Int
) {
  allProducts(filters: $filters, sort: $sort, first: $first) {
    ...fragmentProductConnectionShallow
  }
}
"""
    + FRAGMENT_PRODUCT_CONNECTION_SHALLOW
)
