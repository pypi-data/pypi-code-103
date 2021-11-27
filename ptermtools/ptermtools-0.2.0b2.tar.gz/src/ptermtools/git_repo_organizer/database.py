from mongoengine import (
    Document,
    ListField,
    ObjectIdField,
    StringField,
    URLField,
    connect,
)

connect()


class RepoDB(Document):
    name = StringField(required=True)
    _id = ObjectIdField(required=True)
    url = URLField(required=True)
    path = StringField(required=True)
    groups = ListField(required=True)
    projects = ListField(required=True)
