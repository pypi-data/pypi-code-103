
import pytest
import unittest.mock as mock

from acondbs.github import query

##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    y = mock.Mock()
    monkeypatch.setattr("acondbs.github.call.requests", y)
    yield y


##__________________________________________________________________||
def test_success(mock_requests):

    token = '4d5dc8b74eccdf65859d6ac64358a3a98300c351'
    # random string generated with
    # ''.join(random.choice('0123456789abcdef') for i in range(40))

    mock_requests.post().json.return_value = {
        'data': {
            'viewer': {
                "id": "MDQ6VXNlcjU4MzIzMQ==",
                "login": "octocat",
                "name": "The Octocat",
                "avatarUrl": "https://avatars3.githubusercontent.com/u/583231?u=a59fef2a493e2b67dd13754231daf220c82ba84d&v=4",
                "url": "https://github.com/octocat"
            }
        }
    }

    expected = {
        "id": "04:User583231",
        "login": "octocat",
        "name": "The Octocat",
        "avatarUrl": "https://avatars3.githubusercontent.com/u/583231?u=a59fef2a493e2b67dd13754231daf220c82ba84d&v=4",
        "url": "https://github.com/octocat"
    }

    actual = query.viewer(token)

    assert expected == actual

##__________________________________________________________________||
def test_bad_credentials(mock_requests):

    token = '4d5dc8b74eccdf65859d6ac64358a3a98300c351'
    # random string generated with
    # ''.join(random.choice('0123456789abcdef') for i in range(40))

    mock_requests.post().json.return_value = {
        'message': 'Bad credentials',
        'documentation_url': 'https://docs.github.com/graphql'
    }

    with pytest.raises(Exception) as e:
        query.viewer(token)

    expected = {
        'message': 'Bad credentials',
        'documentation_url': 'https://docs.github.com/graphql'
    }

    assert expected == e.value.args[0]

##__________________________________________________________________||
