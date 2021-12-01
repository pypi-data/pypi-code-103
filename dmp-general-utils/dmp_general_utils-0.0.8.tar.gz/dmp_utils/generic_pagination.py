class PaginationSchema:
    global ma_object
    global schema_object

    def __init__(self, ma, schema):
        self.ma_object = ma
        self.schema_object = schema

    class Meta:
        fields = ('has_prev', 'has_next', 'next_num', 'page', 'pages', 'per_page', 'prev_num', 'total', 'items')
    items: ma_object.List(ma_object.Nested(schema_object(many=True)))
