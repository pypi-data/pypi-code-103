from .fragment_product_relation_type import FRAGMENT_PRODUCT_RELATION_TYPE

FRAGMENT_PRODUCT_RELATION_TYPE_CONNECTION = '''
fragment fragmentProductRelationTypeConnection on ProductRelationTypeConnection {
  edges {
    node {
      ...fragmentProductRelationType
    }
  }
}
''' + FRAGMENT_PRODUCT_RELATION_TYPE
