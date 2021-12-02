from ..db.sa import sa
from ..db.backup import request_backup_db


##__________________________________________________________________||
def commit():
    """Commit the changes to the DB"""
    sa.session.commit()
    request_backup_db()


##__________________________________________________________________||
