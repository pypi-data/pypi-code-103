import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_UPDATE_PRODUCT

QEURY = """
{
  allProducts {
    edges {
      node {
        name
      }
    }
  }
  allProductRelations {
    edges {
      node {
        type_ {
          name
        }
        self_ {
          name
        }
        other {
          name
        }
      }
    }
  }
  allProductFilePaths {
    edges {
      node {
        path
      }
    }
  }
}
"""

HEADERS = {
    "Authorization": "Bearer 39d86487d76a84087f1da599c872dac4473e5f07",  # user1
}


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 1,
                "input": {
                    "note": "- updated note 123",
                    "attributes": {
                        "unicodeText": [
                            {"fieldId": 1, "value": "new-contact"},
                        ],
                    },
                },
            },
        },
        {"query": QEURY},
        id="update",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 1,
                "input": {
                    "name": "new-name",
                },
            },
        },
        {"query": QEURY},
        id="update-name",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 1,
                "input": {
                    "paths": [
                        "site1:/path/to/map1",
                        "site2:/updated/way/map1",
                        "site4:/additional/map1",
                    ],
                },
            },
        },
        {"query": QEURY},
        id="update-paths",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 1,
                "input": {
                    "paths": [],
                },
            },
        },
        {"query": QEURY},
        id="delete-paths",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 5,
                "input": {
                    "relations": [
                        {"typeId": 1, "productId": 4},
                        {"typeId": 1, "productId": 2},
                    ],
                },
            },
        },
        {"query": QEURY},
        id="update-relations",
    ),
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 5,
                "input": {
                    "relations": [],
                },
            },
        },
        {"query": QEURY},
        id="delete-relations",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema_success(
    app, snapshot, data_mutation, data_query, mock_request_backup_db
):
    success = True
    await assert_mutation(
        app,
        snapshot,
        data_mutation,
        HEADERS,
        data_query,
        HEADERS,
        mock_request_backup_db,
        success,
    )


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": MUTATION_UPDATE_PRODUCT,
            "variables": {
                "productId": 1,
                "input": {
                    "name": "map2",
                },
            },
        },
        {"query": QEURY},
        id="error-constraint",
    ),
]


@pytest.mark.parametrize("data_mutation, data_query", params)
@pytest.mark.asyncio
async def test_schema_error(
    app, snapshot, data_mutation, data_query, mock_request_backup_db
):
    success = False
    await assert_mutation(
        app,
        snapshot,
        data_mutation,
        HEADERS,
        data_query,
        HEADERS,
        mock_request_backup_db,
        success,
    )


##__________________________________________________________________||
