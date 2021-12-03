# coding=utf-8
import sys
import os
from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import marshal_with
from rest_server.resource.models.helper import resource_fields
from test_framework.dut.dut import Dut
from utils import log


PARSER = reqparse.RequestParser()
PARSER.add_argument('name')


class DutResource(Resource):

    def __init__(self):
        pass

    @marshal_with(resource_fields, envelope='resource')
    def post(self):
        log.INFO("REST refresh DUT")
        args = PARSER.parse_args()
        dut = Dut()
        dut.refresh()

