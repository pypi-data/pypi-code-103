"""Tests for module secread"""
import os
import pytest
from secread import __version__, SecretServer


def test_version():
    assert __version__ == "0.1.4"


@pytest.fixture
def sec_server():
    return SecretServer()


def test_default_slugs_is_a_list(sec_server: SecretServer):
    slugs = sec_server.SECRET_SERVER_DEFAULT_SLUGS
    assert isinstance(slugs, list)


def test_secretserver(sec_server: SecretServer):
    token = sec_server.getAuthToken()
    assert len(token) > 0, "Token could not be read"


def test_get_secret_response_by_name(sec_server: SecretServer):
    secname = os.getenv("TEST_SECRET_NAME", "GitLab Token netsearch-ro")
    res = sec_server.searchSecretResponse(secname)
    fields = sec_server.getFieldItemWithSlug(res)
    assert "username" in fields.keys(), "Missing username"
    assert "password" in fields.keys(), "Missing password"


def test_get_secret_by_name(sec_server: SecretServer):
    secname = os.getenv("TEST_SECRET_NAME", "GitLab Token netsearch-ro")
    res = sec_server.searchSecret(secname)
    assert "username" in res.keys(), "Missing username"
    assert "password" in res.keys(), "Missing password"
