from flask_restful_helper import Logic

from apps.frontend.managers import manager
from apps.frontend.schemas import schema


class Menu(Logic):
    _manager = manager.Menu
    _schema = schema.Menu

    def list(self, query_args, *args, **kwargs):
        if query_args.format == 'menu':
            page = query_args.pop('page')
            results_per_page = query_args.pop('results_per_page')
            sort = query_args.pop('sort', 'id:asc')
            data = self.manager.list_root_node()

            return_obj = {
                'data': self.schema.dump(data, many=True) if data else [],
                'total': self.manager.count(),
                'sort': sort,
                'size': len(data)
            }
            return return_obj, 200

        else:
            return super(Menu, self).list(query_args, *args, **kwargs)
