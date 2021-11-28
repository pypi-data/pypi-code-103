from flask import request
from flask_restful import Resource, reqparse

from flask import make_response, jsonify


class ApiView(Resource):
    _logic = None
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.query_args = self.parser.parse_args()
        self.set_global_args()
        self.set_query_args()
        if self._logic is not None:
            self.logic = self._logic()

    def set_query_args(self):
        self.set_global_args()
        self.query_args = self.parser.parse_args()
        if request.method == 'GET':
            self.set_get_args()
        elif request.method == 'POST':
            self.set_post_args()
        elif request.method == 'PUT':
            self.set_put_args()
        elif request.method == 'PATCH':
            self.set_patch_args()
        elif request.method == 'DELETE':
            self.set_delete_args()
        self.query_args = self.parser.parse_args()

    def set_global_args(self):
        argument1 = {'name': 'page', 'default': 0, 'type': int, 'location': 'args'}
        argument2 = {'name': 'results_per_page', 'default': 0, 'type': int, 'location': 'args'}
        self.add_union_argument(argument1, argument2)
        self.parser.add_argument('sort', type=str, default='id:asc', required=False, location='args')

    def add_mutex_argument(self, argument1, argument2):
        """
        arg1與arg2互斥
        :param arg1:
        :param arg2:
        :param type1:
        :param type2:
        :param location:
        :return:
        """
        argument1_name = argument1.pop('name')
        argument2_name = argument2.pop('name')
        self.parser.add_argument(argument1_name, **argument1)
        self.parser.add_argument(argument2_name, **argument2)
        self.query_args = self.parser.parse_args()
        if self.query_args[argument2_name]:
            self.parser.remove_argument(argument1_name)
        elif self.query_args[argument1_name]:
            self.parser.remove_argument(argument2_name)

        self.query_args = self.parser.parse_args()

    def add_union_argument(self, argument1, argument2):
        """
        arg1 與 arg2 必須同時被設定
        :param argument1:
        :param argument2:
        :return:
        """
        argument1_name = argument1.pop('name')
        argument2_name = argument2.pop('name')
        self.parser.add_argument(argument1_name, **argument1)
        self.parser.add_argument(argument2_name, **argument2)
        self.query_args = self.parser.parse_args()
        if self.query_args[argument2_name]:
            self.parser.replace_argument(argument1_name, **argument1, required=True)
        elif self.query_args[argument1_name]:
            self.parser.replace_argument(argument2_name, **argument2, required=True)

    def add_filter_argument(self, name, type, required, location):
        """
        一次加入單數與複數參數
        :param name:
        :param type:
        :param required:
        :param location:
        :return:
        """
        multiple_name = f'{name}[]'
        self.parser.add_argument(name, type=type, required=required, location=location)
        self.parser.add_argument(multiple_name, type=type, required=required, action='append', location=location)
        self.query_args = self.parser.parse_args()
        if self.query_args[name]:
            self.parser.remove_argument(multiple_name)
        elif self.query_args[multiple_name]:
            self.parser.remove_argument(name)

    def set_get_args(self):
        pass

    def get(self, pk=None):
        if pk is None:
            data, status_code = self.logic.list(query_args=self.query_args)
            return make_response(jsonify(data), status_code)
        else:
            data, status_code = self.logic.retrieve(pk, query_args=self.query_args)
            return make_response(jsonify(data), status_code)

    def set_post_args(self):
        pass

    def post(self):
        request_data = request.get_json(force=True)
        data, status_code = self.logic.create(data=request_data, query_args=self.query_args)
        return make_response(jsonify(data), status_code)

    def set_put_args(self):
        pass

    def put(self, pk):
        request_data = request.get_json(force=True)
        data, status_code = self.logic.update(pk=pk, data=request_data, query_args=self.query_args)
        return make_response(jsonify(data), status_code)

    def set_patch_args(self):
        pass

    def patch(self, pk):
        request_data = request.get_json(force=True)
        data, status_code = self.logic.update(pk=pk, data=request_data, partial=True, query_args=self.query_args)
        return make_response(jsonify(data), status_code)

    def set_delete_args(self):
        pass

    def delete(self, pk):
        data, status_code = self.logic.delete(pk=pk)
        return make_response(jsonify(data), status_code)
