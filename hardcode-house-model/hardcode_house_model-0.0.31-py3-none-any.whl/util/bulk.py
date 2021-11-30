from pymongo.operations import InsertOne, UpdateOne, UpdateMany

class BulkOperationBuilder(object):
    def __init__(self):
        self.requests = []

    def insert_one(self):
        pass

    def update_many(self, filter, update, upsert):
        self.requests.append(UpdateMany(filter, update, upsert))

    def build(self):
        return self.requests