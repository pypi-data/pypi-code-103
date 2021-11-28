from sys import argv
from os import path
from logging import basicConfig, warning

MODE_DEBUG = '--debug' in argv

basicConfig(level="WARNING")

# directorios
ROOT_API = path.dirname(path.realpath(__file__))
RESOURCES_FILE_PATH = path.join(ROOT_API, 'resources')
DIRECTORY_TEMP_PATH = path.join(ROOT_API, "__temp__")

# envirenment
ENV = "DEV"

# puerto
PORT = <<PORT>>

# identificador de la aplicacion
APPLICATION_CODE = '<<APPLICATION_CODE>>'

# IP Local servidor api dealergeek
DGAPI_SERVER = ''


# cadena de coneccion
MONGO_CONN = {
    'user': '',
    'password': '',
    'host': '',
    'database': '',
    'port': 27017
}

if '--prod' in argv:
    ENV = "PROD"
    API_SERVER = ''
    MONGO_CONN.update({
        'password': '',
        'database': ''
    })
elif '--demo' in argv:
    ENV = "DEMO"
    API_SERVER = ''
    MONGO_CONN.update({
        'password': '',
        'database': ''
    })
warning("%s MODE" % ENV)
