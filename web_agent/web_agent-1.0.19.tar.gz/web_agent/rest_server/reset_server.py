# coding=utf-8
from flask import Flask
from flask_restful import Api
from .resource.models.ftp_server import thread_start_ftp_server
from .resource.dut_resource import DutResource

APP = Flask(__name__)
API = Api(APP)


API.add_resource(DutResource, "/dut/status")


if __name__ == '__main__':
    thread_start_ftp_server()
    APP.run(host="0.0.0.0", debug=False)
