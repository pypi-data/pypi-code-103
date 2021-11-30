import orjson
from fastapi.responses import ORJSONResponse


class JsonResponse(ORJSONResponse):
    total_time = None

    def __init__(self, total_time: float = None, *args, **kwargs) -> None:
        self.total_time = total_time
        super().__init__(*args, **kwargs)

    @property
    def is_ok(self) -> bool:
        return self.status_code < 400

    def as_dict(self):
        if self.media_type == "application/json":
            return orjson.loads(self.body)
        return {}
