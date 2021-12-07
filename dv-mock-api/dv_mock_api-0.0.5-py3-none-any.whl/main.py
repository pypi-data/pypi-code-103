#!/usr/bin/env python3

from http import HTTPStatus
from flask import Flask
from dv_mock_api.routes.partner import partner_blueprint
from dv_mock_api.routes.advertiser import advertiser_blueprint
from dv_mock_api.routes.lineitem import lineitem_blueprint
from dv_mock_api.routes.discovery import discover_blueprint
from dv_mock_api.routes.reporting import reporting_blueprint

app = Flask(__name__)

app.register_blueprint(partner_blueprint)
app.register_blueprint(advertiser_blueprint)
app.register_blueprint(lineitem_blueprint)
app.register_blueprint(discover_blueprint)
app.register_blueprint(reporting_blueprint)


@app.errorhandler(404)
def not_found(_):
    return {"message": "Resource not found"}, HTTPStatus.NOT_FOUND


@app.after_request
def add_header(response):
    response.headers['Content-type'] = 'text/plain; charset=utf-8'
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5050', debug=True)
