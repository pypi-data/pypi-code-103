import json

class BaseObject(object):

    def to_json_str(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def from_json(self,json_data:dict):
        self.__dict__ = json_data