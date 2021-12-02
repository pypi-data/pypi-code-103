from ..db.sa import sa
from ..models import Log


def create_log(**kwargs):
    model = Log(**kwargs)
    sa.session.add(model)
    return model


def delete_log(id_):
    model = Log.query.filter_by(id_=id_).one()
    sa.session.delete(model)
    return
