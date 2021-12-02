FRAGMENT_PRODUCT_RELATION = '''
fragment fragmentProductRelation on ProductRelation {
  relationId
  type_ {
    typeId
    name
  }
  self_ {
    productId
    name
  }
  other {
    productId
    name
  }
  reverse {
    relationId
  }
}
'''
