from http import HTTPStatus
from dv_mock_api.settings import ResponseTypes


class DbmRequest:
    def get(self):
        return self.request(ResponseTypes.GET_REPORT)

    def run(self):
        return self.request(ResponseTypes.RUN_REPORT)

    def create(self):
        return self.request(ResponseTypes.CREATE_REPORT)

    def download(self):
        return self.request(ResponseTypes.DOWNLOAD_FILE, file=True)

    def request(self, response_type: HTTPStatus, file=False):
        raise NotImplemented
