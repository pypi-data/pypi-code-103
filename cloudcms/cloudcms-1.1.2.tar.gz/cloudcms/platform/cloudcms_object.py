from ..error import RequestError

class CloudCMSObject(object):
    
    def __init__(self, client, data):
        self.client = client
        self._doc = data['_doc']

        self.data = data

    def get_id(self):
        return self._doc

    def get_string(self, field):
        value = self.data.get(field)
        if value:
            value = str(value)
        
        return value
    
    def set_string(self, field, value):
        self.data[field] = value

    def uri(self):
        raise NotImplementedError()

    def reload(self):
        try:
            self.data = self.client.get(self.uri())
        except RequestError:
            self.data = None
            

    def delete(self):
        return self.client.delete(self.uri())

    def update(self):
        return self.client.put(self.uri(), data=self.data)