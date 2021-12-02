from ..models import ProductFilePath

from ..db.sa import sa

def create_product_file_path(**kwargs):
    model = ProductFilePath(**kwargs)
    sa.session.add(model)
    return model

def update_product_file_path(path_id, **kwargs):
    model = ProductFilePath.query.filter_by(path_id=path_id).one()
    for k, v in kwargs.items():
        setattr(model, k, v)
    return model

def delete_product_file_path(path_id):
    model = ProductFilePath.query.filter_by(path_id=path_id).one()
    sa.session.delete(model)
    return
