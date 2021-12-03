from config.configuration import Configuration
from flask import Flask, Response
from json import dumps

__app = Flask(__name__)


@__app.route('/api/config/get')
def __get_config__():
    config = Configuration()
    response = dumps(config)
    del config
    return Response(response, mimetype='application/json')


def start_server():
    config = Configuration()

    if config.config_server_api['enabled']:
        host = config.config_server_api['address']
        port = config.config_server_api['port']
        del config
        __app.run(host, port=port)


if __name__ == '__main__':
    start_server()
