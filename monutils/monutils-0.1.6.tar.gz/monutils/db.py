from enum import Enum
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

MAX_SEV_SEL_DELAY = 5
DEF_MONGODB_PORT = 27017


class Mode(Enum):
    NONE = None
    AUTO = 'AUTO'
    URI = 'URI'
    SCRAM_SHA_256 = 'SCRAM-SHA-256'
    SCRAM_SHA_1 = 'SCRAM-SHA-1'
    MONGODB_CR = 'MONGODB-CR'
    MONGODB_X509 = 'MONGODB-X509'
    GSSAPI = 'GSSAPI'
    Windows = 'Windows'
    PLAIN = 'PLAIN'
    MONGODB_AWS = 'MONGODB-AWS'
    AssumeRole = 'MONGODB-AWS'
    AWS_Lambda = 'MONGODB-AWS'
    ECS_Container = 'MONGODB-AWS'
    EC2_Instance = 'MONGODB-AWS'


def uri_connect(host: str = 'localhost', port: int = 27017, replicaset: str = None,
                user: str = None, password: str = None, cert_key_file: str = None,
                ca_file: str = None, session_token: str = None, mode: Mode = Mode.AUTO) -> MongoClient:
    """ Connect with the database using different URI authentication methods.
    :param host: The database connection host.
    :param port: The database connection port.
    :param replicaset: The replicaset. If None, then, replicaset is not used.
    :param user: The MongoDB username, access key id or session token. If None, then, username is used.
    :param password: The MongoDB password or secret access key. If None, then, password is used.
    :param cert_key_file: The path to the certificate key file.
    :param ca_file: The path to the CA file.
    :param session_token: The session token to use.
    :param mode: The authentication mode. By default, the URL mode is used.
    :return: The MongoDB client.
    """
    if mode == Mode.AUTO:
        raise ValueError('The mode AUTO is not supported directly by this function.'
                         ' You need to use connect() or connect_database() functions.')
    user = quote_plus(user) if user and mode in [Mode.GSSAPI, Mode.Windows] else user
    uri = f'mongodb://'
    if mode not in [Mode.AWS_Lambda, Mode.ECS_Container, Mode.EC2_Instance]:
        uri += f'{user}' if user else ''
        uri += f':{password}' if password else ''
    host = host if host.endswith('/') else f'{host}/'
    port = port if port else DEF_MONGODB_PORT
    host = host[:-1] + f':{port}' + '/' if port else host
    uri += f'@{host}' if user and mode not in [Mode.MONGODB_AWS] else host
    if mode and mode.value:
        uri += (f'?authMechanism={mode.value}' if mode != Mode.URI else '') + \
            (f'&authMechanismProperties={session_token}' if session_token else '')

    if cert_key_file:
        if replicaset:
            client = MongoClient(uri, replicaset=replicaset, tls=True, tlsCertificateKeyFile=cert_key_file,
                                 tlsCAFile=ca_file, serverSelectionTimeoutMS=MAX_SEV_SEL_DELAY)
        else:
            client = MongoClient(uri, tls=True, tlsCertificateKeyFile=cert_key_file,
                                 tlsCAFile=ca_file, serverSelectionTimeoutMS=MAX_SEV_SEL_DELAY)
    elif replicaset:
        client = MongoClient(uri, replicaset=replicaset, serverSelectionTimeoutMS=MAX_SEV_SEL_DELAY)
    else:
        client = MongoClient(uri, serverSelectionTimeoutMS=MAX_SEV_SEL_DELAY)
    client.list_database_names()
    return client


