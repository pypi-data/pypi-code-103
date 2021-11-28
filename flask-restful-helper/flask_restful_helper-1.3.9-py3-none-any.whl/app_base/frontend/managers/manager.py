from flask_restful_helper import Manager

from apps.frontend.models import model


class Menu(Manager):
    _model = model.Menu

    def list_root_node(self):

        query = self._model.query.filter_by(parent_id=None)
        return query.all()
