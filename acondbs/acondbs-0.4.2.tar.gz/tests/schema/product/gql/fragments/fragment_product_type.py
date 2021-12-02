FRAGMENT_PRODUCT_TYPE = '''
fragment fragmentProductType on ProductType {
  typeId
  name
  order
  indefArticle
  singular
  plural
  icon
  fields {
    edges {
      node {
        type_ {
          name
        }
        field {
          name
          type_
        }
      }
    }
  }
  products {
    edges {
      node {
        name
      }
    }
  }
}
'''
