from active_alchemy import ActiveAlchemy
import os

db_path = './migration.db'
db_path = os.path.abspath(db_path)
db = ActiveAlchemy('sqlite:////%s' % db_path)

class CacheDB:

    @staticmethod
    def should_update(st13, time_stamp):
        result = CollectionFile.query().filter(CollectionFile.st13 == st13)
        if len(list(result)) == 1:
            if result[0].last_modified < time_stamp:
                return True
            return False
        else:
            return True

    @staticmethod
    def update_record(st13, time_stamp, path_on_disk):
        record = CollectionFile.upsert(st13=st13)
        record.last_modified = time_stamp
        record.path_on_disk = path_on_disk
        record.save()


class CollectionFile(db.Model):
    __tablename__ = 'collection_file'
    st13 = db.Column(db.String)
    last_modified = db.Column(db.String)
    path_on_disk = db.Column(db.String)

    @staticmethod
    def upsert(st13=None):
        result = CollectionFile.query().filter(CollectionFile.st13 == st13)
        if len(list(result)) == 1:
            return result[0]
        else:
            return CollectionFile.create(st13=st13)

db.create_all()



