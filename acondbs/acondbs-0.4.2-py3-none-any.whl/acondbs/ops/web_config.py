from ..db.sa import sa
from ..models import WebConfig


def save_web_config(**kwargs):
    model = WebConfig.query.one_or_none()
    if model:
        for k, v in kwargs.items():
            setattr(model, k, v)
    else:
        model = WebConfig(**kwargs)
        sa.session.add(model)
    return model
