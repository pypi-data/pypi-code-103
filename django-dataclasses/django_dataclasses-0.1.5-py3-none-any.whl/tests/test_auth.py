def test_authenticated(admin_client):
    response = admin_client.get("/auth/")
    assert response.status_code == 200


def test_not_authenticated(client):
    response = client.get("/auth/")
    assert response.status_code == 401
    assert response.content == b""
