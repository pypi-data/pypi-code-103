# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['secread', 'secread.tests']

package_data = \
{'': ['*'], 'secread.tests': ['data/*']}

install_requires = \
['python-dotenv>=0.1.0,<1.0.0',
 'requests>=2.0.0,<3.0.0',
 'types-requests>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'secread',
    'version': '0.1.4',
    'description': 'This Python module allows to retrive secrets from Thycotic Secret Server. It utilizes the REST API',
    'long_description': '## Thycotic Secret Server Reader\n\nThis Python module allows to retrive secrets from Thycotic Secret Server.\nIt utilizes the REST API\n\nsee:\n<https://docs.thycotic.com/ss/10.8.0/api-scripting/rest-api-reference-download>\n\n### License\n\nMIT\n\n### Installation\n\nInstallation with `PyPi`:\n\n```bash\npip install secread\n```\n\nInstallation with `poetry`:\n\n```bash\npoetry add secread\n```\n\n### Configuration\n\nTo configure the module use following environment variables. It is also possible\nto provide the file \'.env\' with the settings\n\n```bash\n# copy the template as environment file\ncp .env.example .env\n\n# Edit configuration file\nvi .env\n```\n\n```python\n#############################################################################\n# Settings for Thycotic Secret Server Reader\n\nSECRET_SERVER_SITE=\'https://pw.example.com/SecretServer\'\nSECRET_SERVER_AUTH_API=\'/oauth2/token\'\nSECRET_SERVER_USERNAME=\'apiuser\'\nSECRET_SERVER_PASSWORD=\'my_password_for_apiuser\'\n\n# Values for SECRET_SERVER_SSL_VERIFY\n# - True    server certificate will be verified (Default)\n# - False   server certificate will be ignored; warning\n# - Path    path to trusted cerificate bundle e.g. \'/etc/ssl/certs/ca-bundle.trust.crt\'\nSECRET_SERVER_SSL_VERIFY=\'/etc/ssl/certs/ca-bundle.trust.crt\'\n\n# Default field-items to extract from result.\nSECRET_SERVER_DEFAULT_SLUGS=\'["id", "url", "username", "password"]\'\n\n# SECRET_SERVER_IS_DUMMY (Default: False)\n# - False: Secert-Server-API is active\n# - True: The API will not be used. SECRET_SERVER_TEST_DUMMY_RESULT will be returned\n# SECRET_SERVER_IS_DUMMY=False\n\nSECRET_SERVER_TEST_DUMMY_RESULT=\'{"id": "12345", username": "testuser", "password": "testpassword", "url": "https://localhost/SecretServer"}\'\n\n# \'name\' of the secret that is used for testing on live server\n# TEST_SECRET_NAME=\'GitLab Token netsearch-ro\'\n```\n\n### Development\n\nThe installation instruction for `poetry` is here: <https://python-poetry.org/docs/#installation>\n\n```bash\ngit clone https://github.com/jifox/secret-server-reader.git\ncd secret-server-reader\n\n# Set python environment to use for development\n# poetry env use python3.8\n\n# Install the module\npoetry install\n\n# Execute tests (be sure to configure the system before)\npoetry run pytest -v\n```\n\n#### Update pypi\n\nBefore updating pypi, the version number must be incremented in following files:\n\n- pyproject.toml\n- secread/__init__.py\n- secread/tests/test_secread.py\n\n```bash\npoetry build\npoetry publish\n```\n\n### Examples\n\n```python\n"""Tests for module secread"""\nimport os\nimport pytest\nfrom secread import __version__, SecretServer\n\n\ndef test_version():\n    assert __version__ == "0.1.1"\n\n\n@pytest.fixture\ndef sec_server():\n    return SecretServer()\n\n\ndef test_default_slugs_is_a_list(sec_server: SecretServer):\n    slugs = sec_server.SECRET_SERVER_DEFAULT_SLUGS\n    assert isinstance(slugs, list)\n\n\ndef test_secretserver(sec_server: SecretServer):\n    token = sec_server.getAuthToken()\n    assert len(token) > 0, "Token could not be read"\n\n\ndef test_get_secret_response_by_name(sec_server: SecretServer):\n    secname = os.getenv("TEST_SECRET_NAME", "GitLab Token netsearch-ro")\n    res = sec_server.searchSecretResponse(secname)\n    fields = sec_server.getFieldItemWithSlug(res)\n    assert "username" in fields.keys(), "Missing username"\n    assert "password" in fields.keys(), "Missing password"\n\n\ndef test_get_secret_by_name(sec_server: SecretServer):\n    secname = os.getenv("TEST_SECRET_NAME", "GitLab Token netsearch-ro")\n    res = sec_server.searchSecret(secname)\n    assert "username" in res.keys(), "Missing username"\n    assert "password" in res.keys(), "Missing password"\n```\n',
    'author': 'Josef Fuchs',
    'author_email': 'j053ff0x@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jifox/secret-server-reader.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
