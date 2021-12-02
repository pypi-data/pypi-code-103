from flask import json

import pytest
import unittest.mock as mock

from acondbs import create_app
from acondbs.db.ops import define_tables


##__________________________________________________________________||
QUERY = '''
{
  __schema {
    queryType {
      fields {
        name
      }
    }
    mutationType {
      fields {
        name
      }
    }
    subscriptionType {
      fields {
        name
      }
    }
  }
}
'''


##__________________________________________________________________||
@pytest.fixture
def app_empty():
    database_uri = "sqlite:///:memory:"
    y = create_app(SQLALCHEMY_DATABASE_URI=database_uri)
    with y.app_context():
        define_tables()
    yield y


##__________________________________________________________________||
@pytest.fixture()
def mock_auth(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.blueprint.auth", y)
    yield y


##__________________________________________________________________||
@pytest.mark.parametrize('is_signed_in', [True, False])
@pytest.mark.parametrize('is_admin', [True, False])
def test_schema_selection(app_empty, is_signed_in, is_admin, mock_auth, snapshot):
    app = app_empty

    mock_auth.is_signed_in.return_value = is_signed_in
    mock_auth.is_admin.return_value = is_admin

    client = app.test_client()

    response = client.get('/graphql', query_string=dict(query=QUERY))

    assert 200 == response.status_code

    result = json.loads(response.data)['data']

    un_jsonified = json.loads(response.data)
    snapshot.assert_match(un_jsonified)
    # print(json.dumps(un_jsonified, indent=2))

##__________________________________________________________________||
