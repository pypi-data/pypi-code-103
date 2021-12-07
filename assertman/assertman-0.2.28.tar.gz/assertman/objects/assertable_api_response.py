from assertman.assertable_mixin import AssertableMixin
from assertman.assert_that  import assert_that
from requests import Session, Response
import requests
# from assertman.helpers.waiting_helper import wait_soft_until


class AssertableResponse(Response, AssertableMixin):

    def __init__(self, origin_responce):
        super(AssertableResponse, self).__init__()
        for k, v in origin_responce.__dict__.items():
            self.__dict__[k] = v

    _waiting_processing = False

    @property
    def _assertable_data(self):
        return self.json()

    def __call__(self, query):
        return self.__class__(self).extract(query)

    # def wait(self):
    #     function = lambda: requests.request(
    #         method=self.request.method,
    #         url=self.request.url,
    #         data=self.request.body,
    #         headers=self.request.headers
    #     ).json()
    #
    #     self._waiting_processing = {"function": function}
    #     return self

    # def should(self, matcher):
    #     if self._waiting_processing:
    #         request = self._waiting_processing["function"]
    #         wait_soft_until(request, matcher, timeout=5)
    #         super(AssertableResponse, self).should(matcher)
    #     else:
    #         super(AssertableResponse, self).should(matcher)


    def filter(self, *args, **kwargs):
        """Отфильтровать проверяемый документ-список, оставив только то, что подходит под переданные условия.

        :param args: условия фильтрации в виде функции или JsonPatch
        :param kwargs: условия фильтрации в виде key-value аргументов
        """
        return assert_that(self._assertable_data).filter(*args, **kwargs)

    def find(self, *args, **kwargs):
        """Найти в проверяемом документе-списке подходящую под условия запись и вернуть ее.

        :param args: условия фильтрации в виде функции или JSONPath
        :param kwargs: условия фильтрации в виде key-value аргументов
        """
        return assert_that(self._assertable_data).find(*args, **kwargs)

    def extract(self, query):
        """Достать нужные данные из проверяемого документа-словаря по ключу или с использованием JSONPath.

        :param query: ключ словаря или JSONPath-селектор
        """
        return assert_that(self._assertable_data).extract(query)
