from flask_marshmallow import Marshmallow

ma = Marshmallow()


class PaginationSchema(ma.SQLAlchemyAutoSchema):
    # global schema_object
    schema_object = None
    marsh = ma

    def __init__(self, mar, app, schema_object):
        self.schema_object = schema_object
        self.marsh = mar
        self.marsh.init_app(app)

    class Meta:
        fields = ('has_prev', 'has_next', 'next_num', 'page', 'pages', 'per_page', 'prev_num', 'total', 'items')

    items: marsh.List(marsh.Nested(schema_object))
