QUERY_ALL_PRODUCTS_TOTAL_COUNT = """
query AllProductsTotalCount(
  $filters: ProductFilter
  $sort: [ProductSortEnum]
  $first: Int
) {
  allProducts(filters: $filters, sort: $sort, first: $first) {
    totalCount
  }
}
"""
