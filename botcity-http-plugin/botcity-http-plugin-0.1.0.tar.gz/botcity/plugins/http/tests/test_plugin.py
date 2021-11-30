import datetime
import hashlib
import os

from botcity.plugins.http import BotHttpPlugin


def test_get():
    assert BotHttpPlugin("https://ptsv2.com/t/ocrc3-1624379671/post").get().text == "The test of BotHttpPlugin work!"


def test_post():
    params = {
        'id': 'ocrc3-1624379671',
        'text': 'POST date: ' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    }
    response = BotHttpPlugin("https://ptsv2.com/t/ocrc3-1624379671/post", params).post().text
    assert response == "The test of BotHttpPlugin work!"


def test_get_bytes():
    # Expected values
    url = "https://files.pythonhosted.org/packages/b7/86/c9ea9877ed8f9abc4e7f55fc910c40fbbf88778b65e006a917970ac5524f/botcity-framework-web-0.2.0.tar.gz"
    expected_sha = "3637f54e8d9e24f4d346a5e511b545e059e938144beedcfa9323d00aaf18154b"

    content = BotHttpPlugin(url).get_bytes()
    assert hashlib.sha256(content).hexdigest() == expected_sha


def test_get_file():
    # Expected values
    url = "https://files.pythonhosted.org/packages/b7/86/c9ea9877ed8f9abc4e7f55fc910c40fbbf88778b65e006a917970ac5524f/botcity-framework-web-0.2.0.tar.gz"
    expected_sha = "3637f54e8d9e24f4d346a5e511b545e059e938144beedcfa9323d00aaf18154b"

    # Downloads the file with a get request
    name = BotHttpPlugin(url).get_as_file("get_file_test")

    # Verifies if the file was properly downloaded
    with open(os.path.join(os.getcwd(), name), 'rb') as file:
        data = file.read()
    assert hashlib.sha256(data).hexdigest() == expected_sha
