import pytest
import textwrap


from ....funcs import assert_mutation

HEADERS = {"Authorization": "Bearer token123"}  # octocat


##__________________________________________________________________||
params = [
    pytest.param(
        {
            "query": textwrap.dedent(
                """
                  mutation m {
                    deleteProductFilePath(pathId: 1) { ok }
                  }
                """,
            ),
        },
        {
            "query": textwrap.dedent(
                """
                  {
                    product(productId: 1001 ) {
                      name timePosted note
                      paths { edges { node { path note product { productId } } } }
                    }
                  }
                """,
            )
        },
        id="deleteProductFilePath",
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
            "query": textwrap.dedent(
                """
                  mutation m {
                    deleteProductFilePath(pathId: 15) { ok }
                  }
                """,
            )
        },
        {
            "query": textwrap.dedent(
                """
                  {
                    allProductFilePaths {
                      edges {
                        node {
                          productId
                        }
                      }
                    }
                  }
                """,
            )
        },
        id="deleteProductFilePath-error",
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
