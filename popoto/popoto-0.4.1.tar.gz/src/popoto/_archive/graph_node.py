from ..fields.field import Field

class GraphNodeField(Field):
    graph_alias: str = ""
    graph_label: str = ""

    def __init__(self, **kwargs):
        super().__init__()
        graphnodefield_defaults = {
            'graph_alias': "",  # required field attr?
            'graph_label': "",  # model.db_key:field_name
        }
        self.field_defaults.update(graphnodefield_defaults)
        # set field_options, let kwargs override
        for k, v in graphnodefield_defaults.items():
            setattr(self, k, kwargs.get(k, v))
