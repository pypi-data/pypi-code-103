FRAGMENT_PRODUCT_RELATION_TYPE = '''
fragment fragmentProductRelationType on ProductRelationType {
  typeId
  name
  indefArticle
  singular
  plural
  reverse {
    typeId
    name
  }
  relations {
    edges {
      node {
        self_ {
          productId
          name
        }
        other {
          productId
          name
        }
      }
    }
  }
}
'''
