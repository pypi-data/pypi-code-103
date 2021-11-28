from flask_restful.utils import http_status_message

from flask_restful_helper.restful_helper.db_helper import DBHelper

db_helper = DBHelper()


class Logic(object):
    """
    Remember to call super() function in __init__ when inheriting this class.
    """
    _manager = None
    _schema = None

    def __init__(self):
        self.error_messages = {}
        if self._schema is not None:
            self.schema = self._schema()
        if self._manager is not None:
            self.manager = self._manager()

    def list(self, query_args, *args, **kwargs):

        page = query_args.pop('page')
        results_per_page = query_args.pop('results_per_page')
        sort = query_args.pop('sort', 'id:asc')
        collection = self.manager.list(page=page, results_per_page=results_per_page, sort=sort, **query_args)
        return_obj = {
            'data': self.schema.dump(collection, many=True) if collection else [],
            'total': self.manager.count(),
            'sort': sort,
            'size': len(collection),
            'start': (results_per_page * (page - 1)) + 1 if page > 0 else 1
        }
        return return_obj, 200

    def retrieve(self, pk, *args, **kwargs):

        valid_data = self.manager.retrieve(pk=pk)
        if valid_data is None:
            return {'message': http_status_message(404)}, 404
        return {'data': self.schema.dump(valid_data)}, 200

    def create(self, data, query_args, *args, **kwargs):
        with db_helper.auto_commit():
            valid_data = self.validate(data)
            new_instance = self.manager.create(valid_data)
        return {'data': self.schema.dump(new_instance)}, 201

    def update(self, pk, data, partial=False, *args, **kwargs):

        with db_helper.auto_commit():
            valid_data = self.validate(data, partial=partial)
            new_instance = self.manager.update(pk, valid_data)
        return {'data': self.schema.dump(new_instance)}, 200

    def delete(self, pk, *args, **kwargs):
        with db_helper.auto_commit():
            self.manager.delete(targets=pk)

        return None, 204

    def validate(self, data, schema=None, *args, **kwargs):

        if schema is None:
            valid_data = self.schema.load(data, partial=kwargs.get('partial', False))
        else:
            valid_data = schema().load(data, partial=kwargs.get('partial', False))

        return valid_data
