from flask_marshmallow import Marshmallow


class PaginationSchema:
    schema_object = None
    ma = Marshmallow()

    def __init__(self, ma, app, schema_object):
        self.schema_object = schema_object
        self.ma = ma
        self.ma.init_app(app)
        self.ma = self.ma.SQLAlchemyAutoSchema

    class Meta:
        fields = ('has_prev', 'has_next', 'next_num', 'page', 'pages', 'per_page', 'prev_num', 'total', 'items')
    items: ma.List(ma.Nested(schema_object))
