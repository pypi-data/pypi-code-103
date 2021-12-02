QUERY_ALL_PRODUCT_FILE_PATHS = """
{
  allProductFilePaths {
    totalCount
    edges {
      node {
        pathId
        path
        note
        product {
          name
        }
      }
    }
  }
}
"""
