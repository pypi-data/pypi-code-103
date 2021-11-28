from flask_restful_helper import ApiView

from apps.frontend.logics import logic


class Menu(ApiView):
    _logic = logic.Menu

    def set_get_args(self):
        self.parser.add_argument('format',
                                 choices=['standard', 'menu'],
                                 default='standard',
                                 required=False,
                                 location='args')
