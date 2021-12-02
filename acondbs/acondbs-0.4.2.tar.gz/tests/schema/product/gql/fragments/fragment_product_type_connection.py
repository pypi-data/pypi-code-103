from .fragment_product_type import FRAGMENT_PRODUCT_TYPE

FRAGMENT_PRODUCT_TYPE_CONNECTION = '''
fragment fragmentProductTypeConnection on ProductTypeConnection {
  totalCount
  edges {
    node {
      ...fragmentProductType
    }
  }
}
''' + FRAGMENT_PRODUCT_TYPE
