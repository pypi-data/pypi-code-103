class Embed:
    def __init__(self, title:str = None, description:str = None):
        self.title = title
        self.description = description
        self.fields = []

    def add_field(self, name:str, value:str):
        self.fields.appends({"name": name, "value": "value"})

    def to_dict(self):
        payload = {}
        if self.title is not None:
            payload["title"] = self.title
        if self.description is not None:
            payload["description"] = self.description
        if len(self.fields) != 0:
            payload["fields"] = [i for i in self.fields]
        return payload