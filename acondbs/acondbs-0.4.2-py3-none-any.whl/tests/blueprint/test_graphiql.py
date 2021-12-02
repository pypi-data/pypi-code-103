import pytest

from acondbs import create_app
from acondbs.db.ops import define_tables


##__________________________________________________________________||
params = [
    [True, 200, "<!DOCTYPE html>"],
    [False, 400, "errors"],
]


@pytest.mark.parametrize("graphiql, code, data", params)
def test_disable(graphiql, code, data):
    app = create_app(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        ACONDBS_GRAPHIQL=graphiql,
        ACONDBS_GRAPHIQL_TEMPLATE_NO=2,
    )
    with app.app_context():
        define_tables()

    client = app.test_client()

    response = client.get("/graphql", headers={"Accept": "text/html"})
    assert code == response.status_code
    assert data in response.data.decode("utf-8")


##__________________________________________________________________||
params = [
    [None, "//cdn.jsdelivr.net/npm/graphiql@0.11.11/graphiql.min.js"],
    [1, "https://unpkg.com/graphiql/graphiql.min.js"],
    [2, "graphql-playground"],
]


@pytest.mark.parametrize("number, data", params)
def test_template(number, data):
    app = create_app(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        ACONDBS_GRAPHIQL=True,
        ACONDBS_GRAPHIQL_TEMPLATE_NO=number,
    )
    with app.app_context():
        define_tables()

    client = app.test_client()

    response = client.get("/graphql", headers={"Accept": "text/html"})
    assert 200 == response.status_code
    assert data in response.data.decode("utf-8")


##__________________________________________________________________||
