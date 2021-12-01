from flask_marshmallow import Marshmallow
ma = Marshmallow()


class PaginationSchema(ma.SQLAlchemyAutoSchema):
    # global schema_object

    def __init__(self, schema_object, app):
        # self.schema_object = schema_object
        ma.init_app(app)

    class Meta:
        fields = ('has_prev', 'has_next', 'next_num', 'page', 'pages', 'per_page', 'prev_num', 'total', 'items')
    # items: ma.List(ma.Nested(schema_object(many=True)))
