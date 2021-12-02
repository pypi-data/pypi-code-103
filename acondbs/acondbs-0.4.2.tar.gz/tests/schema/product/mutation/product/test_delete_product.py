import pytest

from ....funcs import assert_mutation

from ...gql import MUTATION_DELETE_PRODUCT

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


HEADERS = {"Authorization": "Bearer 39d86487d76a84087f1da599c872dac4473e5f07"}  # user1


##__________________________________________________________________||
params = [
    pytest.param(
        {"query": MUTATION_DELETE_PRODUCT, "variables": {"productId": 1}},
        {"query": QEURY},
        id="delete",
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
        {"query": MUTATION_DELETE_PRODUCT, "variables": {"productId": 512}},
        {"query": QEURY},
        id="error",
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
