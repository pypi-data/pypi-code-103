"""Parse configuration from environment variables."""
import os

from unimatrix.lib import environ


#: Indicates that the application is running in debug mode.
DEBUG: bool = os.getenv('DEBUG') == '1'

#: The current environment in which the application is runtime. This variable
#: defaults to ``production`` to prevent unwanted side-effects when it is not
#: set.
DEPLOYMENT_ENV: str = os.getenv('DEPLOYMENT_ENV') or 'production'

#: Indicates if SSL should be verified.
ENABLE_SSL = os.getenv('PYTHONHTTPSVERIFY') != '0'

#: Specifies which hosts may make requests to application, based on the
#: content of the ``Host`` header.
HTTP_ALLOWED_HOSTS: tuple = environ.parselist(
    os.environ, 'HTTP_ALLOWED_HOSTS', sep=';')

#: Indicate if Cross-Origin Resource Sharing (CORS) is enabled for the
#: application.
HTTP_CORS_ENABLED: bool = environ.parsebool(os.environ, 'HTTP_CORS_ENABLED')

#: The allowed origins as determined based on the ``Origin`` header setting
#: for Cross-Origin Resource Sharing (CORS).
HTTP_CORS_ALLOW_ORIGINS: tuple = environ.parselist(
    os.environ, 'HTTP_CORS_ALLOW_ORIGINS', sep=';')

#: The allowed request methods for cross-origin requests.
HTTP_CORS_ALLOW_METHODS: tuple = environ.parselist(
    os.environ, 'HTTP_CORS_ALLOW_METHODS', sep=':')

#: The allowed request headers setting for Cross-Origin Resource Sharing (CORS).
HTTP_CORS_ALLOW_HEADERS: tuple = environ.parselist(
    os.environ, 'HTTP_CORS_ALLOW_HEADERS', sep=':')

#: Indicates if cross-origin responses may include cookies.
HTTP_CORS_ALLOW_CREDENTIALS: bool = environ.parsebool(
    os.environ, 'HTTP_CORS_ALLOW_CREDENTIALS')

#: The list of response headers that may be included in a cross-origin
#: response, separated by a colon.
HTTP_CORS_EXPOSE_HEADERS: tuple = environ.parselist(
    os.environ, 'HTTP_CORS_EXPOSE_HEADERS', sep=':')

#: Specifies the maximum time in seconds that a browser may cache a CORS
#: response. Defaults to ``600``.
HTTP_CORS_TTL: int = environ.parseint(
    os.environ, 'HTTP_CORS_TTL', default=600)

#: Path to the URL configuration file.
HTTP_URLCONF = os.getenv('HTTP_URLCONF') or 'etc/urlconf.yml'


#: The default log level.
LOG_LEVEL = os.getenv('LOG_LEVEL') or 'WARNING'

#: The filepath to a PEM-encoded private key (either RSA or elliptic curve with
#: a supported curve) that is used by the application to sign access tokens when
#: communicating with other services. Implementations must ensure that when
#: issueing access tokens using this key, that the OpenID discovery document is
#: also served from the well-known URI (``/.well-known/openid-configuration``),
#: relative to the ``iss`` claim that it specifies on the tokens.
OAUTH2_ACTOR_KEY: str = os.getenv('OAUTH2_ACTOR_KEY')

#: Additional audiences that the server accepts.
OAUTH2_AUDIENCES: tuple = environ.parselist(
    os.environ, 'OAUTH2_AUDIENCES', sep=';'
)

#: The list of Security Token Services (STSs) that the application trusts. The
#: services are expected to provide a ``/.well-known/openid-configuration``
#: URL, from which the JWKS holding its keys can be discovered. Multiple STSs
#: are separated by a semicolon.
OAUTH2_TRUSTED_STS: tuple = environ.parselist(
    os.environ, 'OAUTH2_TRUSTED_STS', sep=";"
)

#: The URL at which the application may exchange security tokens.
OAUTH2_TOKEN_EXCHANGE_URL = os.getenv('OAUTH2_TOKEN_EXCHANGE_URL')

#: The default secret key. This is an opaque string.
SECRET_KEY: str = os.getenv('SECRET_KEY')
