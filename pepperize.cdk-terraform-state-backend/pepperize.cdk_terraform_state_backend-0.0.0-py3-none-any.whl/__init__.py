'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-terraform-state-backend?style=flat-square)](https://github.com/pepperize/cdk-terraform-state-backend/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-terraform-state-backend?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-terraform-state-backend)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-terraform-state-backend?style=flat-square)](https://pypi.org/project/pepperize.cdk-terraform-state-backend/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.TerraformStateBackend?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.TerraformStateBackend/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-terraform-state-backend/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-terraform-state-backend/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-terraform-state-backend?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-terraform-state-backend/releases)

# AWS CDK Terraform state backend
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_dynamodb
import aws_cdk.aws_s3
import aws_cdk.core


class TerraformStateBackend(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-terraform-state-backend.TerraformStateBackend",
):
    def __init__(
        self,
        scope: aws_cdk.core.Stack,
        id: builtins.str,
        *,
        name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name_prefix: 
        '''
        props = TerraformStateBackendProps(name_prefix=name_prefix)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "table"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-terraform-state-backend.TerraformStateBackendProps",
    jsii_struct_bases=[],
    name_mapping={"name_prefix": "namePrefix"},
)
class TerraformStateBackendProps:
    def __init__(self, *, name_prefix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param name_prefix: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TerraformStateBackendProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TerraformStateBackend",
    "TerraformStateBackendProps",
]

publication.publish()
