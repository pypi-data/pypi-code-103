from apps.frontend.models import model
from main.extension import ma


class Menu(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = model.Menu

    children = ma.List(ma.Nested(lambda: Menu()))