from http import HTTPStatus
from dv_mock_api.settings import ResponseTypes


class DvRequest:
    def get(self):
        return self.request(ResponseTypes.GET)

    def patch(self):
        return self.request(ResponseTypes.PATCH)

    def request(self, request_method: HTTPStatus):
        raise NotImplemented
