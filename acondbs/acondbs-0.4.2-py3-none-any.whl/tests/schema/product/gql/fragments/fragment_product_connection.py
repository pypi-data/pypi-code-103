from .fragment_product import FRAGMENT_PRODUCT

FRAGMENT_PRODUCT_CONNECTION = '''
fragment fragmentProductConnection on ProductConnection {
  edges {
    node {
     ...fragmentProduct
    }
  }
}
''' + FRAGMENT_PRODUCT
