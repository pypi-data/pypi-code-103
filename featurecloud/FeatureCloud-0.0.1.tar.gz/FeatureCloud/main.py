from bottle import Bottle

from FeatureCloud.api import api_server
from FeatureCloud.api.http_web import web_server

from FeatureCloud.engine import app

server = Bottle()


if __name__ == '__main__':
    app.register()
    server.mount('/api', api_server)
    server.mount('/web', web_server)
    server.run(host='localhost', port=5000)
