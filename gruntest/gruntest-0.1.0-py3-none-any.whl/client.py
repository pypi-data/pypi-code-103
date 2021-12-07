""" 
@project: gruntest
@file: client 
@time: 2021/11/18
@software: PyCharm
@author: zy7y
"""
from json import JSONDecodeError, dumps

from requests import Session, RequestException

from gruntest.schemas import RequestInfoSchema, InterFaceInfos, ResponseInfoSchema


class GruntClientError(Exception):
    ...


class Client(Session):
    _infos = InterFaceInfos()

    def __int__(self):
        super().__init__()

    def _request(self, method: str, url: str, **kwargs):
        try:
            return super().request(method, url, **kwargs)
        except RequestException:
            raise GruntClientError('gruntest 客户端错误.')

    def print_info(self):
        result = dumps(self.infos, sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False)
        print(result)

    @property
    def infos(self):
        return self._infos()

    def request(self, method: str, url: str, **kwargs):
        self._infos.request = RequestInfoSchema(url=url, method=method).to_dict()
        kwargs.setdefault("timeout", 120)
        kwargs["stream"] = True
        kwargs.pop("gql")
        self._infos.request.update(**kwargs)
        response = self._request(method, url, **kwargs)
        error: str = 'None'
        try:
            resp = response.json()
        except JSONDecodeError:
            resp = response.text
        except GruntClientError as e:
            resp = {}
            error = str(e)
        self._infos.response = ResponseInfoSchema(code=response.status_code,
                                                  time=round(response.elapsed.total_seconds() * 1000, 2),
                                                  response=resp,
                                                  err_msg=error
                                                  ).to_dict()
        return resp
