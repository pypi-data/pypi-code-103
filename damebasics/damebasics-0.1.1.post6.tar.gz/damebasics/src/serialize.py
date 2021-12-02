import json

class Serialize(object):
    def __init__(self):
        self.s = None

    def serialize_json(self, instance=None, path=None):
        dt = {}
        dt.update(vars(instance))
        with open(path, "w") as file:
            json.dump(dt, file)
        
    def deserialize_json(self, cls=None, path=None):
        with open(path, "r") as file:
            data = json.load(file)
        instance = object.__new__(cls)
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
        
# s = Serialize
# json.dumps(Serialize)

