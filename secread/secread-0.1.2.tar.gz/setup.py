# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['secread', 'secread.tests']

package_data = \
{'': ['*'], 'secread.tests': ['data/*']}

install_requires = \
['python-dotenv>=0.18.0,<0.19.0',
 'requests>=2.26.0,<3.0.0',
 'types-requests>=2.25.9,<3.0.0']

setup_kwargs = {
    'name': 'secread',
    'version': '0.1.2',
    'description': 'This Python module allows to retrive secrets from Thycotic Secret Server. It utilizes the REST API',
    'long_description': '## Thycotic Secret Server Reader\n\nThis Python module allows to retrive secrets from Thycotic Secret Server.\nIt utilizes the REST API\n\nsee:\n<https://docs.thycotic.com/ss/10.8.0/api-scripting/rest-api-reference-download>\n\n### License\n\nMIT\n\n### Installation\n\n```bash\npoetry install\n```\n\n### Configuration\n\nTo configure the module use following environment variables. It is also possible\nto provide the file \'.env\' with the settings\n\n```bash\ncp .env.example .env\nvi .env\n```\n\n```python\n#############################################################################\n# Settings for Thycotic Secret Server Reader\n\nSECRET_SERVER_SITE=\'https://pw.example.com/SecretServer\'\nSECRET_SERVER_AUTH_API=\'/oauth2/token\'\nSECRET_SERVER_USERNAME=\'apiuser\'\nSECRET_SERVER_PASSWORD=\'my_password_for_apiuser\'\n\n# Values for SECRET_SERVER_SSL_VERIFY\n# - True    server certificate will be verified (Default)\n# - False   server certificate will be ignored; warning\n# - Path    path to trusted cerificate bundle e.g. \'/etc/ssl/certs/ca-bundle.trust.crt\'\nSECRET_SERVER_SSL_VERIFY=\'/etc/ssl/certs/ca-bundle.trust.crt\'\n\n# Default field-items to extract from result.\nSECRET_SERVER_DEFAULT_SLUGS=\'["id", "url", "username", "password"]\'\n\n# SECRET_SERVER_IS_DUMMY (Default: False)\n# - False: Secert-Server-API is active\n# - True: The API will not be used. SECRET_SERVER_TEST_DUMMY_RESULT will be returned\n# SECRET_SERVER_IS_DUMMY=False\n\nSECRET_SERVER_TEST_DUMMY_RESULT=\'{"id": "12345", username": "testuser", "password": "testpassword", "url": "https://localhost/SecretServer"}\'\n\n# \'name\' of the secret that is used for testing on live server\n# TEST_SECRET_NAME=\'GitLab Token netsearch-ro\'\n```\n\n### Development\n\nThe installation instruction for `poetry` is here: <https://python-poetry.org/docs/#installation>\n\n- **Using the module with poetry:**\n\n    ```bash\n    git clone https://github.com/jifox/secret-server-reader.git\n    cd your_project_dir\n    poetry add .../secret-server-reader\n    ```\n\n- **Using the module with pip:**\n\n    ```bash\n    git clone .... secret-server-reader\n    cd .../secret-server-reader\n    poetry build\n\n    pip install dist/secread-0.1.0-py3-none-any.whl\n    ```\n\n### Examples\n\n```python\n"""Tests for module secread"""\nimport os\nimport pytest\nfrom secread import __version__, SecretServer\n\n\ndef test_version():\n    assert __version__ == "0.1.1"\n\n\n@pytest.fixture\ndef sec_server():\n    return SecretServer()\n\n\ndef test_default_slugs_is_a_list(sec_server: SecretServer):\n    slugs = sec_server.SECRET_SERVER_DEFAULT_SLUGS\n    assert isinstance(slugs, list)\n\n\ndef test_secretserver(sec_server: SecretServer):\n    token = sec_server.getAuthToken()\n    assert len(token) > 0, "Token could not be read"\n\n\ndef test_get_secret_response_by_name(sec_server: SecretServer):\n    secname = os.getenv("TEST_SECRET_NAME", "GitLab Token netsearch-ro")\n    res = sec_server.searchSecretResponse(secname)\n    fields = sec_server.getFieldItemWithSlug(res)\n    assert "username" in fields.keys(), "Missing username"\n    assert "password" in fields.keys(), "Missing password"\n\n\ndef test_get_secret_by_name(sec_server: SecretServer):\n    secname = os.getenv("TEST_SECRET_NAME", "GitLab Token netsearch-ro")\n    res = sec_server.searchSecret(secname)\n    assert "username" in res.keys(), "Missing username"\n    assert "password" in res.keys(), "Missing password"\n```\n',
    'author': 'Josef Fuchs',
    'author_email': 'j053ff0x@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jifox/secret-server-reader.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