def auth_connect(host: str = 'localhost', port: int = 27017, replicaset: str = None,
                 user: str = None, password: str = None, mode: Mode = Mode.SCRAM_SHA_256) -> MongoClient:
    """ Connect with the database using the specified authentication mechanism.
    :param host: The database connection host.
    :param port: The database connection port.
    :param replicaset: The replicaset. If None, then, replicaset is not used.
    :param user: The MongoDB username, access key id or session token. If None, then, username is used.
    :param password: The MongoDB password or secret access key. If None, then, password is used.
    :param mode: The authentication mode. By default, the URL mode is used.
    :return: The MongoDB client.
    """
    if mode == Mode.AUTO:
        raise ValueError('The mode AUTO is not supported directly by this function.'
                         ' You need to use connect() or connect_database() functions.')
    if replicaset:
        return MongoClient(host, port, replicaset=replicaset, username=user, password=password,
                           authMechanism=mode.value, serverSelectionTimeoutMS=MAX_SEV_SEL_DELAY)
    return MongoClient(host, port, username=user, password=password,
                       authMechanism=mode.value, serverSelectionTimeoutMS=MAX_SEV_SEL_DELAY)


def connect(host: str = 'localhost', port: int = 27017, replicaset: str = None,
            user: str = None, password: str = None, cert_key_file: str = None, ca_file: str = None,
            session_token: str = None, mode: Mode = Mode.AUTO) -> MongoClient:
    """ Connect with the database.
    :param host: The database connection host.
    :param port: The database connection port.
    :param replicaset: The replicaset. If None, then, replicaset is not used.
    :param user: The MongoDB username, access key id or session token. If None, then, username is used.
    :param password: The MongoDB password or secret access key. If None, then, password is used.
    :param mode: The authentication mode. By default, the URL mode is used.
    :param cert_key_file: The path to the certificate key file.
    :param ca_file: The path to the CA file.
    :param session_token: The session token to use.
    :return: The MongoDB client.
    """
    if not user or mode == Mode.NONE:
        return uri_connect(host, port, replicaset, mode=Mode.NONE)
    if mode == Mode.AUTO:
        return detect_connection(host, port, replicaset, user, password, cert_key_file, ca_file, session_token)
    if mode in [Mode.MONGODB_X509, Mode.GSSAPI]:
        return uri_connect(host, port, replicaset, user, None, cert_key_file, ca_file, session_token, mode)
    if mode in [Mode.SCRAM_SHA_256, Mode.SCRAM_SHA_1]:
        return auth_connect(host, port, replicaset, user, password, mode)
    return uri_connect(host, port, replicaset, user, password, cert_key_file, ca_file, session_token, mode)


def connect_database(host: str = 'localhost', port: int = 27017, replicaset: str = None, database: str = None,
                     user: str = None, password: str = None, cert_key_file: str = None, ca_file: str = None,
                     session_token: str = None, mode: Mode = Mode.AUTO) -> Database:
    """ Connect with the database.
    :param host: The database connection host.
    :param port: The database connection port.
    :param replicaset: The replicaset. If None, then, replicaset is not used.
    :param user: The MongoDB username, access key id or session token. If None, then, username is used.
    :param password: The MongoDB password or secret access key. If None, then, password is used.
    :param database: The MongoDB database to connect.
    :param cert_key_file: The path to the certificate key file.
    :param ca_file: The path to the CA file.
    :param session_token: The session token to use.
    :param mode: The authentication mode. By default, the URL mode is used.
    :return: The MongoDB client.
    """
    client = connect(host, port, replicaset, user, password, cert_key_file, ca_file, session_token, mode)
    db = client[database]
    db.list_collection_names()
    return db


def detect_connection(host: str = 'localhost', port: int = 27017, replicaset: str = None,
                      user: str = None, password: str = None,
                      cert_key_file: str = None, ca_file: str = None, session_token: str = None) -> MongoClient:
    """ Connect with the database detecting the connection method.
    :param host: The database connection host.
    :param port: The database connection port.
    :param replicaset: The replicaset. If None, then, replicaset is not used.
    :param user: The MongoDB username, access key id or session token. If None, then, username is used.
    :param password: The MongoDB password or secret access key. If None, then, password is used.
    :param cert_key_file: The path to the certificate key file.
    :param ca_file: The path to the CA file.
    :param session_token: The session token to use.
    :return: The MongoDB client.
    """
    for mode in list(Mode)[2:]:
        try:
            client = connect(host, port, replicaset, user, password, cert_key_file, ca_file, session_token, mode)
            client.list_database_names()
            return client
        except (ServerSelectionTimeoutError, OperationFailure):
            pass
    raise OperationFailure('Authentication error')
