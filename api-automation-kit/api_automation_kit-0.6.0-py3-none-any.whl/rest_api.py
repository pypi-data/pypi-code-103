"""
This module gives the option to create HTTP requests for GET, POST, PUT, DELETE, and PATCH methods
"""
import re
import allure
import requests as req


class ApiCapabilities:

    def __init__(self):
        self.__response = None
        self.__default_headers = {'content-type': 'application/json', "accept": "*/*"}
        self.__default_params = ['?']

    @allure.step("send get request")
    def get_request(self, url, body='', params='', headers=''):
        """
        send get request, and return the response
        """
        self.url_validator(url)

        if not headers:
            headers = self.__default_headers

        try:
            self.__response = req.get(url, headers=headers, data=body, params=params)

        except Exception as ex:
            self.get_exception(url, ex)

        return self.__response

    @allure.step("send post request")
    def post_request(self, url, body='', params='', headers=''):
        """
        send post request, and return the response
        """
        self.url_validator(url)
        if not headers:
            headers = self.__default_headers

        try:
            self.__response = req.post(url=url, data=body, headers=headers, params=params)

        except Exception as ex:
            self.get_exception(url, ex)

        return self.__response

    @allure.step("send put request")
    def put_request(self, url, body='', params='', headers=''):
        """
        send put request, and return the response
        """
        self.url_validator(url)
        if not headers:
            headers = self.__default_headers

        try:
            self.__response = req.put(url=url, data=body, headers=headers, params=params)

        except Exception as ex:
            self.get_exception(url, ex)

        return self.__response

    @allure.step("send patch request")
    def patch_request(self, url, body='', params='', headers=''):
        """
        send patch request, and return the response
        """
        self.url_validator(url)
        if not headers:
            headers = self.__default_headers

        try:
            self.__response = req.patch(url=url, data=body, headers=headers, params=params)

        except Exception as ex:
            self.get_exception(url, ex)

        return self.__response

    @allure.step("send delete request")
    def delete_request(self, url, body='', params='', headers=''):
        """
        send delete request, and return the response
        """
        self.url_validator(url)
        if not headers:
            headers = self.__default_headers

        try:
            self.__response = req.delete(url=url, data=body, headers=headers, params=params)

        except Exception as ex:
            self.get_exception(url, ex)

        return self.__response

    @allure.step("url validator")
    def url_validator(self, url):
        """ standard validation function that check if provided string is valid url"""
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, url) is not None

    @allure.step("get exception")
    def get_exception(self, url, ex, fail=True):
        msg = str(req.exceptions.RequestException(
            "failed on getting response from " + url + "\n error message description: %s" % str(ex)))
        if not fail:
            print(msg)

        else:
            raise print(msg)
