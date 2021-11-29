# -*- coding: utf-8 -*-
# @File    : authority.py
# @Time    : 2021/11/26 5:25 下午

import functools
from typing import Callable

from sso.auth import login_required
from sso.auth import resource_check

from basic_sdk.exceptions import PermissionDenied
from basic_sdk.func import replace_slots


def _id():
    i = 1
    while i:
        yield i
        i += 1


_identifier = _id()


class Definition(object):
    def __init__(self, action: str, resource: str, description: str):
        """
        :param action: 操作名 示例: aizao.video.generate
        :param resource: 资源标识 示例: aizao:${organization_id}:${team_id}:video
        :param description: 资源功能说明 示例: 艾造视频生成权限
        """
        self.action = action
        self.resource = resource
        self.description = description
        self.no = next(_identifier)

    @login_required
    def has_permission(self, organization_id: int, team_id: int):
        return resource_check(
            resource=replace_slots(
                self.resource, organization_id=organization_id, team_id=team_id or 0
            ),
            method=self.action,
        )

    def verify(self, func: Callable):
        @functools.wraps(func)
        def inner(resource, *args, **kwargs):
            if not self.has_permission(
                organization_id=resource.organization_id, team_id=resource.team_id
            ):
                raise PermissionDenied(f"禁止访问！你没有 {self.description}")
            return func(resource, *args, **kwargs)

        setattr(inner, "_authority", self)
        return inner

    def validate(self, organization_id: int, team_id: int):
        if not self.has_permission(organization_id=organization_id, team_id=team_id):
            raise PermissionDenied(f"禁止访问! 你没有 {self.description}")


class AuthorityDefinition(Definition):
    def __init__(self, action: str, resource: str, description: str):
        assert "{organization_id}" in resource, "资源标识必须包含 {organization_id} 插槽"
        assert "{team_id}" in resource, "资源标识必须包含 {team_id} 插槽"
        super(AuthorityDefinition, self).__init__(
            action=action, resource=resource, description=description
        )


class AizaoOrgDefinition(AuthorityDefinition):
    def __init__(self, action: str, resource: str, description: str):
        """
        :param action: 会自动添加 prefix "aizao."
        :param resource: 会自动添加 prefix "aizao:${organization_id}:${team_id}:"
        :param description: 说明
        """
        super(AizaoOrgDefinition, self).__init__(
            action="aizao:%s:%s" % (resource, action),
            resource="aizao:${organization_id}:${team_id}:%s" % resource,
            description=description,
        )


class ViewDefinition(Definition):
    def __init__(self, action: str, description: str, team_id: str = "${team_id}"):
        super(ViewDefinition, self).__init__(
            action=f"aizao:view:{action}",
            resource=f"aizao:${{organization_id}}:{team_id}:view",
            description=description,
        )
