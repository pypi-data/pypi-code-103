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
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_name: builtins.str,
        table_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: 
        :param table_name: 
        '''
        props = TerraformStateBackendProps(
            bucket_name=bucket_name, table_name=table_name
        )

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
    name_mapping={"bucket_name": "bucketName", "table_name": "tableName"},
)
class TerraformStateBackendProps:
    def __init__(self, *, bucket_name: builtins.str, table_name: builtins.str) -> None:
        '''
        :param bucket_name: 
        :param table_name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "table_name": table_name,
        }

    @builtins.property
    def bucket_name(self) -> builtins.str:
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table_name(self) -> builtins.str:
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

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
