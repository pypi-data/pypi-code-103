""" 
@project: gruntest
@file: grunner
@time: 2021/11/19
@software: PyCharm
@author: zy7y
"""
from typing import List, Optional
from json import dumps

import allure

from gruntest.loader import loader_local
from gruntest.schemas import Config, TestStep, RequestSchema
from gruntest.client import Client
from gruntest.parse import Parse


def attach(step, var):
    if var is None:
        var = {}
    allure.attach(
        dumps(
            var,
            ensure_ascii=False,
            indent=4),
        step,
        allure.attachment_type.JSON)


class Grunner:

    config: Config

    steps: List[TestStep]
    _client: Client = Client()
    _parse: Parse = Parse(func_pool=loader_local())

    def url(self, setp_url: Optional[str]):
        if setp_url is not None and self.config.base_url is not None:
            return self.config.base_url + setp_url
        return self.config.base_url or setp_url

    def headers(self, setp_headers: Optional[dict[str, str]]):
        if setp_headers is not None:
            self.config.base_header.update(setp_headers)
        return self.config.base_header

    def parse_request(self, request: RequestSchema):
        """
        解析替换整个requestSchema中的变量 方法
        :param request:
        :return:
        """
        attach('原始请求参数', request.to_dict())
        request.url = self.url(setp_url=request.url)
        request.headers = self.headers(setp_headers=request.headers)

        request.url = self._parse.parse_url(request.url)
        request.headers = self._parse.parse_json(request.headers)
        if request.gql is not None:
            request.method = 'post'
            request.json = self._parse.parse_gql_body(request.gql, request.json)
        else:
            request.params = self._parse.parse_json(request.params)
            request.data = self._parse.parse_json(request.data)
            request.json = self._parse.parse_json(request.json)
        attach('最终请求参数', request.to_dict())
        return request

    def _run_http(self, request: RequestSchema):
        request = self.parse_request(request)
        resp = self._client.request(**request.to_dict())
        attach('响应结果', resp)
        return resp

    def _run_step(self, step: TestStep):
        """运行步骤"""

        self._parse.resp = self._run_http(step.request)

        attach('提取参数', step.extra)
        self._parse.extra_vars(step.extra)
        attach('可用参数', self._parse.data_pool)
        attach('可用方法', {k: [arg for arg in v.__annotations__] for k, v in self._parse.func_pool.items()})

        attach('期望结果', step.expect)
        self._parse.expect_vars(step.expect)

        # self._client.print_info()
        # self._parse.print_maps()

    def _run_testcase(self):
        for step in self.steps:
            with allure.step(step.name or f'步骤{self.steps[step]}'):
                self._run_step(step)

    def test_start(self):
        """启动方法"""
        allure.dynamic.title(self.config.name or '测试用例001')
        self._run_testcase()

