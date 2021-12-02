'''
# AWS::MemoryDB Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_memorydb as aws_memorydb
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_9df397a6,
    CfnTag as _CfnTag_f6864754,
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnACL(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_memorydb.CfnACL",
):
    '''A CloudFormation ``AWS::MemoryDB::ACL``.

    :cloudformationResource: AWS::MemoryDB::ACL
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_memorydb as memorydb
        
        cfn_aCL = memorydb.CfnACL(self, "MyCfnACL",
            acl_name="aclName",
        
            # the properties below are optional
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            user_names=["userNames"]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        acl_name: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        user_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::MemoryDB::ACL``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param acl_name: ``AWS::MemoryDB::ACL.ACLName``.
        :param tags: ``AWS::MemoryDB::ACL.Tags``.
        :param user_names: ``AWS::MemoryDB::ACL.UserNames``.
        '''
        props = CfnACLProps(acl_name=acl_name, tags=tags, user_names=user_names)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclName")
    def acl_name(self) -> builtins.str:
        '''``AWS::MemoryDB::ACL.ACLName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html#cfn-memorydb-acl-aclname
        '''
        return typing.cast(builtins.str, jsii.get(self, "aclName"))

    @acl_name.setter
    def acl_name(self, value: builtins.str) -> None:
        jsii.set(self, "aclName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MemoryDB::ACL.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html#cfn-memorydb-acl-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNames")
    def user_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::MemoryDB::ACL.UserNames``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html#cfn-memorydb-acl-usernames
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userNames"))

    @user_names.setter
    def user_names(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "userNames", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_memorydb.CfnACLProps",
    jsii_struct_bases=[],
    name_mapping={"acl_name": "aclName", "tags": "tags", "user_names": "userNames"},
)
class CfnACLProps:
    def __init__(
        self,
        *,
        acl_name: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        user_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::MemoryDB::ACL``.

        :param acl_name: ``AWS::MemoryDB::ACL.ACLName``.
        :param tags: ``AWS::MemoryDB::ACL.Tags``.
        :param user_names: ``AWS::MemoryDB::ACL.UserNames``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_memorydb as memorydb
            
            cfn_aCLProps = memorydb.CfnACLProps(
                acl_name="aclName",
            
                # the properties below are optional
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                user_names=["userNames"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "acl_name": acl_name,
        }
        if tags is not None:
            self._values["tags"] = tags
        if user_names is not None:
            self._values["user_names"] = user_names

    @builtins.property
    def acl_name(self) -> builtins.str:
        '''``AWS::MemoryDB::ACL.ACLName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html#cfn-memorydb-acl-aclname
        '''
        result = self._values.get("acl_name")
        assert result is not None, "Required property 'acl_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::MemoryDB::ACL.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html#cfn-memorydb-acl-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def user_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::MemoryDB::ACL.UserNames``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-acl.html#cfn-memorydb-acl-usernames
        '''
        result = self._values.get("user_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnACLProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCluster(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_memorydb.CfnCluster",
):
    '''A CloudFormation ``AWS::MemoryDB::Cluster``.

    :cloudformationResource: AWS::MemoryDB::Cluster
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_memorydb as memorydb
        
        cfn_cluster = memorydb.CfnCluster(self, "MyCfnCluster",
            acl_name="aclName",
            cluster_name="clusterName",
            node_type="nodeType",
        
            # the properties below are optional
            auto_minor_version_upgrade=False,
            description="description",
            engine_version="engineVersion",
            final_snapshot_name="finalSnapshotName",
            kms_key_id="kmsKeyId",
            maintenance_window="maintenanceWindow",
            num_replicas_per_shard=123,
            num_shards=123,
            parameter_group_name="parameterGroupName",
            port=123,
            security_group_ids=["securityGroupIds"],
            snapshot_arns=["snapshotArns"],
            snapshot_name="snapshotName",
            snapshot_retention_limit=123,
            snapshot_window="snapshotWindow",
            sns_topic_arn="snsTopicArn",
            sns_topic_status="snsTopicStatus",
            subnet_group_name="subnetGroupName",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            tls_enabled=False
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        acl_name: builtins.str,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        cluster_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        node_type: builtins.str,
        num_replicas_per_shard: typing.Optional[jsii.Number] = None,
        num_shards: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        sns_topic_status: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        tls_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::MemoryDB::Cluster``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param acl_name: ``AWS::MemoryDB::Cluster.ACLName``.
        :param auto_minor_version_upgrade: ``AWS::MemoryDB::Cluster.AutoMinorVersionUpgrade``.
        :param cluster_name: ``AWS::MemoryDB::Cluster.ClusterName``.
        :param description: ``AWS::MemoryDB::Cluster.Description``.
        :param engine_version: ``AWS::MemoryDB::Cluster.EngineVersion``.
        :param final_snapshot_name: ``AWS::MemoryDB::Cluster.FinalSnapshotName``.
        :param kms_key_id: ``AWS::MemoryDB::Cluster.KmsKeyId``.
        :param maintenance_window: ``AWS::MemoryDB::Cluster.MaintenanceWindow``.
        :param node_type: ``AWS::MemoryDB::Cluster.NodeType``.
        :param num_replicas_per_shard: ``AWS::MemoryDB::Cluster.NumReplicasPerShard``.
        :param num_shards: ``AWS::MemoryDB::Cluster.NumShards``.
        :param parameter_group_name: ``AWS::MemoryDB::Cluster.ParameterGroupName``.
        :param port: ``AWS::MemoryDB::Cluster.Port``.
        :param security_group_ids: ``AWS::MemoryDB::Cluster.SecurityGroupIds``.
        :param snapshot_arns: ``AWS::MemoryDB::Cluster.SnapshotArns``.
        :param snapshot_name: ``AWS::MemoryDB::Cluster.SnapshotName``.
        :param snapshot_retention_limit: ``AWS::MemoryDB::Cluster.SnapshotRetentionLimit``.
        :param snapshot_window: ``AWS::MemoryDB::Cluster.SnapshotWindow``.
        :param sns_topic_arn: ``AWS::MemoryDB::Cluster.SnsTopicArn``.
        :param sns_topic_status: ``AWS::MemoryDB::Cluster.SnsTopicStatus``.
        :param subnet_group_name: ``AWS::MemoryDB::Cluster.SubnetGroupName``.
        :param tags: ``AWS::MemoryDB::Cluster.Tags``.
        :param tls_enabled: ``AWS::MemoryDB::Cluster.TLSEnabled``.
        '''
        props = CfnClusterProps(
            acl_name=acl_name,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            cluster_name=cluster_name,
            description=description,
            engine_version=engine_version,
            final_snapshot_name=final_snapshot_name,
            kms_key_id=kms_key_id,
            maintenance_window=maintenance_window,
            node_type=node_type,
            num_replicas_per_shard=num_replicas_per_shard,
            num_shards=num_shards,
            parameter_group_name=parameter_group_name,
            port=port,
            security_group_ids=security_group_ids,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            sns_topic_arn=sns_topic_arn,
            sns_topic_status=sns_topic_status,
            subnet_group_name=subnet_group_name,
            tags=tags,
            tls_enabled=tls_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclName")
    def acl_name(self) -> builtins.str:
        '''``AWS::MemoryDB::Cluster.ACLName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-aclname
        '''
        return typing.cast(builtins.str, jsii.get(self, "aclName"))

    @acl_name.setter
    def acl_name(self, value: builtins.str) -> None:
        jsii.set(self, "aclName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: ARN
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrClusterEndpointAddress")
    def attr_cluster_endpoint_address(self) -> builtins.str:
        '''
        :cloudformationAttribute: ClusterEndpoint.Address
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrClusterEndpointAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrClusterEndpointPort")
    def attr_cluster_endpoint_port(self) -> jsii.Number:
        '''
        :cloudformationAttribute: ClusterEndpoint.Port
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrClusterEndpointPort"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrParameterGroupStatus")
    def attr_parameter_group_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: ParameterGroupStatus
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrParameterGroupStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::MemoryDB::Cluster.AutoMinorVersionUpgrade``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-autominorversionupgrade
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "autoMinorVersionUpgrade", value)

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''``AWS::MemoryDB::Cluster.ClusterName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-clustername
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.EngineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-engineversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotName")
    def final_snapshot_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.FinalSnapshotName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-finalsnapshotname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "finalSnapshotName"))

    @final_snapshot_name.setter
    def final_snapshot_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "finalSnapshotName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyId")
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-kmskeyid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyId"))

    @kms_key_id.setter
    def kms_key_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "kmsKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.MaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-maintenancewindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindow"))

    @maintenance_window.setter
    def maintenance_window(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "maintenanceWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        '''``AWS::MemoryDB::Cluster.NodeType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-nodetype
        '''
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numReplicasPerShard")
    def num_replicas_per_shard(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.NumReplicasPerShard``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-numreplicaspershard
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numReplicasPerShard"))

    @num_replicas_per_shard.setter
    def num_replicas_per_shard(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numReplicasPerShard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.NumShards``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-numshards
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numShards"))

    @num_shards.setter
    def num_shards(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "numShards", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.ParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-parametergroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterGroupName"))

    @parameter_group_name.setter
    def parameter_group_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "parameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.Port``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-port
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "port"))

    @port.setter
    def port(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::MemoryDB::Cluster.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-securitygroupids
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArns")
    def snapshot_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::MemoryDB::Cluster.SnapshotArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotarns
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "snapshotArns"))

    @snapshot_arns.setter
    def snapshot_arns(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "snapshotArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotName")
    def snapshot_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnapshotName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotName"))

    @snapshot_name.setter
    def snapshot_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snapshotName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.SnapshotRetentionLimit``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotretentionlimit
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "snapshotRetentionLimit"))

    @snapshot_retention_limit.setter
    def snapshot_retention_limit(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "snapshotRetentionLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnapshotWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotwindow
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotWindow"))

    @snapshot_window.setter
    def snapshot_window(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snapshotWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnsTopicArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snstopicarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snsTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicStatus")
    def sns_topic_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnsTopicStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snstopicstatus
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicStatus"))

    @sns_topic_status.setter
    def sns_topic_status(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snsTopicStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-subnetgroupname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetGroupName"))

    @subnet_group_name.setter
    def subnet_group_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "subnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MemoryDB::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsEnabled")
    def tls_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::MemoryDB::Cluster.TLSEnabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-tlsenabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "tlsEnabled"))

    @tls_enabled.setter
    def tls_enabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "tlsEnabled", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_memorydb.CfnCluster.EndpointProperty",
        jsii_struct_bases=[],
        name_mapping={"address": "address", "port": "port"},
    )
    class EndpointProperty:
        def __init__(
            self,
            *,
            address: typing.Optional[builtins.str] = None,
            port: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param address: ``CfnCluster.EndpointProperty.Address``.
            :param port: ``CfnCluster.EndpointProperty.Port``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-memorydb-cluster-endpoint.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_memorydb as memorydb
                
                endpoint_property = memorydb.CfnCluster.EndpointProperty(
                    address="address",
                    port=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if address is not None:
                self._values["address"] = address
            if port is not None:
                self._values["port"] = port

        @builtins.property
        def address(self) -> typing.Optional[builtins.str]:
            '''``CfnCluster.EndpointProperty.Address``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-memorydb-cluster-endpoint.html#cfn-memorydb-cluster-endpoint-address
            '''
            result = self._values.get("address")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def port(self) -> typing.Optional[jsii.Number]:
            '''``CfnCluster.EndpointProperty.Port``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-memorydb-cluster-endpoint.html#cfn-memorydb-cluster-endpoint-port
            '''
            result = self._values.get("port")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EndpointProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_memorydb.CfnClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "acl_name": "aclName",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "cluster_name": "clusterName",
        "description": "description",
        "engine_version": "engineVersion",
        "final_snapshot_name": "finalSnapshotName",
        "kms_key_id": "kmsKeyId",
        "maintenance_window": "maintenanceWindow",
        "node_type": "nodeType",
        "num_replicas_per_shard": "numReplicasPerShard",
        "num_shards": "numShards",
        "parameter_group_name": "parameterGroupName",
        "port": "port",
        "security_group_ids": "securityGroupIds",
        "snapshot_arns": "snapshotArns",
        "snapshot_name": "snapshotName",
        "snapshot_retention_limit": "snapshotRetentionLimit",
        "snapshot_window": "snapshotWindow",
        "sns_topic_arn": "snsTopicArn",
        "sns_topic_status": "snsTopicStatus",
        "subnet_group_name": "subnetGroupName",
        "tags": "tags",
        "tls_enabled": "tlsEnabled",
    },
)
class CfnClusterProps:
    def __init__(
        self,
        *,
        acl_name: builtins.str,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        cluster_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        node_type: builtins.str,
        num_replicas_per_shard: typing.Optional[jsii.Number] = None,
        num_shards: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        sns_topic_status: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        tls_enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::MemoryDB::Cluster``.

        :param acl_name: ``AWS::MemoryDB::Cluster.ACLName``.
        :param auto_minor_version_upgrade: ``AWS::MemoryDB::Cluster.AutoMinorVersionUpgrade``.
        :param cluster_name: ``AWS::MemoryDB::Cluster.ClusterName``.
        :param description: ``AWS::MemoryDB::Cluster.Description``.
        :param engine_version: ``AWS::MemoryDB::Cluster.EngineVersion``.
        :param final_snapshot_name: ``AWS::MemoryDB::Cluster.FinalSnapshotName``.
        :param kms_key_id: ``AWS::MemoryDB::Cluster.KmsKeyId``.
        :param maintenance_window: ``AWS::MemoryDB::Cluster.MaintenanceWindow``.
        :param node_type: ``AWS::MemoryDB::Cluster.NodeType``.
        :param num_replicas_per_shard: ``AWS::MemoryDB::Cluster.NumReplicasPerShard``.
        :param num_shards: ``AWS::MemoryDB::Cluster.NumShards``.
        :param parameter_group_name: ``AWS::MemoryDB::Cluster.ParameterGroupName``.
        :param port: ``AWS::MemoryDB::Cluster.Port``.
        :param security_group_ids: ``AWS::MemoryDB::Cluster.SecurityGroupIds``.
        :param snapshot_arns: ``AWS::MemoryDB::Cluster.SnapshotArns``.
        :param snapshot_name: ``AWS::MemoryDB::Cluster.SnapshotName``.
        :param snapshot_retention_limit: ``AWS::MemoryDB::Cluster.SnapshotRetentionLimit``.
        :param snapshot_window: ``AWS::MemoryDB::Cluster.SnapshotWindow``.
        :param sns_topic_arn: ``AWS::MemoryDB::Cluster.SnsTopicArn``.
        :param sns_topic_status: ``AWS::MemoryDB::Cluster.SnsTopicStatus``.
        :param subnet_group_name: ``AWS::MemoryDB::Cluster.SubnetGroupName``.
        :param tags: ``AWS::MemoryDB::Cluster.Tags``.
        :param tls_enabled: ``AWS::MemoryDB::Cluster.TLSEnabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_memorydb as memorydb
            
            cfn_cluster_props = memorydb.CfnClusterProps(
                acl_name="aclName",
                cluster_name="clusterName",
                node_type="nodeType",
            
                # the properties below are optional
                auto_minor_version_upgrade=False,
                description="description",
                engine_version="engineVersion",
                final_snapshot_name="finalSnapshotName",
                kms_key_id="kmsKeyId",
                maintenance_window="maintenanceWindow",
                num_replicas_per_shard=123,
                num_shards=123,
                parameter_group_name="parameterGroupName",
                port=123,
                security_group_ids=["securityGroupIds"],
                snapshot_arns=["snapshotArns"],
                snapshot_name="snapshotName",
                snapshot_retention_limit=123,
                snapshot_window="snapshotWindow",
                sns_topic_arn="snsTopicArn",
                sns_topic_status="snsTopicStatus",
                subnet_group_name="subnetGroupName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                tls_enabled=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "acl_name": acl_name,
            "cluster_name": cluster_name,
            "node_type": node_type,
        }
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if description is not None:
            self._values["description"] = description
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_name is not None:
            self._values["final_snapshot_name"] = final_snapshot_name
        if kms_key_id is not None:
            self._values["kms_key_id"] = kms_key_id
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if num_replicas_per_shard is not None:
            self._values["num_replicas_per_shard"] = num_replicas_per_shard
        if num_shards is not None:
            self._values["num_shards"] = num_shards
        if parameter_group_name is not None:
            self._values["parameter_group_name"] = parameter_group_name
        if port is not None:
            self._values["port"] = port
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if snapshot_arns is not None:
            self._values["snapshot_arns"] = snapshot_arns
        if snapshot_name is not None:
            self._values["snapshot_name"] = snapshot_name
        if snapshot_retention_limit is not None:
            self._values["snapshot_retention_limit"] = snapshot_retention_limit
        if snapshot_window is not None:
            self._values["snapshot_window"] = snapshot_window
        if sns_topic_arn is not None:
            self._values["sns_topic_arn"] = sns_topic_arn
        if sns_topic_status is not None:
            self._values["sns_topic_status"] = sns_topic_status
        if subnet_group_name is not None:
            self._values["subnet_group_name"] = subnet_group_name
        if tags is not None:
            self._values["tags"] = tags
        if tls_enabled is not None:
            self._values["tls_enabled"] = tls_enabled

    @builtins.property
    def acl_name(self) -> builtins.str:
        '''``AWS::MemoryDB::Cluster.ACLName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-aclname
        '''
        result = self._values.get("acl_name")
        assert result is not None, "Required property 'acl_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::MemoryDB::Cluster.AutoMinorVersionUpgrade``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-autominorversionupgrade
        '''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''``AWS::MemoryDB::Cluster.ClusterName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-clustername
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.EngineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-engineversion
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.FinalSnapshotName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-finalsnapshotname
        '''
        result = self._values.get("final_snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_id(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.KmsKeyId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-kmskeyid
        '''
        result = self._values.get("kms_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.MaintenanceWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-maintenancewindow
        '''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_type(self) -> builtins.str:
        '''``AWS::MemoryDB::Cluster.NodeType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-nodetype
        '''
        result = self._values.get("node_type")
        assert result is not None, "Required property 'node_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def num_replicas_per_shard(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.NumReplicasPerShard``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-numreplicaspershard
        '''
        result = self._values.get("num_replicas_per_shard")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_shards(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.NumShards``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-numshards
        '''
        result = self._values.get("num_shards")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.ParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-parametergroupname
        '''
        result = self._values.get("parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.Port``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-port
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::MemoryDB::Cluster.SecurityGroupIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-securitygroupids
        '''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::MemoryDB::Cluster.SnapshotArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotarns
        '''
        result = self._values.get("snapshot_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnapshotName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotname
        '''
        result = self._values.get("snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        '''``AWS::MemoryDB::Cluster.SnapshotRetentionLimit``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotretentionlimit
        '''
        result = self._values.get("snapshot_retention_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snapshot_window(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnapshotWindow``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snapshotwindow
        '''
        result = self._values.get("snapshot_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnsTopicArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snstopicarn
        '''
        result = self._values.get("sns_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns_topic_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SnsTopicStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-snstopicstatus
        '''
        result = self._values.get("sns_topic_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::Cluster.SubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-subnetgroupname
        '''
        result = self._values.get("subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::MemoryDB::Cluster.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def tls_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::MemoryDB::Cluster.TLSEnabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-cluster.html#cfn-memorydb-cluster-tlsenabled
        '''
        result = self._values.get("tls_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnParameterGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_memorydb.CfnParameterGroup",
):
    '''A CloudFormation ``AWS::MemoryDB::ParameterGroup``.

    :cloudformationResource: AWS::MemoryDB::ParameterGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_memorydb as memorydb
        
        # parameters is of type object
        
        cfn_parameter_group = memorydb.CfnParameterGroup(self, "MyCfnParameterGroup",
            family="family",
            parameter_group_name="parameterGroupName",
        
            # the properties below are optional
            description="description",
            parameters=parameters,
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        family: builtins.str,
        parameter_group_name: builtins.str,
        parameters: typing.Any = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::MemoryDB::ParameterGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::MemoryDB::ParameterGroup.Description``.
        :param family: ``AWS::MemoryDB::ParameterGroup.Family``.
        :param parameter_group_name: ``AWS::MemoryDB::ParameterGroup.ParameterGroupName``.
        :param parameters: ``AWS::MemoryDB::ParameterGroup.Parameters``.
        :param tags: ``AWS::MemoryDB::ParameterGroup.Tags``.
        '''
        props = CfnParameterGroupProps(
            description=description,
            family=family,
            parameter_group_name=parameter_group_name,
            parameters=parameters,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: ARN
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::ParameterGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        '''``AWS::MemoryDB::ParameterGroup.Family``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-family
        '''
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        '''``AWS::MemoryDB::ParameterGroup.ParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-parametergroupname
        '''
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @parameter_group_name.setter
    def parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        '''``AWS::MemoryDB::ParameterGroup.Parameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-parameters
        '''
        return typing.cast(typing.Any, jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Any) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MemoryDB::ParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_memorydb.CfnParameterGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "family": "family",
        "parameter_group_name": "parameterGroupName",
        "parameters": "parameters",
        "tags": "tags",
    },
)
class CfnParameterGroupProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        family: builtins.str,
        parameter_group_name: builtins.str,
        parameters: typing.Any = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::MemoryDB::ParameterGroup``.

        :param description: ``AWS::MemoryDB::ParameterGroup.Description``.
        :param family: ``AWS::MemoryDB::ParameterGroup.Family``.
        :param parameter_group_name: ``AWS::MemoryDB::ParameterGroup.ParameterGroupName``.
        :param parameters: ``AWS::MemoryDB::ParameterGroup.Parameters``.
        :param tags: ``AWS::MemoryDB::ParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_memorydb as memorydb
            
            # parameters is of type object
            
            cfn_parameter_group_props = memorydb.CfnParameterGroupProps(
                family="family",
                parameter_group_name="parameterGroupName",
            
                # the properties below are optional
                description="description",
                parameters=parameters,
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "family": family,
            "parameter_group_name": parameter_group_name,
        }
        if description is not None:
            self._values["description"] = description
        if parameters is not None:
            self._values["parameters"] = parameters
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::ParameterGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def family(self) -> builtins.str:
        '''``AWS::MemoryDB::ParameterGroup.Family``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-family
        '''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_group_name(self) -> builtins.str:
        '''``AWS::MemoryDB::ParameterGroup.ParameterGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-parametergroupname
        '''
        result = self._values.get("parameter_group_name")
        assert result is not None, "Required property 'parameter_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters(self) -> typing.Any:
        '''``AWS::MemoryDB::ParameterGroup.Parameters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-parameters
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Any, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::MemoryDB::ParameterGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-parametergroup.html#cfn-memorydb-parametergroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnParameterGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSubnetGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_memorydb.CfnSubnetGroup",
):
    '''A CloudFormation ``AWS::MemoryDB::SubnetGroup``.

    :cloudformationResource: AWS::MemoryDB::SubnetGroup
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_memorydb as memorydb
        
        cfn_subnet_group = memorydb.CfnSubnetGroup(self, "MyCfnSubnetGroup",
            subnet_group_name="subnetGroupName",
            subnet_ids=["subnetIds"],
        
            # the properties below are optional
            description="description",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        subnet_group_name: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::MemoryDB::SubnetGroup``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::MemoryDB::SubnetGroup.Description``.
        :param subnet_group_name: ``AWS::MemoryDB::SubnetGroup.SubnetGroupName``.
        :param subnet_ids: ``AWS::MemoryDB::SubnetGroup.SubnetIds``.
        :param tags: ``AWS::MemoryDB::SubnetGroup.Tags``.
        '''
        props = CfnSubnetGroupProps(
            description=description,
            subnet_group_name=subnet_group_name,
            subnet_ids=subnet_ids,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: ARN
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::SubnetGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> builtins.str:
        '''``AWS::MemoryDB::SubnetGroup.SubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-subnetgroupname
        '''
        return typing.cast(builtins.str, jsii.get(self, "subnetGroupName"))

    @subnet_group_name.setter
    def subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "subnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::MemoryDB::SubnetGroup.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-subnetids
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MemoryDB::SubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_memorydb.CfnSubnetGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "subnet_group_name": "subnetGroupName",
        "subnet_ids": "subnetIds",
        "tags": "tags",
    },
)
class CfnSubnetGroupProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        subnet_group_name: builtins.str,
        subnet_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::MemoryDB::SubnetGroup``.

        :param description: ``AWS::MemoryDB::SubnetGroup.Description``.
        :param subnet_group_name: ``AWS::MemoryDB::SubnetGroup.SubnetGroupName``.
        :param subnet_ids: ``AWS::MemoryDB::SubnetGroup.SubnetIds``.
        :param tags: ``AWS::MemoryDB::SubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_memorydb as memorydb
            
            cfn_subnet_group_props = memorydb.CfnSubnetGroupProps(
                subnet_group_name="subnetGroupName",
                subnet_ids=["subnetIds"],
            
                # the properties below are optional
                description="description",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "subnet_group_name": subnet_group_name,
            "subnet_ids": subnet_ids,
        }
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::MemoryDB::SubnetGroup.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_group_name(self) -> builtins.str:
        '''``AWS::MemoryDB::SubnetGroup.SubnetGroupName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-subnetgroupname
        '''
        result = self._values.get("subnet_group_name")
        assert result is not None, "Required property 'subnet_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''``AWS::MemoryDB::SubnetGroup.SubnetIds``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-subnetids
        '''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::MemoryDB::SubnetGroup.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-subnetgroup.html#cfn-memorydb-subnetgroup-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSubnetGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnUser(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_memorydb.CfnUser",
):
    '''A CloudFormation ``AWS::MemoryDB::User``.

    :cloudformationResource: AWS::MemoryDB::User
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_memorydb as memorydb
        
        # authentication_mode is of type object
        
        cfn_user = memorydb.CfnUser(self, "MyCfnUser",
            access_string="accessString",
            authentication_mode=authentication_mode,
            user_name="userName",
        
            # the properties below are optional
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_string: builtins.str,
        authentication_mode: typing.Any,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        user_name: builtins.str,
    ) -> None:
        '''Create a new ``AWS::MemoryDB::User``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param access_string: ``AWS::MemoryDB::User.AccessString``.
        :param authentication_mode: ``AWS::MemoryDB::User.AuthenticationMode``.
        :param tags: ``AWS::MemoryDB::User.Tags``.
        :param user_name: ``AWS::MemoryDB::User.UserName``.
        '''
        props = CfnUserProps(
            access_string=access_string,
            authentication_mode=authentication_mode,
            tags=tags,
            user_name=user_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_488e0dd5) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessString")
    def access_string(self) -> builtins.str:
        '''``AWS::MemoryDB::User.AccessString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-accessstring
        '''
        return typing.cast(builtins.str, jsii.get(self, "accessString"))

    @access_string.setter
    def access_string(self, value: builtins.str) -> None:
        jsii.set(self, "accessString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrStatus")
    def attr_status(self) -> builtins.str:
        '''
        :cloudformationAttribute: Status
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationMode")
    def authentication_mode(self) -> typing.Any:
        '''``AWS::MemoryDB::User.AuthenticationMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-authenticationmode
        '''
        return typing.cast(typing.Any, jsii.get(self, "authenticationMode"))

    @authentication_mode.setter
    def authentication_mode(self, value: typing.Any) -> None:
        jsii.set(self, "authenticationMode", value)

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::MemoryDB::User.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        '''``AWS::MemoryDB::User.UserName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-username
        '''
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_memorydb.CfnUserProps",
    jsii_struct_bases=[],
    name_mapping={
        "access_string": "accessString",
        "authentication_mode": "authenticationMode",
        "tags": "tags",
        "user_name": "userName",
    },
)
class CfnUserProps:
    def __init__(
        self,
        *,
        access_string: builtins.str,
        authentication_mode: typing.Any,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        user_name: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::MemoryDB::User``.

        :param access_string: ``AWS::MemoryDB::User.AccessString``.
        :param authentication_mode: ``AWS::MemoryDB::User.AuthenticationMode``.
        :param tags: ``AWS::MemoryDB::User.Tags``.
        :param user_name: ``AWS::MemoryDB::User.UserName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_memorydb as memorydb
            
            # authentication_mode is of type object
            
            cfn_user_props = memorydb.CfnUserProps(
                access_string="accessString",
                authentication_mode=authentication_mode,
                user_name="userName",
            
                # the properties below are optional
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "access_string": access_string,
            "authentication_mode": authentication_mode,
            "user_name": user_name,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def access_string(self) -> builtins.str:
        '''``AWS::MemoryDB::User.AccessString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-accessstring
        '''
        result = self._values.get("access_string")
        assert result is not None, "Required property 'access_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_mode(self) -> typing.Any:
        '''``AWS::MemoryDB::User.AuthenticationMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-authenticationmode
        '''
        result = self._values.get("authentication_mode")
        assert result is not None, "Required property 'authentication_mode' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::MemoryDB::User.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''``AWS::MemoryDB::User.UserName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-memorydb-user.html#cfn-memorydb-user-username
        '''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnACL",
    "CfnACLProps",
    "CfnCluster",
    "CfnClusterProps",
    "CfnParameterGroup",
    "CfnParameterGroupProps",
    "CfnSubnetGroup",
    "CfnSubnetGroupProps",
    "CfnUser",
    "CfnUserProps",
]

publication.publish()
