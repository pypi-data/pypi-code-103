FRAGMENT_PRODUCT = """
fragment fragmentProduct on Product {
  productId
  typeId
  type_ {
    typeId
    name
  }
  attributesUnicodeText {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  attributesBoolean {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  attributesInteger {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  attributesFloat {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  attributesDate {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  attributesDateTime {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  attributesTime {
    edges {
      node {
        typeFieldAssociation {
          field {
            name
            type_
          }
        }
        field {
          name
          type_
        }
        value
      }
    }
  }
  name
  timePosted
  postingGitHubUser {
    login
  }
  timeUpdated
  updatingGitHubUser {
    login
  }
  paths {
    edges {
      node {
        pathId
        path
        note
      }
    }
  }
  relations {
    edges {
      node {
        relationId
        typeId
        type_ {
          typeId
          name
        }
        otherProductId
        other {
          productId
          typeId
          type_ {
            typeId
            name
          }
          name
        }
        reverseRelationId
        reverse {
          relationId
          typeId
          type_ {
            typeId
            name
          }
        }
      }
    }
  }
  note
}
"""
