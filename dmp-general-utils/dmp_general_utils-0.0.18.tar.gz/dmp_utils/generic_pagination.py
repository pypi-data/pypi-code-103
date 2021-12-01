from flask_marshmallow import Marshmallow


def get_schema_object():
    return PaginationSchema.schema_object


def get_ma():
    return PaginationSchema.ma


class PaginationSchema:
    schema_object = None
    ma = Marshmallow()

    def __init__(self, ma, app, schema_object):
        self.schema_object = schema_object
        self.ma = ma
        self.ma.init_app(app)
        self.pagination_sub_class = self.PaginationSchemaSubClass()

    def xd(self):
        return self.schema_object

    class PaginationSchemaSubClass(ma.SQLAlchemyAutoSchema):
        schema_object = get_schema_object()
        ma = get_ma()

        class Meta:
            fields = ('has_prev', 'has_next', 'next_num', 'page', 'pages', 'per_page', 'prev_num', 'total', 'items')

        items: ma.List(ma.Nested(schema_object))
