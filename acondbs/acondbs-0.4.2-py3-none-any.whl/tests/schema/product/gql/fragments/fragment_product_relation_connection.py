from .fragment_product_relation import FRAGMENT_PRODUCT_RELATION

FRAGMENT_PRODUCT_RELATION_CONNECTION = '''
fragment fragmentProductRelationConnection on ProductRelationConnection {
  edges {
    node {
      ...fragmentProductRelation
    }
  }
}
''' + FRAGMENT_PRODUCT_RELATION
