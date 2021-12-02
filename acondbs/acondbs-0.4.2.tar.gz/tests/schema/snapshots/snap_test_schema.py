# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_schema[admin] 1'] = {
    'data': {
        '__schema': {
            'mutationType': {
                'fields': [
                    {
                        'name': 'authenticateWithGitHub'
                    },
                    {
                        'name': 'createLog'
                    },
                    {
                        'name': 'createProduct'
                    },
                    {
                        'name': 'deleteProduct'
                    },
                    {
                        'name': 'updateProduct'
                    },
                    {
                        'name': 'convertProductType'
                    },
                    {
                        'name': 'createProductFilePath'
                    },
                    {
                        'name': 'deleteProductFilePath'
                    },
                    {
                        'name': 'updateProductFilePath'
                    },
                    {
                        'name': 'createProductRelation'
                    },
                    {
                        'name': 'deleteProductRelation'
                    },
                    {
                        'name': 'createProductRelationTypes'
                    },
                    {
                        'name': 'deleteProductRelationTypes'
                    },
                    {
                        'name': 'updateProductRelationType'
                    },
                    {
                        'name': 'createProductType'
                    },
                    {
                        'name': 'deleteProductType'
                    },
                    {
                        'name': 'updateProductType'
                    },
                    {
                        'name': 'createField'
                    },
                    {
                        'name': 'deleteField'
                    },
                    {
                        'name': 'updateField'
                    },
                    {
                        'name': 'addGitHubOrg'
                    },
                    {
                        'name': 'deleteGitHubOrg'
                    },
                    {
                        'name': 'addGitHubAdminAppToken'
                    },
                    {
                        'name': 'deleteGitHubAdminAppToken'
                    },
                    {
                        'name': 'updateGitHubOrgMemberLists'
                    },
                    {
                        'name': 'deleteLog'
                    },
                    {
                        'name': 'saveWebConfig'
                    }
                ]
            },
            'queryType': {
                'fields': [
                    {
                        'name': 'webConfig'
                    },
                    {
                        'name': 'isSignedIn'
                    },
                    {
                        'name': 'gitHubOAuthAppInfo'
                    },
                    {
                        'name': 'version'
                    },
                    {
                        'name': 'alembicVersion'
                    },
                    {
                        'name': 'isAdmin'
                    },
                    {
                        'name': 'gitHubViewer'
                    },
                    {
                        'name': 'allProducts'
                    },
                    {
                        'name': 'allProductTypes'
                    },
                    {
                        'name': 'allProductRelations'
                    },
                    {
                        'name': 'allProductRelationTypes'
                    },
                    {
                        'name': 'allProductFilePaths'
                    },
                    {
                        'name': 'allFields'
                    },
                    {
                        'name': 'product'
                    },
                    {
                        'name': 'productType'
                    },
                    {
                        'name': 'productRelation'
                    },
                    {
                        'name': 'productRelationType'
                    },
                    {
                        'name': 'field'
                    },
                    {
                        'name': 'node'
                    },
                    {
                        'name': 'allGitHubOrgs'
                    },
                    {
                        'name': 'allGitHubUsers'
                    },
                    {
                        'name': 'allGitHubTokens'
                    },
                    {
                        'name': 'allLogs'
                    },
                    {
                        'name': 'log'
                    }
                ]
            },
            'subscriptionType': None,
            'types': [
                {
                    'fields': [
                        {
                            'name': 'webConfig'
                        },
                        {
                            'name': 'isSignedIn'
                        },
                        {
                            'name': 'gitHubOAuthAppInfo'
                        },
                        {
                            'name': 'version'
                        },
                        {
                            'name': 'alembicVersion'
                        },
                        {
                            'name': 'isAdmin'
                        },
                        {
                            'name': 'gitHubViewer'
                        },
                        {
                            'name': 'allProducts'
                        },
                        {
                            'name': 'allProductTypes'
                        },
                        {
                            'name': 'allProductRelations'
                        },
                        {
                            'name': 'allProductRelationTypes'
                        },
                        {
                            'name': 'allProductFilePaths'
                        },
                        {
                            'name': 'allFields'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'productType'
                        },
                        {
                            'name': 'productRelation'
                        },
                        {
                            'name': 'productRelationType'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'allGitHubOrgs'
                        },
                        {
                            'name': 'allGitHubUsers'
                        },
                        {
                            'name': 'allGitHubTokens'
                        },
                        {
                            'name': 'allLogs'
                        },
                        {
                            'name': 'log'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'QueryAdmin'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'json'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'WebConfig'
                },
                {
                    'fields': [
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'INTERFACE',
                    'name': 'Node'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'ID'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'String'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Boolean'
                },
                {
                    'fields': [
                        {
                            'name': 'clientId'
                        },
                        {
                            'name': 'authorizeUrl'
                        },
                        {
                            'name': 'redirectUri'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOAuthAppInfo'
                },
                {
                    'fields': [
                        {
                            'name': 'userId'
                        },
                        {
                            'name': 'gitHubId'
                        },
                        {
                            'name': 'login'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'avatarUrl'
                        },
                        {
                            'name': 'url'
                        },
                        {
                            'name': 'postedProducts'
                        },
                        {
                            'name': 'updatedProducts'
                        },
                        {
                            'name': 'tokens'
                        },
                        {
                            'name': 'memberships'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubUser'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'hasNextPage'
                        },
                        {
                            'name': 'hasPreviousPage'
                        },
                        {
                            'name': 'startCursor'
                        },
                        {
                            'name': 'endCursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'PageInfo'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'timePosted'
                        },
                        {
                            'name': 'postingGitHubUserId'
                        },
                        {
                            'name': 'timeUpdated'
                        },
                        {
                            'name': 'updatingGitHubUserId'
                        },
                        {
                            'name': 'note'
                        },
                        {
                            'name': 'type_'
                        },
                        {
                            'name': 'postingGitHubUser'
                        },
                        {
                            'name': 'updatingGitHubUser'
                        },
                        {
                            'name': 'paths'
                        },
                        {
                            'name': 'relations'
                        },
                        {
                            'name': 'attributesUnicodeText'
                        },
                        {
                            'name': 'attributesBoolean'
                        },
                        {
                            'name': 'attributesInteger'
                        },
                        {
                            'name': 'attributesFloat'
                        },
                        {
                            'name': 'attributesDate'
                        },
                        {
                            'name': 'attributesDateTime'
                        },
                        {
                            'name': 'attributesTime'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Product'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Int'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'DateTime'
                },
                {
                    'fields': [
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'order'
                        },
                        {
                            'name': 'indefArticle'
                        },
                        {
                            'name': 'singular'
                        },
                        {
                            'name': 'plural'
                        },
                        {
                            'name': 'icon'
                        },
                        {
                            'name': 'products'
                        },
                        {
                            'name': 'fields'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'ProductFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'TypeFieldAssociationConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'TypeFieldAssociationEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'order'
                        },
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'type_'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'attributesUnicodeText'
                        },
                        {
                            'name': 'attributesBoolean'
                        },
                        {
                            'name': 'attributesInteger'
                        },
                        {
                            'name': 'attributesFloat'
                        },
                        {
                            'name': 'attributesDate'
                        },
                        {
                            'name': 'attributesDateTime'
                        },
                        {
                            'name': 'attributesTime'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'TypeFieldAssociation'
                },
                {
                    'fields': [
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'attributesUnicodeText'
                        },
                        {
                            'name': 'attributesBoolean'
                        },
                        {
                            'name': 'attributesInteger'
                        },
                        {
                            'name': 'attributesFloat'
                        },
                        {
                            'name': 'attributesDate'
                        },
                        {
                            'name': 'attributesDateTime'
                        },
                        {
                            'name': 'attributesTime'
                        },
                        {
                            'name': 'entryTypes'
                        },
                        {
                            'name': 'id'
                        },
                        {
                            'name': 'type_'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Field'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeUnicodeTextConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeUnicodeTextEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeUnicodeText'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeUnicodeTextSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeBooleanConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeBooleanEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeBoolean'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeBooleanSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeIntegerConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeIntegerEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeInteger'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeIntegerSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeFloatConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeFloatEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeFloat'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Float'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeFloatSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDate'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeDateSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateTimeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateTimeEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateTime'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeDateTimeSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeTimeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeTimeEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeTime'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeTimeSortEnum'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'TypeFieldAssociationSortEnum'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'FieldType'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductFilePathConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductFilePathEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'pathId'
                        },
                        {
                            'name': 'path'
                        },
                        {
                            'name': 'note'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductFilePath'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductFilePathSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'relationId'
                        },
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'selfProductId'
                        },
                        {
                            'name': 'otherProductId'
                        },
                        {
                            'name': 'reverseRelationId'
                        },
                        {
                            'name': 'type_'
                        },
                        {
                            'name': 'self_'
                        },
                        {
                            'name': 'other'
                        },
                        {
                            'name': 'reverse'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelation'
                },
                {
                    'fields': [
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'reverseTypeId'
                        },
                        {
                            'name': 'indefArticle'
                        },
                        {
                            'name': 'singular'
                        },
                        {
                            'name': 'plural'
                        },
                        {
                            'name': 'reverse'
                        },
                        {
                            'name': 'relations'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationType'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductRelationSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubTokenConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubTokenEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'tokenId'
                        },
                        {
                            'name': 'scope'
                        },
                        {
                            'name': 'userId'
                        },
                        {
                            'name': 'timeCreated'
                        },
                        {
                            'name': 'user'
                        },
                        {
                            'name': 'id'
                        },
                        {
                            'name': 'tokenMasked'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubToken'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'GitHubTokenFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'GitHubTokenSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgMembershipConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgMembershipEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'entryId'
                        },
                        {
                            'name': 'orgId'
                        },
                        {
                            'name': 'memberId'
                        },
                        {
                            'name': 'org'
                        },
                        {
                            'name': 'member'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgMembership'
                },
                {
                    'fields': [
                        {
                            'name': 'orgId'
                        },
                        {
                            'name': 'gitHubId'
                        },
                        {
                            'name': 'login'
                        },
                        {
                            'name': 'avatarUrl'
                        },
                        {
                            'name': 'url'
                        },
                        {
                            'name': 'memberships'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrg'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'GitHubOrgMembershipSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductTypeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductTypeEdge'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'ProductTypeFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductTypeSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationTypeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationTypeEdge'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductRelationTypeSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'FieldConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'FieldEdge'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'FieldSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgEdge'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'GitHubOrgSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubUserConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubUserEdge'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'GitHubUserFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'GitHubUserSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'LogConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'LogEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'level'
                        },
                        {
                            'name': 'message'
                        },
                        {
                            'name': 'time'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Log'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'LogSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'authenticateWithGitHub'
                        },
                        {
                            'name': 'createLog'
                        },
                        {
                            'name': 'createProduct'
                        },
                        {
                            'name': 'deleteProduct'
                        },
                        {
                            'name': 'updateProduct'
                        },
                        {
                            'name': 'convertProductType'
                        },
                        {
                            'name': 'createProductFilePath'
                        },
                        {
                            'name': 'deleteProductFilePath'
                        },
                        {
                            'name': 'updateProductFilePath'
                        },
                        {
                            'name': 'createProductRelation'
                        },
                        {
                            'name': 'deleteProductRelation'
                        },
                        {
                            'name': 'createProductRelationTypes'
                        },
                        {
                            'name': 'deleteProductRelationTypes'
                        },
                        {
                            'name': 'updateProductRelationType'
                        },
                        {
                            'name': 'createProductType'
                        },
                        {
                            'name': 'deleteProductType'
                        },
                        {
                            'name': 'updateProductType'
                        },
                        {
                            'name': 'createField'
                        },
                        {
                            'name': 'deleteField'
                        },
                        {
                            'name': 'updateField'
                        },
                        {
                            'name': 'addGitHubOrg'
                        },
                        {
                            'name': 'deleteGitHubOrg'
                        },
                        {
                            'name': 'addGitHubAdminAppToken'
                        },
                        {
                            'name': 'deleteGitHubAdminAppToken'
                        },
                        {
                            'name': 'updateGitHubOrgMemberLists'
                        },
                        {
                            'name': 'deleteLog'
                        },
                        {
                            'name': 'saveWebConfig'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'MutationAdmin'
                },
                {
                    'fields': [
                        {
                            'name': 'authPayload'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthenticateWithGitHub'
                },
                {
                    'fields': [
                        {
                            'name': 'token'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthPayload'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'log'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateLog'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateLogInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'product'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProduct'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductInput'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'RelationInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributesInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeUnicodeTextInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeBooleanInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeIntegerInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeFloatInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeDateInputFields'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Date'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeDateTimeInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeTimeInputFields'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Time'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProduct'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'product'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProduct'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'product'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ConvertProductType'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productFilePath'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductFilePath'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductFilePathInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductFilePath'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productFilePath'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProductFilePath'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductFilePathInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productRelation'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductRelation'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductRelationInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductRelation'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productRelationType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductRelationTypes'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductRelationTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductRelationTypes'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productRelationType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProductRelationType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductRelationTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductType'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProductType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'field'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateField'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateFieldInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteField'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'field'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateField'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateFieldInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'gitHubOrg'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AddGitHubOrg'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteGitHubOrg'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AddGitHubAdminAppToken'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteGitHubAdminAppToken'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateGitHubOrgMemberLists'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteLog'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'webConfig'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'SaveWebconfig'
                },
                {
                    'fields': [
                        {
                            'name': 'types'
                        },
                        {
                            'name': 'queryType'
                        },
                        {
                            'name': 'mutationType'
                        },
                        {
                            'name': 'subscriptionType'
                        },
                        {
                            'name': 'directives'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Schema'
                },
                {
                    'fields': [
                        {
                            'name': 'kind'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'fields'
                        },
                        {
                            'name': 'interfaces'
                        },
                        {
                            'name': 'possibleTypes'
                        },
                        {
                            'name': 'enumValues'
                        },
                        {
                            'name': 'inputFields'
                        },
                        {
                            'name': 'ofType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Type'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__TypeKind'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'args'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Field'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'defaultValue'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__InputValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__EnumValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'locations'
                        },
                        {
                            'name': 'args'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Directive'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__DirectiveLocation'
                }
            ]
        }
    }
}

snapshots['test_schema[private] 1'] = {
    'data': {
        '__schema': {
            'mutationType': {
                'fields': [
                    {
                        'name': 'authenticateWithGitHub'
                    },
                    {
                        'name': 'createLog'
                    },
                    {
                        'name': 'createProduct'
                    },
                    {
                        'name': 'deleteProduct'
                    },
                    {
                        'name': 'updateProduct'
                    },
                    {
                        'name': 'convertProductType'
                    },
                    {
                        'name': 'createProductFilePath'
                    },
                    {
                        'name': 'deleteProductFilePath'
                    },
                    {
                        'name': 'updateProductFilePath'
                    },
                    {
                        'name': 'createProductRelation'
                    },
                    {
                        'name': 'deleteProductRelation'
                    },
                    {
                        'name': 'createProductRelationTypes'
                    },
                    {
                        'name': 'deleteProductRelationTypes'
                    },
                    {
                        'name': 'updateProductRelationType'
                    },
                    {
                        'name': 'createProductType'
                    },
                    {
                        'name': 'deleteProductType'
                    },
                    {
                        'name': 'updateProductType'
                    },
                    {
                        'name': 'createField'
                    },
                    {
                        'name': 'deleteField'
                    },
                    {
                        'name': 'updateField'
                    }
                ]
            },
            'queryType': {
                'fields': [
                    {
                        'name': 'webConfig'
                    },
                    {
                        'name': 'isSignedIn'
                    },
                    {
                        'name': 'gitHubOAuthAppInfo'
                    },
                    {
                        'name': 'version'
                    },
                    {
                        'name': 'alembicVersion'
                    },
                    {
                        'name': 'isAdmin'
                    },
                    {
                        'name': 'gitHubViewer'
                    },
                    {
                        'name': 'allProducts'
                    },
                    {
                        'name': 'allProductTypes'
                    },
                    {
                        'name': 'allProductRelations'
                    },
                    {
                        'name': 'allProductRelationTypes'
                    },
                    {
                        'name': 'allProductFilePaths'
                    },
                    {
                        'name': 'allFields'
                    },
                    {
                        'name': 'product'
                    },
                    {
                        'name': 'productType'
                    },
                    {
                        'name': 'productRelation'
                    },
                    {
                        'name': 'productRelationType'
                    },
                    {
                        'name': 'field'
                    },
                    {
                        'name': 'node'
                    }
                ]
            },
            'subscriptionType': None,
            'types': [
                {
                    'fields': [
                        {
                            'name': 'webConfig'
                        },
                        {
                            'name': 'isSignedIn'
                        },
                        {
                            'name': 'gitHubOAuthAppInfo'
                        },
                        {
                            'name': 'version'
                        },
                        {
                            'name': 'alembicVersion'
                        },
                        {
                            'name': 'isAdmin'
                        },
                        {
                            'name': 'gitHubViewer'
                        },
                        {
                            'name': 'allProducts'
                        },
                        {
                            'name': 'allProductTypes'
                        },
                        {
                            'name': 'allProductRelations'
                        },
                        {
                            'name': 'allProductRelationTypes'
                        },
                        {
                            'name': 'allProductFilePaths'
                        },
                        {
                            'name': 'allFields'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'productType'
                        },
                        {
                            'name': 'productRelation'
                        },
                        {
                            'name': 'productRelationType'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'node'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'QueryPrivate'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'json'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'WebConfig'
                },
                {
                    'fields': [
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'INTERFACE',
                    'name': 'Node'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'ID'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'String'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Boolean'
                },
                {
                    'fields': [
                        {
                            'name': 'clientId'
                        },
                        {
                            'name': 'authorizeUrl'
                        },
                        {
                            'name': 'redirectUri'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOAuthAppInfo'
                },
                {
                    'fields': [
                        {
                            'name': 'userId'
                        },
                        {
                            'name': 'gitHubId'
                        },
                        {
                            'name': 'login'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'avatarUrl'
                        },
                        {
                            'name': 'url'
                        },
                        {
                            'name': 'postedProducts'
                        },
                        {
                            'name': 'updatedProducts'
                        },
                        {
                            'name': 'tokens'
                        },
                        {
                            'name': 'memberships'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubUser'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'hasNextPage'
                        },
                        {
                            'name': 'hasPreviousPage'
                        },
                        {
                            'name': 'startCursor'
                        },
                        {
                            'name': 'endCursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'PageInfo'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'timePosted'
                        },
                        {
                            'name': 'postingGitHubUserId'
                        },
                        {
                            'name': 'timeUpdated'
                        },
                        {
                            'name': 'updatingGitHubUserId'
                        },
                        {
                            'name': 'note'
                        },
                        {
                            'name': 'type_'
                        },
                        {
                            'name': 'postingGitHubUser'
                        },
                        {
                            'name': 'updatingGitHubUser'
                        },
                        {
                            'name': 'paths'
                        },
                        {
                            'name': 'relations'
                        },
                        {
                            'name': 'attributesUnicodeText'
                        },
                        {
                            'name': 'attributesBoolean'
                        },
                        {
                            'name': 'attributesInteger'
                        },
                        {
                            'name': 'attributesFloat'
                        },
                        {
                            'name': 'attributesDate'
                        },
                        {
                            'name': 'attributesDateTime'
                        },
                        {
                            'name': 'attributesTime'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Product'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Int'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'DateTime'
                },
                {
                    'fields': [
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'order'
                        },
                        {
                            'name': 'indefArticle'
                        },
                        {
                            'name': 'singular'
                        },
                        {
                            'name': 'plural'
                        },
                        {
                            'name': 'icon'
                        },
                        {
                            'name': 'products'
                        },
                        {
                            'name': 'fields'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'ProductFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'TypeFieldAssociationConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'TypeFieldAssociationEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'order'
                        },
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'type_'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'attributesUnicodeText'
                        },
                        {
                            'name': 'attributesBoolean'
                        },
                        {
                            'name': 'attributesInteger'
                        },
                        {
                            'name': 'attributesFloat'
                        },
                        {
                            'name': 'attributesDate'
                        },
                        {
                            'name': 'attributesDateTime'
                        },
                        {
                            'name': 'attributesTime'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'TypeFieldAssociation'
                },
                {
                    'fields': [
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'attributesUnicodeText'
                        },
                        {
                            'name': 'attributesBoolean'
                        },
                        {
                            'name': 'attributesInteger'
                        },
                        {
                            'name': 'attributesFloat'
                        },
                        {
                            'name': 'attributesDate'
                        },
                        {
                            'name': 'attributesDateTime'
                        },
                        {
                            'name': 'attributesTime'
                        },
                        {
                            'name': 'entryTypes'
                        },
                        {
                            'name': 'id'
                        },
                        {
                            'name': 'type_'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Field'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeUnicodeTextConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeUnicodeTextEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeUnicodeText'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeUnicodeTextSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeBooleanConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeBooleanEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeBoolean'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeBooleanSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeIntegerConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeIntegerEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeInteger'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeIntegerSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeFloatConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeFloatEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeFloat'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Float'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeFloatSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDate'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeDateSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateTimeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateTimeEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeDateTime'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeDateTimeSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeTimeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeTimeEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'iid'
                        },
                        {
                            'name': 'value'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'typeFieldAssociationIid'
                        },
                        {
                            'name': 'fieldId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'typeFieldAssociation'
                        },
                        {
                            'name': 'field'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AttributeTime'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'AttributeTimeSortEnum'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'TypeFieldAssociationSortEnum'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'FieldType'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductFilePathConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductFilePathEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'pathId'
                        },
                        {
                            'name': 'path'
                        },
                        {
                            'name': 'note'
                        },
                        {
                            'name': 'productId'
                        },
                        {
                            'name': 'product'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductFilePath'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductFilePathSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'relationId'
                        },
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'selfProductId'
                        },
                        {
                            'name': 'otherProductId'
                        },
                        {
                            'name': 'reverseRelationId'
                        },
                        {
                            'name': 'type_'
                        },
                        {
                            'name': 'self_'
                        },
                        {
                            'name': 'other'
                        },
                        {
                            'name': 'reverse'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelation'
                },
                {
                    'fields': [
                        {
                            'name': 'typeId'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'reverseTypeId'
                        },
                        {
                            'name': 'indefArticle'
                        },
                        {
                            'name': 'singular'
                        },
                        {
                            'name': 'plural'
                        },
                        {
                            'name': 'reverse'
                        },
                        {
                            'name': 'relations'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationType'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductRelationSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubTokenConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubTokenEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'tokenId'
                        },
                        {
                            'name': 'scope'
                        },
                        {
                            'name': 'userId'
                        },
                        {
                            'name': 'timeCreated'
                        },
                        {
                            'name': 'user'
                        },
                        {
                            'name': 'id'
                        },
                        {
                            'name': 'tokenMasked'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubToken'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'GitHubTokenFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'GitHubTokenSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgMembershipConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgMembershipEdge'
                },
                {
                    'fields': [
                        {
                            'name': 'entryId'
                        },
                        {
                            'name': 'orgId'
                        },
                        {
                            'name': 'memberId'
                        },
                        {
                            'name': 'org'
                        },
                        {
                            'name': 'member'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrgMembership'
                },
                {
                    'fields': [
                        {
                            'name': 'orgId'
                        },
                        {
                            'name': 'gitHubId'
                        },
                        {
                            'name': 'login'
                        },
                        {
                            'name': 'avatarUrl'
                        },
                        {
                            'name': 'url'
                        },
                        {
                            'name': 'memberships'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOrg'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'GitHubOrgMembershipSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductTypeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductTypeEdge'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'ProductTypeFilter'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductTypeSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationTypeConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ProductRelationTypeEdge'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'ProductRelationTypeSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'pageInfo'
                        },
                        {
                            'name': 'edges'
                        },
                        {
                            'name': 'totalCount'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'FieldConnection'
                },
                {
                    'fields': [
                        {
                            'name': 'node'
                        },
                        {
                            'name': 'cursor'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'FieldEdge'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': 'FieldSortEnum'
                },
                {
                    'fields': [
                        {
                            'name': 'authenticateWithGitHub'
                        },
                        {
                            'name': 'createLog'
                        },
                        {
                            'name': 'createProduct'
                        },
                        {
                            'name': 'deleteProduct'
                        },
                        {
                            'name': 'updateProduct'
                        },
                        {
                            'name': 'convertProductType'
                        },
                        {
                            'name': 'createProductFilePath'
                        },
                        {
                            'name': 'deleteProductFilePath'
                        },
                        {
                            'name': 'updateProductFilePath'
                        },
                        {
                            'name': 'createProductRelation'
                        },
                        {
                            'name': 'deleteProductRelation'
                        },
                        {
                            'name': 'createProductRelationTypes'
                        },
                        {
                            'name': 'deleteProductRelationTypes'
                        },
                        {
                            'name': 'updateProductRelationType'
                        },
                        {
                            'name': 'createProductType'
                        },
                        {
                            'name': 'deleteProductType'
                        },
                        {
                            'name': 'updateProductType'
                        },
                        {
                            'name': 'createField'
                        },
                        {
                            'name': 'deleteField'
                        },
                        {
                            'name': 'updateField'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'MutationPrivate'
                },
                {
                    'fields': [
                        {
                            'name': 'authPayload'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthenticateWithGitHub'
                },
                {
                    'fields': [
                        {
                            'name': 'token'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthPayload'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'log'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateLog'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'level'
                        },
                        {
                            'name': 'message'
                        },
                        {
                            'name': 'time'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Log'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateLogInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'product'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProduct'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductInput'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'RelationInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributesInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeUnicodeTextInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeBooleanInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeIntegerInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeFloatInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeDateInputFields'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Date'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeDateTimeInputFields'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'AttributeTimeInputFields'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Time'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProduct'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'product'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProduct'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'product'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'ConvertProductType'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productFilePath'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductFilePath'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductFilePathInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductFilePath'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productFilePath'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProductFilePath'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductFilePathInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productRelation'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductRelation'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductRelationInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductRelation'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productRelationType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductRelationTypes'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductRelationTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductRelationTypes'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productRelationType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProductRelationType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductRelationTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateProductType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateProductTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteProductType'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'productType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateProductType'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateProductTypeInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'field'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateField'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateFieldInput'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'DeleteField'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'field'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'UpdateField'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'UpdateFieldInput'
                },
                {
                    'fields': [
                        {
                            'name': 'types'
                        },
                        {
                            'name': 'queryType'
                        },
                        {
                            'name': 'mutationType'
                        },
                        {
                            'name': 'subscriptionType'
                        },
                        {
                            'name': 'directives'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Schema'
                },
                {
                    'fields': [
                        {
                            'name': 'kind'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'fields'
                        },
                        {
                            'name': 'interfaces'
                        },
                        {
                            'name': 'possibleTypes'
                        },
                        {
                            'name': 'enumValues'
                        },
                        {
                            'name': 'inputFields'
                        },
                        {
                            'name': 'ofType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Type'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__TypeKind'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'args'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Field'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'defaultValue'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__InputValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__EnumValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'locations'
                        },
                        {
                            'name': 'args'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Directive'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__DirectiveLocation'
                }
            ]
        }
    }
}

snapshots['test_schema[public-no-token] 1'] = {
    'data': {
        '__schema': {
            'mutationType': {
                'fields': [
                    {
                        'name': 'authenticateWithGitHub'
                    },
                    {
                        'name': 'createLog'
                    }
                ]
            },
            'queryType': {
                'fields': [
                    {
                        'name': 'webConfig'
                    },
                    {
                        'name': 'isSignedIn'
                    },
                    {
                        'name': 'gitHubOAuthAppInfo'
                    }
                ]
            },
            'subscriptionType': None,
            'types': [
                {
                    'fields': [
                        {
                            'name': 'webConfig'
                        },
                        {
                            'name': 'isSignedIn'
                        },
                        {
                            'name': 'gitHubOAuthAppInfo'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'QueryPublic'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'json'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'WebConfig'
                },
                {
                    'fields': [
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'INTERFACE',
                    'name': 'Node'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'ID'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'String'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Boolean'
                },
                {
                    'fields': [
                        {
                            'name': 'clientId'
                        },
                        {
                            'name': 'authorizeUrl'
                        },
                        {
                            'name': 'redirectUri'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOAuthAppInfo'
                },
                {
                    'fields': [
                        {
                            'name': 'authenticateWithGitHub'
                        },
                        {
                            'name': 'createLog'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'MutationPublic'
                },
                {
                    'fields': [
                        {
                            'name': 'authPayload'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthenticateWithGitHub'
                },
                {
                    'fields': [
                        {
                            'name': 'token'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthPayload'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'log'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateLog'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'level'
                        },
                        {
                            'name': 'message'
                        },
                        {
                            'name': 'time'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Log'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'DateTime'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateLogInput'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Int'
                },
                {
                    'fields': [
                        {
                            'name': 'types'
                        },
                        {
                            'name': 'queryType'
                        },
                        {
                            'name': 'mutationType'
                        },
                        {
                            'name': 'subscriptionType'
                        },
                        {
                            'name': 'directives'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Schema'
                },
                {
                    'fields': [
                        {
                            'name': 'kind'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'fields'
                        },
                        {
                            'name': 'interfaces'
                        },
                        {
                            'name': 'possibleTypes'
                        },
                        {
                            'name': 'enumValues'
                        },
                        {
                            'name': 'inputFields'
                        },
                        {
                            'name': 'ofType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Type'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__TypeKind'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'args'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Field'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'defaultValue'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__InputValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__EnumValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'locations'
                        },
                        {
                            'name': 'args'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Directive'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__DirectiveLocation'
                }
            ]
        }
    }
}

snapshots['test_schema[public-wrong-token] 1'] = {
    'data': {
        '__schema': {
            'mutationType': {
                'fields': [
                    {
                        'name': 'authenticateWithGitHub'
                    },
                    {
                        'name': 'createLog'
                    }
                ]
            },
            'queryType': {
                'fields': [
                    {
                        'name': 'webConfig'
                    },
                    {
                        'name': 'isSignedIn'
                    },
                    {
                        'name': 'gitHubOAuthAppInfo'
                    }
                ]
            },
            'subscriptionType': None,
            'types': [
                {
                    'fields': [
                        {
                            'name': 'webConfig'
                        },
                        {
                            'name': 'isSignedIn'
                        },
                        {
                            'name': 'gitHubOAuthAppInfo'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'QueryPublic'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'json'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'WebConfig'
                },
                {
                    'fields': [
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'INTERFACE',
                    'name': 'Node'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'ID'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'String'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Boolean'
                },
                {
                    'fields': [
                        {
                            'name': 'clientId'
                        },
                        {
                            'name': 'authorizeUrl'
                        },
                        {
                            'name': 'redirectUri'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'GitHubOAuthAppInfo'
                },
                {
                    'fields': [
                        {
                            'name': 'authenticateWithGitHub'
                        },
                        {
                            'name': 'createLog'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'MutationPublic'
                },
                {
                    'fields': [
                        {
                            'name': 'authPayload'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthenticateWithGitHub'
                },
                {
                    'fields': [
                        {
                            'name': 'token'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'AuthPayload'
                },
                {
                    'fields': [
                        {
                            'name': 'ok'
                        },
                        {
                            'name': 'log'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'CreateLog'
                },
                {
                    'fields': [
                        {
                            'name': 'id_'
                        },
                        {
                            'name': 'level'
                        },
                        {
                            'name': 'message'
                        },
                        {
                            'name': 'time'
                        },
                        {
                            'name': 'id'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': 'Log'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'DateTime'
                },
                {
                    'fields': None,
                    'kind': 'INPUT_OBJECT',
                    'name': 'CreateLogInput'
                },
                {
                    'fields': None,
                    'kind': 'SCALAR',
                    'name': 'Int'
                },
                {
                    'fields': [
                        {
                            'name': 'types'
                        },
                        {
                            'name': 'queryType'
                        },
                        {
                            'name': 'mutationType'
                        },
                        {
                            'name': 'subscriptionType'
                        },
                        {
                            'name': 'directives'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Schema'
                },
                {
                    'fields': [
                        {
                            'name': 'kind'
                        },
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'fields'
                        },
                        {
                            'name': 'interfaces'
                        },
                        {
                            'name': 'possibleTypes'
                        },
                        {
                            'name': 'enumValues'
                        },
                        {
                            'name': 'inputFields'
                        },
                        {
                            'name': 'ofType'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Type'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__TypeKind'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'args'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Field'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'type'
                        },
                        {
                            'name': 'defaultValue'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__InputValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'isDeprecated'
                        },
                        {
                            'name': 'deprecationReason'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__EnumValue'
                },
                {
                    'fields': [
                        {
                            'name': 'name'
                        },
                        {
                            'name': 'description'
                        },
                        {
                            'name': 'locations'
                        },
                        {
                            'name': 'args'
                        }
                    ],
                    'kind': 'OBJECT',
                    'name': '__Directive'
                },
                {
                    'fields': None,
                    'kind': 'ENUM',
                    'name': '__DirectiveLocation'
                }
            ]
        }
    }
}
