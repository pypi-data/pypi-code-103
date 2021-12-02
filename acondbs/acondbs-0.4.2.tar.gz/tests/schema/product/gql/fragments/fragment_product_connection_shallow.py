from .fragment_product_shallow import FRAGMENT_PRODUCT_SHALLOW

FRAGMENT_PRODUCT_CONNECTION_SHALLOW = '''
fragment fragmentProductConnectionShallow on ProductConnection {
  edges {
    node {
     ...fragmentProductShallow
    }
  }
}
''' + FRAGMENT_PRODUCT_SHALLOW
