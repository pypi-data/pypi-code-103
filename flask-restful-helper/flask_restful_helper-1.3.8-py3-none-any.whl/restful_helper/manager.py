from flask_restful_helper.restful_helper.db_helper import DBHelper
from flask_restful_helper.restful_helper.response import abort

db_helper = DBHelper()


class Manager(object):
    _model = None
    _db = None

    def __init__(self):
        self.query = None

    def count(self):

        return self.query.count()

    def list(self, page=None, results_per_page=None, sort=None, *args, **kwargs):

        query = self._model.query


        for key, value in kwargs.items():
            if isinstance(value, list):
                if key.endswith('_between'):
                    key = key.replace('_between', '')
                    query = query.filter(eval(f'self._model.{key}').between(value[0], value[1]))
                elif key.endswith('[]'):
                    key = key.replace('[]', '')
                    query = query.filter(self._model.__dict__[key].in_(value))
                else:
                    query = query.filter(self._model.__dict__[key].in_(value))
            else:
                if isinstance(value, bool):
                    query = query.filter_by(**{key: value})
                else:
                    if value:
                        if key.endswith('_in'):
                            query = query.filter(self._model[key].in_(value))

                        else:
                            query = query.filter_by(**{key: value})
        if sort:
            sort_list = sort.split(',')
            for criteria in sort_list:
                try:
                    sort_by, order = criteria.split(':')
                except ValueError:
                    sort_by = criteria
                    order = 'asc'
                if hasattr(self._model, sort_by):
                    if order == 'asc':
                        query = query.order_by(self._model.__dict__[sort_by])
                    elif order == 'desc':
                        query = query.order_by(self._model.__dict__[sort_by].desc())
        self.query = query
        if page and results_per_page:
            offset = (page - 1) * results_per_page
            query = query.limit(results_per_page).offset(offset)
        return query.all()

    def retrieve(self, pk=None, *args, **kwargs):
        query = self._model.query
        if pk:
            query = query.get(pk)
            return query
        elif kwargs:
            for key, value in kwargs.items():
                if isinstance(value, list):
                    key = key.replace('[]', '')
                    query = query.filter(self._model.__dict__[key].in_(value))
                else:
                    if isinstance(value, bool):
                        query = query.filter_by(**{key: value})
                    else:
                        if value:
                            query = query.filter_by(**{key: value})
            self.query = query
            return query.first()
        else:
            raise abort(404)

    def create(self, data, *args, **kwargs):
        res = self._model(**data)
        db_helper.add(res)

        return res

    def update(self, pk, data, partial=False, *args, **kwargs):
        obj = self._model.query.get(pk)
        if partial and obj is None:
            data['id'] = pk
            res = self.create(data)
            return res
        elif obj is None:
            abort(404)

        for key, value in data.items():
            setattr(obj, key, value)

        return obj

    def delete(self, targets, multi=False, *args, **kwargs):

        if multi:
            if not isinstance(targets, list):
                raise TypeError()
            for target in targets:
                instance = self._model.query.get(target)
                if instance:
                    db_helper.delete(instance)
                    db_helper.flush()

        else:
            instance = self._model.query.get(targets)
            db_helper.delete(instance)

    def delete_by_instance(self, targets, multi=False, *args, **kwargs):

        if multi:
            if not isinstance(targets, list):
                raise TypeError()
            for target in targets:
                db_helper.delete(target)
        else:
            db_helper.delete(targets)
