'''
# AWS::Greengrass Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_greengrass as aws_greengrass
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
    IInspectable as _IInspectable_c2943556,
    IResolvable as _IResolvable_da3f097b,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)


@jsii.implements(_IInspectable_c2943556)
class CfnConnectorDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::ConnectorDefinition``.

    :cloudformationResource: AWS::Greengrass::ConnectorDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # parameters is of type object
        # tags is of type object
        
        cfn_connector_definition = greengrass.CfnConnectorDefinition(self, "MyCfnConnectorDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty(
                connectors=[greengrass.CfnConnectorDefinition.ConnectorProperty(
                    connector_arn="connectorArn",
                    id="id",
        
                    # the properties below are optional
                    parameters=parameters
                )]
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnConnectorDefinition.ConnectorDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::ConnectorDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::ConnectorDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::ConnectorDefinition.Name``.
        :param tags: ``AWS::Greengrass::ConnectorDefinition.Tags``.
        '''
        props = CfnConnectorDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnConnectorDefinition.ConnectorDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnConnectorDefinition.ConnectorDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnConnectorDefinition.ConnectorDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::ConnectorDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::ConnectorDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"connectors": "connectors"},
    )
    class ConnectorDefinitionVersionProperty:
        def __init__(
            self,
            *,
            connectors: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnConnectorDefinition.ConnectorProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param connectors: ``CfnConnectorDefinition.ConnectorDefinitionVersionProperty.Connectors``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # parameters is of type object
                
                connector_definition_version_property = greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty(
                    connectors=[greengrass.CfnConnectorDefinition.ConnectorProperty(
                        connector_arn="connectorArn",
                        id="id",
                
                        # the properties below are optional
                        parameters=parameters
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "connectors": connectors,
            }

        @builtins.property
        def connectors(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnConnectorDefinition.ConnectorProperty", _IResolvable_da3f097b]]]:
            '''``CfnConnectorDefinition.ConnectorDefinitionVersionProperty.Connectors``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connectordefinitionversion.html#cfn-greengrass-connectordefinition-connectordefinitionversion-connectors
            '''
            result = self._values.get("connectors")
            assert result is not None, "Required property 'connectors' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnConnectorDefinition.ConnectorProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConnectorDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinition.ConnectorProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connector_arn": "connectorArn",
            "id": "id",
            "parameters": "parameters",
        },
    )
    class ConnectorProperty:
        def __init__(
            self,
            *,
            connector_arn: builtins.str,
            id: builtins.str,
            parameters: typing.Any = None,
        ) -> None:
            '''
            :param connector_arn: ``CfnConnectorDefinition.ConnectorProperty.ConnectorArn``.
            :param id: ``CfnConnectorDefinition.ConnectorProperty.Id``.
            :param parameters: ``CfnConnectorDefinition.ConnectorProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # parameters is of type object
                
                connector_property = greengrass.CfnConnectorDefinition.ConnectorProperty(
                    connector_arn="connectorArn",
                    id="id",
                
                    # the properties below are optional
                    parameters=parameters
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "connector_arn": connector_arn,
                "id": id,
            }
            if parameters is not None:
                self._values["parameters"] = parameters

        @builtins.property
        def connector_arn(self) -> builtins.str:
            '''``CfnConnectorDefinition.ConnectorProperty.ConnectorArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-connectorarn
            '''
            result = self._values.get("connector_arn")
            assert result is not None, "Required property 'connector_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnConnectorDefinition.ConnectorProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnConnectorDefinition.ConnectorProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinition-connector.html#cfn-greengrass-connectordefinition-connector-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConnectorProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnConnectorDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnConnectorDefinition.ConnectorDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::ConnectorDefinition``.

        :param initial_version: ``AWS::Greengrass::ConnectorDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::ConnectorDefinition.Name``.
        :param tags: ``AWS::Greengrass::ConnectorDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # parameters is of type object
            # tags is of type object
            
            cfn_connector_definition_props = greengrass.CfnConnectorDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnConnectorDefinition.ConnectorDefinitionVersionProperty(
                    connectors=[greengrass.CfnConnectorDefinition.ConnectorProperty(
                        connector_arn="connectorArn",
                        id="id",
            
                        # the properties below are optional
                        parameters=parameters
                    )]
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnConnectorDefinition.ConnectorDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::ConnectorDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnConnectorDefinition.ConnectorDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::ConnectorDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::ConnectorDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinition.html#cfn-greengrass-connectordefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConnectorDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnConnectorDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::ConnectorDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::ConnectorDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # parameters is of type object
        
        cfn_connector_definition_version = greengrass.CfnConnectorDefinitionVersion(self, "MyCfnConnectorDefinitionVersion",
            connector_definition_id="connectorDefinitionId",
            connectors=[greengrass.CfnConnectorDefinitionVersion.ConnectorProperty(
                connector_arn="connectorArn",
                id="id",
        
                # the properties below are optional
                parameters=parameters
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        connector_definition_id: builtins.str,
        connectors: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnConnectorDefinitionVersion.ConnectorProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::ConnectorDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param connector_definition_id: ``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.
        :param connectors: ``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.
        '''
        props = CfnConnectorDefinitionVersionProps(
            connector_definition_id=connector_definition_id, connectors=connectors
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
    @jsii.member(jsii_name="connectorDefinitionId")
    def connector_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "connectorDefinitionId"))

    @connector_definition_id.setter
    def connector_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "connectorDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectors")
    def connectors(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnConnectorDefinitionVersion.ConnectorProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnConnectorDefinitionVersion.ConnectorProperty", _IResolvable_da3f097b]]], jsii.get(self, "connectors"))

    @connectors.setter
    def connectors(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnConnectorDefinitionVersion.ConnectorProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "connectors", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinitionVersion.ConnectorProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connector_arn": "connectorArn",
            "id": "id",
            "parameters": "parameters",
        },
    )
    class ConnectorProperty:
        def __init__(
            self,
            *,
            connector_arn: builtins.str,
            id: builtins.str,
            parameters: typing.Any = None,
        ) -> None:
            '''
            :param connector_arn: ``CfnConnectorDefinitionVersion.ConnectorProperty.ConnectorArn``.
            :param id: ``CfnConnectorDefinitionVersion.ConnectorProperty.Id``.
            :param parameters: ``CfnConnectorDefinitionVersion.ConnectorProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # parameters is of type object
                
                connector_property = greengrass.CfnConnectorDefinitionVersion.ConnectorProperty(
                    connector_arn="connectorArn",
                    id="id",
                
                    # the properties below are optional
                    parameters=parameters
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "connector_arn": connector_arn,
                "id": id,
            }
            if parameters is not None:
                self._values["parameters"] = parameters

        @builtins.property
        def connector_arn(self) -> builtins.str:
            '''``CfnConnectorDefinitionVersion.ConnectorProperty.ConnectorArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-connectorarn
            '''
            result = self._values.get("connector_arn")
            assert result is not None, "Required property 'connector_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnConnectorDefinitionVersion.ConnectorProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def parameters(self) -> typing.Any:
            '''``CfnConnectorDefinitionVersion.ConnectorProperty.Parameters``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-connectordefinitionversion-connector.html#cfn-greengrass-connectordefinitionversion-connector-parameters
            '''
            result = self._values.get("parameters")
            return typing.cast(typing.Any, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConnectorProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnConnectorDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={
        "connector_definition_id": "connectorDefinitionId",
        "connectors": "connectors",
    },
)
class CfnConnectorDefinitionVersionProps:
    def __init__(
        self,
        *,
        connector_definition_id: builtins.str,
        connectors: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnConnectorDefinitionVersion.ConnectorProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::ConnectorDefinitionVersion``.

        :param connector_definition_id: ``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.
        :param connectors: ``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # parameters is of type object
            
            cfn_connector_definition_version_props = greengrass.CfnConnectorDefinitionVersionProps(
                connector_definition_id="connectorDefinitionId",
                connectors=[greengrass.CfnConnectorDefinitionVersion.ConnectorProperty(
                    connector_arn="connectorArn",
                    id="id",
            
                    # the properties below are optional
                    parameters=parameters
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "connector_definition_id": connector_definition_id,
            "connectors": connectors,
        }

    @builtins.property
    def connector_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::ConnectorDefinitionVersion.ConnectorDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectordefinitionid
        '''
        result = self._values.get("connector_definition_id")
        assert result is not None, "Required property 'connector_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connectors(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnConnectorDefinitionVersion.ConnectorProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::ConnectorDefinitionVersion.Connectors``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-connectordefinitionversion.html#cfn-greengrass-connectordefinitionversion-connectors
        '''
        result = self._values.get("connectors")
        assert result is not None, "Required property 'connectors' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnConnectorDefinitionVersion.ConnectorProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConnectorDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCoreDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::CoreDefinition``.

    :cloudformationResource: AWS::Greengrass::CoreDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        
        cfn_core_definition = greengrass.CfnCoreDefinition(self, "MyCfnCoreDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty(
                cores=[greengrass.CfnCoreDefinition.CoreProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
        
                    # the properties below are optional
                    sync_shadow=False
                )]
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnCoreDefinition.CoreDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::CoreDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::CoreDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::CoreDefinition.Name``.
        :param tags: ``AWS::Greengrass::CoreDefinition.Tags``.
        '''
        props = CfnCoreDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnCoreDefinition.CoreDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::CoreDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCoreDefinition.CoreDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnCoreDefinition.CoreDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::CoreDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::CoreDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"cores": "cores"},
    )
    class CoreDefinitionVersionProperty:
        def __init__(
            self,
            *,
            cores: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCoreDefinition.CoreProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param cores: ``CfnCoreDefinition.CoreDefinitionVersionProperty.Cores``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                core_definition_version_property = greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty(
                    cores=[greengrass.CfnCoreDefinition.CoreProperty(
                        certificate_arn="certificateArn",
                        id="id",
                        thing_arn="thingArn",
                
                        # the properties below are optional
                        sync_shadow=False
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "cores": cores,
            }

        @builtins.property
        def cores(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCoreDefinition.CoreProperty", _IResolvable_da3f097b]]]:
            '''``CfnCoreDefinition.CoreDefinitionVersionProperty.Cores``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-coredefinitionversion.html#cfn-greengrass-coredefinition-coredefinitionversion-cores
            '''
            result = self._values.get("cores")
            assert result is not None, "Required property 'cores' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCoreDefinition.CoreProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CoreDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinition.CoreProperty",
        jsii_struct_bases=[],
        name_mapping={
            "certificate_arn": "certificateArn",
            "id": "id",
            "sync_shadow": "syncShadow",
            "thing_arn": "thingArn",
        },
    )
    class CoreProperty:
        def __init__(
            self,
            *,
            certificate_arn: builtins.str,
            id: builtins.str,
            sync_shadow: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            thing_arn: builtins.str,
        ) -> None:
            '''
            :param certificate_arn: ``CfnCoreDefinition.CoreProperty.CertificateArn``.
            :param id: ``CfnCoreDefinition.CoreProperty.Id``.
            :param sync_shadow: ``CfnCoreDefinition.CoreProperty.SyncShadow``.
            :param thing_arn: ``CfnCoreDefinition.CoreProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                core_property = greengrass.CfnCoreDefinition.CoreProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
                
                    # the properties below are optional
                    sync_shadow=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "certificate_arn": certificate_arn,
                "id": id,
                "thing_arn": thing_arn,
            }
            if sync_shadow is not None:
                self._values["sync_shadow"] = sync_shadow

        @builtins.property
        def certificate_arn(self) -> builtins.str:
            '''``CfnCoreDefinition.CoreProperty.CertificateArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-certificatearn
            '''
            result = self._values.get("certificate_arn")
            assert result is not None, "Required property 'certificate_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnCoreDefinition.CoreProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def sync_shadow(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnCoreDefinition.CoreProperty.SyncShadow``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-syncshadow
            '''
            result = self._values.get("sync_shadow")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def thing_arn(self) -> builtins.str:
            '''``CfnCoreDefinition.CoreProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinition-core.html#cfn-greengrass-coredefinition-core-thingarn
            '''
            result = self._values.get("thing_arn")
            assert result is not None, "Required property 'thing_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CoreProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnCoreDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnCoreDefinition.CoreDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::CoreDefinition``.

        :param initial_version: ``AWS::Greengrass::CoreDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::CoreDefinition.Name``.
        :param tags: ``AWS::Greengrass::CoreDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            
            cfn_core_definition_props = greengrass.CfnCoreDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnCoreDefinition.CoreDefinitionVersionProperty(
                    cores=[greengrass.CfnCoreDefinition.CoreProperty(
                        certificate_arn="certificateArn",
                        id="id",
                        thing_arn="thingArn",
            
                        # the properties below are optional
                        sync_shadow=False
                    )]
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnCoreDefinition.CoreDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::CoreDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnCoreDefinition.CoreDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::CoreDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::CoreDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinition.html#cfn-greengrass-coredefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCoreDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCoreDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::CoreDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::CoreDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        cfn_core_definition_version = greengrass.CfnCoreDefinitionVersion(self, "MyCfnCoreDefinitionVersion",
            core_definition_id="coreDefinitionId",
            cores=[greengrass.CfnCoreDefinitionVersion.CoreProperty(
                certificate_arn="certificateArn",
                id="id",
                thing_arn="thingArn",
        
                # the properties below are optional
                sync_shadow=False
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        core_definition_id: builtins.str,
        cores: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCoreDefinitionVersion.CoreProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::CoreDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param core_definition_id: ``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.
        :param cores: ``AWS::Greengrass::CoreDefinitionVersion.Cores``.
        '''
        props = CfnCoreDefinitionVersionProps(
            core_definition_id=core_definition_id, cores=cores
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
    @jsii.member(jsii_name="coreDefinitionId")
    def core_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "coreDefinitionId"))

    @core_definition_id.setter
    def core_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "coreDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cores")
    def cores(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCoreDefinitionVersion.CoreProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCoreDefinitionVersion.CoreProperty", _IResolvable_da3f097b]]], jsii.get(self, "cores"))

    @cores.setter
    def cores(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCoreDefinitionVersion.CoreProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "cores", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinitionVersion.CoreProperty",
        jsii_struct_bases=[],
        name_mapping={
            "certificate_arn": "certificateArn",
            "id": "id",
            "sync_shadow": "syncShadow",
            "thing_arn": "thingArn",
        },
    )
    class CoreProperty:
        def __init__(
            self,
            *,
            certificate_arn: builtins.str,
            id: builtins.str,
            sync_shadow: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            thing_arn: builtins.str,
        ) -> None:
            '''
            :param certificate_arn: ``CfnCoreDefinitionVersion.CoreProperty.CertificateArn``.
            :param id: ``CfnCoreDefinitionVersion.CoreProperty.Id``.
            :param sync_shadow: ``CfnCoreDefinitionVersion.CoreProperty.SyncShadow``.
            :param thing_arn: ``CfnCoreDefinitionVersion.CoreProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                core_property = greengrass.CfnCoreDefinitionVersion.CoreProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
                
                    # the properties below are optional
                    sync_shadow=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "certificate_arn": certificate_arn,
                "id": id,
                "thing_arn": thing_arn,
            }
            if sync_shadow is not None:
                self._values["sync_shadow"] = sync_shadow

        @builtins.property
        def certificate_arn(self) -> builtins.str:
            '''``CfnCoreDefinitionVersion.CoreProperty.CertificateArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-certificatearn
            '''
            result = self._values.get("certificate_arn")
            assert result is not None, "Required property 'certificate_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnCoreDefinitionVersion.CoreProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def sync_shadow(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnCoreDefinitionVersion.CoreProperty.SyncShadow``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-syncshadow
            '''
            result = self._values.get("sync_shadow")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def thing_arn(self) -> builtins.str:
            '''``CfnCoreDefinitionVersion.CoreProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-coredefinitionversion-core.html#cfn-greengrass-coredefinitionversion-core-thingarn
            '''
            result = self._values.get("thing_arn")
            assert result is not None, "Required property 'thing_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CoreProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnCoreDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={"core_definition_id": "coreDefinitionId", "cores": "cores"},
)
class CfnCoreDefinitionVersionProps:
    def __init__(
        self,
        *,
        core_definition_id: builtins.str,
        cores: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnCoreDefinitionVersion.CoreProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::CoreDefinitionVersion``.

        :param core_definition_id: ``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.
        :param cores: ``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            cfn_core_definition_version_props = greengrass.CfnCoreDefinitionVersionProps(
                core_definition_id="coreDefinitionId",
                cores=[greengrass.CfnCoreDefinitionVersion.CoreProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
            
                    # the properties below are optional
                    sync_shadow=False
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "core_definition_id": core_definition_id,
            "cores": cores,
        }

    @builtins.property
    def core_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::CoreDefinitionVersion.CoreDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-coredefinitionid
        '''
        result = self._values.get("core_definition_id")
        assert result is not None, "Required property 'core_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cores(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnCoreDefinitionVersion.CoreProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::CoreDefinitionVersion.Cores``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-coredefinitionversion.html#cfn-greengrass-coredefinitionversion-cores
        '''
        result = self._values.get("cores")
        assert result is not None, "Required property 'cores' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnCoreDefinitionVersion.CoreProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCoreDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDeviceDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::DeviceDefinition``.

    :cloudformationResource: AWS::Greengrass::DeviceDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        
        cfn_device_definition = greengrass.CfnDeviceDefinition(self, "MyCfnDeviceDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty(
                devices=[greengrass.CfnDeviceDefinition.DeviceProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
        
                    # the properties below are optional
                    sync_shadow=False
                )]
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnDeviceDefinition.DeviceDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::DeviceDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::DeviceDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::DeviceDefinition.Name``.
        :param tags: ``AWS::Greengrass::DeviceDefinition.Tags``.
        '''
        props = CfnDeviceDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnDeviceDefinition.DeviceDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnDeviceDefinition.DeviceDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnDeviceDefinition.DeviceDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::DeviceDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::DeviceDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"devices": "devices"},
    )
    class DeviceDefinitionVersionProperty:
        def __init__(
            self,
            *,
            devices: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDeviceDefinition.DeviceProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param devices: ``CfnDeviceDefinition.DeviceDefinitionVersionProperty.Devices``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                device_definition_version_property = greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty(
                    devices=[greengrass.CfnDeviceDefinition.DeviceProperty(
                        certificate_arn="certificateArn",
                        id="id",
                        thing_arn="thingArn",
                
                        # the properties below are optional
                        sync_shadow=False
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "devices": devices,
            }

        @builtins.property
        def devices(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDeviceDefinition.DeviceProperty", _IResolvable_da3f097b]]]:
            '''``CfnDeviceDefinition.DeviceDefinitionVersionProperty.Devices``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-devicedefinitionversion.html#cfn-greengrass-devicedefinition-devicedefinitionversion-devices
            '''
            result = self._values.get("devices")
            assert result is not None, "Required property 'devices' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDeviceDefinition.DeviceProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DeviceDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinition.DeviceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "certificate_arn": "certificateArn",
            "id": "id",
            "sync_shadow": "syncShadow",
            "thing_arn": "thingArn",
        },
    )
    class DeviceProperty:
        def __init__(
            self,
            *,
            certificate_arn: builtins.str,
            id: builtins.str,
            sync_shadow: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            thing_arn: builtins.str,
        ) -> None:
            '''
            :param certificate_arn: ``CfnDeviceDefinition.DeviceProperty.CertificateArn``.
            :param id: ``CfnDeviceDefinition.DeviceProperty.Id``.
            :param sync_shadow: ``CfnDeviceDefinition.DeviceProperty.SyncShadow``.
            :param thing_arn: ``CfnDeviceDefinition.DeviceProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                device_property = greengrass.CfnDeviceDefinition.DeviceProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
                
                    # the properties below are optional
                    sync_shadow=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "certificate_arn": certificate_arn,
                "id": id,
                "thing_arn": thing_arn,
            }
            if sync_shadow is not None:
                self._values["sync_shadow"] = sync_shadow

        @builtins.property
        def certificate_arn(self) -> builtins.str:
            '''``CfnDeviceDefinition.DeviceProperty.CertificateArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-certificatearn
            '''
            result = self._values.get("certificate_arn")
            assert result is not None, "Required property 'certificate_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnDeviceDefinition.DeviceProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def sync_shadow(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnDeviceDefinition.DeviceProperty.SyncShadow``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-syncshadow
            '''
            result = self._values.get("sync_shadow")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def thing_arn(self) -> builtins.str:
            '''``CfnDeviceDefinition.DeviceProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinition-device.html#cfn-greengrass-devicedefinition-device-thingarn
            '''
            result = self._values.get("thing_arn")
            assert result is not None, "Required property 'thing_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DeviceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnDeviceDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnDeviceDefinition.DeviceDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::DeviceDefinition``.

        :param initial_version: ``AWS::Greengrass::DeviceDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::DeviceDefinition.Name``.
        :param tags: ``AWS::Greengrass::DeviceDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            
            cfn_device_definition_props = greengrass.CfnDeviceDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnDeviceDefinition.DeviceDefinitionVersionProperty(
                    devices=[greengrass.CfnDeviceDefinition.DeviceProperty(
                        certificate_arn="certificateArn",
                        id="id",
                        thing_arn="thingArn",
            
                        # the properties below are optional
                        sync_shadow=False
                    )]
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnDeviceDefinition.DeviceDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::DeviceDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnDeviceDefinition.DeviceDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::DeviceDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::DeviceDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinition.html#cfn-greengrass-devicedefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDeviceDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDeviceDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::DeviceDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::DeviceDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        cfn_device_definition_version = greengrass.CfnDeviceDefinitionVersion(self, "MyCfnDeviceDefinitionVersion",
            device_definition_id="deviceDefinitionId",
            devices=[greengrass.CfnDeviceDefinitionVersion.DeviceProperty(
                certificate_arn="certificateArn",
                id="id",
                thing_arn="thingArn",
        
                # the properties below are optional
                sync_shadow=False
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        device_definition_id: builtins.str,
        devices: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDeviceDefinitionVersion.DeviceProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::DeviceDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param device_definition_id: ``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.
        :param devices: ``AWS::Greengrass::DeviceDefinitionVersion.Devices``.
        '''
        props = CfnDeviceDefinitionVersionProps(
            device_definition_id=device_definition_id, devices=devices
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
    @jsii.member(jsii_name="deviceDefinitionId")
    def device_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "deviceDefinitionId"))

    @device_definition_id.setter
    def device_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "deviceDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="devices")
    def devices(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDeviceDefinitionVersion.DeviceProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDeviceDefinitionVersion.DeviceProperty", _IResolvable_da3f097b]]], jsii.get(self, "devices"))

    @devices.setter
    def devices(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDeviceDefinitionVersion.DeviceProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "devices", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinitionVersion.DeviceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "certificate_arn": "certificateArn",
            "id": "id",
            "sync_shadow": "syncShadow",
            "thing_arn": "thingArn",
        },
    )
    class DeviceProperty:
        def __init__(
            self,
            *,
            certificate_arn: builtins.str,
            id: builtins.str,
            sync_shadow: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            thing_arn: builtins.str,
        ) -> None:
            '''
            :param certificate_arn: ``CfnDeviceDefinitionVersion.DeviceProperty.CertificateArn``.
            :param id: ``CfnDeviceDefinitionVersion.DeviceProperty.Id``.
            :param sync_shadow: ``CfnDeviceDefinitionVersion.DeviceProperty.SyncShadow``.
            :param thing_arn: ``CfnDeviceDefinitionVersion.DeviceProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                device_property = greengrass.CfnDeviceDefinitionVersion.DeviceProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
                
                    # the properties below are optional
                    sync_shadow=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "certificate_arn": certificate_arn,
                "id": id,
                "thing_arn": thing_arn,
            }
            if sync_shadow is not None:
                self._values["sync_shadow"] = sync_shadow

        @builtins.property
        def certificate_arn(self) -> builtins.str:
            '''``CfnDeviceDefinitionVersion.DeviceProperty.CertificateArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-certificatearn
            '''
            result = self._values.get("certificate_arn")
            assert result is not None, "Required property 'certificate_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnDeviceDefinitionVersion.DeviceProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def sync_shadow(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnDeviceDefinitionVersion.DeviceProperty.SyncShadow``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-syncshadow
            '''
            result = self._values.get("sync_shadow")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def thing_arn(self) -> builtins.str:
            '''``CfnDeviceDefinitionVersion.DeviceProperty.ThingArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-devicedefinitionversion-device.html#cfn-greengrass-devicedefinitionversion-device-thingarn
            '''
            result = self._values.get("thing_arn")
            assert result is not None, "Required property 'thing_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DeviceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnDeviceDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={"device_definition_id": "deviceDefinitionId", "devices": "devices"},
)
class CfnDeviceDefinitionVersionProps:
    def __init__(
        self,
        *,
        device_definition_id: builtins.str,
        devices: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnDeviceDefinitionVersion.DeviceProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::DeviceDefinitionVersion``.

        :param device_definition_id: ``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.
        :param devices: ``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            cfn_device_definition_version_props = greengrass.CfnDeviceDefinitionVersionProps(
                device_definition_id="deviceDefinitionId",
                devices=[greengrass.CfnDeviceDefinitionVersion.DeviceProperty(
                    certificate_arn="certificateArn",
                    id="id",
                    thing_arn="thingArn",
            
                    # the properties below are optional
                    sync_shadow=False
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "device_definition_id": device_definition_id,
            "devices": devices,
        }

    @builtins.property
    def device_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::DeviceDefinitionVersion.DeviceDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devicedefinitionid
        '''
        result = self._values.get("device_definition_id")
        assert result is not None, "Required property 'device_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def devices(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnDeviceDefinitionVersion.DeviceProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::DeviceDefinitionVersion.Devices``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-devicedefinitionversion.html#cfn-greengrass-devicedefinitionversion-devices
        '''
        result = self._values.get("devices")
        assert result is not None, "Required property 'devices' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnDeviceDefinitionVersion.DeviceProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDeviceDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnFunctionDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::FunctionDefinition``.

    :cloudformationResource: AWS::Greengrass::FunctionDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        # variables is of type object
        
        cfn_function_definition = greengrass.CfnFunctionDefinition(self, "MyCfnFunctionDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty(
                functions=[greengrass.CfnFunctionDefinition.FunctionProperty(
                    function_arn="functionArn",
                    function_configuration=greengrass.CfnFunctionDefinition.FunctionConfigurationProperty(
                        encoding_type="encodingType",
                        environment=greengrass.CfnFunctionDefinition.EnvironmentProperty(
                            access_sysfs=False,
                            execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                                isolation_mode="isolationMode",
                                run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                    gid=123,
                                    uid=123
                                )
                            ),
                            resource_access_policies=[greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                                resource_id="resourceId",
        
                                # the properties below are optional
                                permission="permission"
                            )],
                            variables=variables
                        ),
                        exec_args="execArgs",
                        executable="executable",
                        memory_size=123,
                        pinned=False,
                        timeout=123
                    ),
                    id="id"
                )],
        
                # the properties below are optional
                default_config=greengrass.CfnFunctionDefinition.DefaultConfigProperty(
                    execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                        isolation_mode="isolationMode",
                        run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                            gid=123,
                            uid=123
                        )
                    )
                )
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnFunctionDefinition.FunctionDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::FunctionDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::FunctionDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::FunctionDefinition.Name``.
        :param tags: ``AWS::Greengrass::FunctionDefinition.Tags``.
        '''
        props = CfnFunctionDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnFunctionDefinition.FunctionDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinition.FunctionDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnFunctionDefinition.FunctionDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::FunctionDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::FunctionDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.DefaultConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"execution": "execution"},
    )
    class DefaultConfigProperty:
        def __init__(
            self,
            *,
            execution: typing.Union["CfnFunctionDefinition.ExecutionProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param execution: ``CfnFunctionDefinition.DefaultConfigProperty.Execution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                default_config_property = greengrass.CfnFunctionDefinition.DefaultConfigProperty(
                    execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                        isolation_mode="isolationMode",
                        run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                            gid=123,
                            uid=123
                        )
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "execution": execution,
            }

        @builtins.property
        def execution(
            self,
        ) -> typing.Union["CfnFunctionDefinition.ExecutionProperty", _IResolvable_da3f097b]:
            '''``CfnFunctionDefinition.DefaultConfigProperty.Execution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-defaultconfig.html#cfn-greengrass-functiondefinition-defaultconfig-execution
            '''
            result = self._values.get("execution")
            assert result is not None, "Required property 'execution' is missing"
            return typing.cast(typing.Union["CfnFunctionDefinition.ExecutionProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DefaultConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.EnvironmentProperty",
        jsii_struct_bases=[],
        name_mapping={
            "access_sysfs": "accessSysfs",
            "execution": "execution",
            "resource_access_policies": "resourceAccessPolicies",
            "variables": "variables",
        },
    )
    class EnvironmentProperty:
        def __init__(
            self,
            *,
            access_sysfs: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            execution: typing.Optional[typing.Union["CfnFunctionDefinition.ExecutionProperty", _IResolvable_da3f097b]] = None,
            resource_access_policies: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnFunctionDefinition.ResourceAccessPolicyProperty", _IResolvable_da3f097b]]]] = None,
            variables: typing.Any = None,
        ) -> None:
            '''
            :param access_sysfs: ``CfnFunctionDefinition.EnvironmentProperty.AccessSysfs``.
            :param execution: ``CfnFunctionDefinition.EnvironmentProperty.Execution``.
            :param resource_access_policies: ``CfnFunctionDefinition.EnvironmentProperty.ResourceAccessPolicies``.
            :param variables: ``CfnFunctionDefinition.EnvironmentProperty.Variables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                environment_property = greengrass.CfnFunctionDefinition.EnvironmentProperty(
                    access_sysfs=False,
                    execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                        isolation_mode="isolationMode",
                        run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                            gid=123,
                            uid=123
                        )
                    ),
                    resource_access_policies=[greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                        resource_id="resourceId",
                
                        # the properties below are optional
                        permission="permission"
                    )],
                    variables=variables
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if access_sysfs is not None:
                self._values["access_sysfs"] = access_sysfs
            if execution is not None:
                self._values["execution"] = execution
            if resource_access_policies is not None:
                self._values["resource_access_policies"] = resource_access_policies
            if variables is not None:
                self._values["variables"] = variables

        @builtins.property
        def access_sysfs(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinition.EnvironmentProperty.AccessSysfs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-accesssysfs
            '''
            result = self._values.get("access_sysfs")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def execution(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinition.ExecutionProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinition.EnvironmentProperty.Execution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-execution
            '''
            result = self._values.get("execution")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinition.ExecutionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def resource_access_policies(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinition.ResourceAccessPolicyProperty", _IResolvable_da3f097b]]]]:
            '''``CfnFunctionDefinition.EnvironmentProperty.ResourceAccessPolicies``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-resourceaccesspolicies
            '''
            result = self._values.get("resource_access_policies")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinition.ResourceAccessPolicyProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def variables(self) -> typing.Any:
            '''``CfnFunctionDefinition.EnvironmentProperty.Variables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-environment.html#cfn-greengrass-functiondefinition-environment-variables
            '''
            result = self._values.get("variables")
            return typing.cast(typing.Any, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.ExecutionProperty",
        jsii_struct_bases=[],
        name_mapping={"isolation_mode": "isolationMode", "run_as": "runAs"},
    )
    class ExecutionProperty:
        def __init__(
            self,
            *,
            isolation_mode: typing.Optional[builtins.str] = None,
            run_as: typing.Optional[typing.Union["CfnFunctionDefinition.RunAsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param isolation_mode: ``CfnFunctionDefinition.ExecutionProperty.IsolationMode``.
            :param run_as: ``CfnFunctionDefinition.ExecutionProperty.RunAs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                execution_property = greengrass.CfnFunctionDefinition.ExecutionProperty(
                    isolation_mode="isolationMode",
                    run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                        gid=123,
                        uid=123
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if isolation_mode is not None:
                self._values["isolation_mode"] = isolation_mode
            if run_as is not None:
                self._values["run_as"] = run_as

        @builtins.property
        def isolation_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinition.ExecutionProperty.IsolationMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-isolationmode
            '''
            result = self._values.get("isolation_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def run_as(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinition.RunAsProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinition.ExecutionProperty.RunAs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-execution.html#cfn-greengrass-functiondefinition-execution-runas
            '''
            result = self._values.get("run_as")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinition.RunAsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ExecutionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.FunctionConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "encoding_type": "encodingType",
            "environment": "environment",
            "exec_args": "execArgs",
            "executable": "executable",
            "memory_size": "memorySize",
            "pinned": "pinned",
            "timeout": "timeout",
        },
    )
    class FunctionConfigurationProperty:
        def __init__(
            self,
            *,
            encoding_type: typing.Optional[builtins.str] = None,
            environment: typing.Optional[typing.Union["CfnFunctionDefinition.EnvironmentProperty", _IResolvable_da3f097b]] = None,
            exec_args: typing.Optional[builtins.str] = None,
            executable: typing.Optional[builtins.str] = None,
            memory_size: typing.Optional[jsii.Number] = None,
            pinned: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            timeout: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param encoding_type: ``CfnFunctionDefinition.FunctionConfigurationProperty.EncodingType``.
            :param environment: ``CfnFunctionDefinition.FunctionConfigurationProperty.Environment``.
            :param exec_args: ``CfnFunctionDefinition.FunctionConfigurationProperty.ExecArgs``.
            :param executable: ``CfnFunctionDefinition.FunctionConfigurationProperty.Executable``.
            :param memory_size: ``CfnFunctionDefinition.FunctionConfigurationProperty.MemorySize``.
            :param pinned: ``CfnFunctionDefinition.FunctionConfigurationProperty.Pinned``.
            :param timeout: ``CfnFunctionDefinition.FunctionConfigurationProperty.Timeout``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                function_configuration_property = greengrass.CfnFunctionDefinition.FunctionConfigurationProperty(
                    encoding_type="encodingType",
                    environment=greengrass.CfnFunctionDefinition.EnvironmentProperty(
                        access_sysfs=False,
                        execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                            isolation_mode="isolationMode",
                            run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                gid=123,
                                uid=123
                            )
                        ),
                        resource_access_policies=[greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                            resource_id="resourceId",
                
                            # the properties below are optional
                            permission="permission"
                        )],
                        variables=variables
                    ),
                    exec_args="execArgs",
                    executable="executable",
                    memory_size=123,
                    pinned=False,
                    timeout=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if encoding_type is not None:
                self._values["encoding_type"] = encoding_type
            if environment is not None:
                self._values["environment"] = environment
            if exec_args is not None:
                self._values["exec_args"] = exec_args
            if executable is not None:
                self._values["executable"] = executable
            if memory_size is not None:
                self._values["memory_size"] = memory_size
            if pinned is not None:
                self._values["pinned"] = pinned
            if timeout is not None:
                self._values["timeout"] = timeout

        @builtins.property
        def encoding_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.EncodingType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-encodingtype
            '''
            result = self._values.get("encoding_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def environment(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinition.EnvironmentProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.Environment``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-environment
            '''
            result = self._values.get("environment")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinition.EnvironmentProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def exec_args(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.ExecArgs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-execargs
            '''
            result = self._values.get("exec_args")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def executable(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.Executable``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-executable
            '''
            result = self._values.get("executable")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def memory_size(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.MemorySize``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-memorysize
            '''
            result = self._values.get("memory_size")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def pinned(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.Pinned``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-pinned
            '''
            result = self._values.get("pinned")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def timeout(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinition.FunctionConfigurationProperty.Timeout``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functionconfiguration.html#cfn-greengrass-functiondefinition-functionconfiguration-timeout
            '''
            result = self._values.get("timeout")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FunctionConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"default_config": "defaultConfig", "functions": "functions"},
    )
    class FunctionDefinitionVersionProperty:
        def __init__(
            self,
            *,
            default_config: typing.Optional[typing.Union["CfnFunctionDefinition.DefaultConfigProperty", _IResolvable_da3f097b]] = None,
            functions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnFunctionDefinition.FunctionProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param default_config: ``CfnFunctionDefinition.FunctionDefinitionVersionProperty.DefaultConfig``.
            :param functions: ``CfnFunctionDefinition.FunctionDefinitionVersionProperty.Functions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                function_definition_version_property = greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty(
                    functions=[greengrass.CfnFunctionDefinition.FunctionProperty(
                        function_arn="functionArn",
                        function_configuration=greengrass.CfnFunctionDefinition.FunctionConfigurationProperty(
                            encoding_type="encodingType",
                            environment=greengrass.CfnFunctionDefinition.EnvironmentProperty(
                                access_sysfs=False,
                                execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                                    isolation_mode="isolationMode",
                                    run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                        gid=123,
                                        uid=123
                                    )
                                ),
                                resource_access_policies=[greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                                    resource_id="resourceId",
                
                                    # the properties below are optional
                                    permission="permission"
                                )],
                                variables=variables
                            ),
                            exec_args="execArgs",
                            executable="executable",
                            memory_size=123,
                            pinned=False,
                            timeout=123
                        ),
                        id="id"
                    )],
                
                    # the properties below are optional
                    default_config=greengrass.CfnFunctionDefinition.DefaultConfigProperty(
                        execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                            isolation_mode="isolationMode",
                            run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                gid=123,
                                uid=123
                            )
                        )
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "functions": functions,
            }
            if default_config is not None:
                self._values["default_config"] = default_config

        @builtins.property
        def default_config(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinition.DefaultConfigProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinition.FunctionDefinitionVersionProperty.DefaultConfig``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-defaultconfig
            '''
            result = self._values.get("default_config")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinition.DefaultConfigProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def functions(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinition.FunctionProperty", _IResolvable_da3f097b]]]:
            '''``CfnFunctionDefinition.FunctionDefinitionVersionProperty.Functions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-functiondefinitionversion.html#cfn-greengrass-functiondefinition-functiondefinitionversion-functions
            '''
            result = self._values.get("functions")
            assert result is not None, "Required property 'functions' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinition.FunctionProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FunctionDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.FunctionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "function_arn": "functionArn",
            "function_configuration": "functionConfiguration",
            "id": "id",
        },
    )
    class FunctionProperty:
        def __init__(
            self,
            *,
            function_arn: builtins.str,
            function_configuration: typing.Union["CfnFunctionDefinition.FunctionConfigurationProperty", _IResolvable_da3f097b],
            id: builtins.str,
        ) -> None:
            '''
            :param function_arn: ``CfnFunctionDefinition.FunctionProperty.FunctionArn``.
            :param function_configuration: ``CfnFunctionDefinition.FunctionProperty.FunctionConfiguration``.
            :param id: ``CfnFunctionDefinition.FunctionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                function_property = greengrass.CfnFunctionDefinition.FunctionProperty(
                    function_arn="functionArn",
                    function_configuration=greengrass.CfnFunctionDefinition.FunctionConfigurationProperty(
                        encoding_type="encodingType",
                        environment=greengrass.CfnFunctionDefinition.EnvironmentProperty(
                            access_sysfs=False,
                            execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                                isolation_mode="isolationMode",
                                run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                    gid=123,
                                    uid=123
                                )
                            ),
                            resource_access_policies=[greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                                resource_id="resourceId",
                
                                # the properties below are optional
                                permission="permission"
                            )],
                            variables=variables
                        ),
                        exec_args="execArgs",
                        executable="executable",
                        memory_size=123,
                        pinned=False,
                        timeout=123
                    ),
                    id="id"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "function_arn": function_arn,
                "function_configuration": function_configuration,
                "id": id,
            }

        @builtins.property
        def function_arn(self) -> builtins.str:
            '''``CfnFunctionDefinition.FunctionProperty.FunctionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionarn
            '''
            result = self._values.get("function_arn")
            assert result is not None, "Required property 'function_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def function_configuration(
            self,
        ) -> typing.Union["CfnFunctionDefinition.FunctionConfigurationProperty", _IResolvable_da3f097b]:
            '''``CfnFunctionDefinition.FunctionProperty.FunctionConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-functionconfiguration
            '''
            result = self._values.get("function_configuration")
            assert result is not None, "Required property 'function_configuration' is missing"
            return typing.cast(typing.Union["CfnFunctionDefinition.FunctionConfigurationProperty", _IResolvable_da3f097b], result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnFunctionDefinition.FunctionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-function.html#cfn-greengrass-functiondefinition-function-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FunctionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty",
        jsii_struct_bases=[],
        name_mapping={"permission": "permission", "resource_id": "resourceId"},
    )
    class ResourceAccessPolicyProperty:
        def __init__(
            self,
            *,
            permission: typing.Optional[builtins.str] = None,
            resource_id: builtins.str,
        ) -> None:
            '''
            :param permission: ``CfnFunctionDefinition.ResourceAccessPolicyProperty.Permission``.
            :param resource_id: ``CfnFunctionDefinition.ResourceAccessPolicyProperty.ResourceId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_access_policy_property = greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                    resource_id="resourceId",
                
                    # the properties below are optional
                    permission="permission"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "resource_id": resource_id,
            }
            if permission is not None:
                self._values["permission"] = permission

        @builtins.property
        def permission(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinition.ResourceAccessPolicyProperty.Permission``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-permission
            '''
            result = self._values.get("permission")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def resource_id(self) -> builtins.str:
            '''``CfnFunctionDefinition.ResourceAccessPolicyProperty.ResourceId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-resourceaccesspolicy.html#cfn-greengrass-functiondefinition-resourceaccesspolicy-resourceid
            '''
            result = self._values.get("resource_id")
            assert result is not None, "Required property 'resource_id' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceAccessPolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinition.RunAsProperty",
        jsii_struct_bases=[],
        name_mapping={"gid": "gid", "uid": "uid"},
    )
    class RunAsProperty:
        def __init__(
            self,
            *,
            gid: typing.Optional[jsii.Number] = None,
            uid: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param gid: ``CfnFunctionDefinition.RunAsProperty.Gid``.
            :param uid: ``CfnFunctionDefinition.RunAsProperty.Uid``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                run_as_property = greengrass.CfnFunctionDefinition.RunAsProperty(
                    gid=123,
                    uid=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if gid is not None:
                self._values["gid"] = gid
            if uid is not None:
                self._values["uid"] = uid

        @builtins.property
        def gid(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinition.RunAsProperty.Gid``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-gid
            '''
            result = self._values.get("gid")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def uid(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinition.RunAsProperty.Uid``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinition-runas.html#cfn-greengrass-functiondefinition-runas-uid
            '''
            result = self._values.get("uid")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RunAsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnFunctionDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnFunctionDefinition.FunctionDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::FunctionDefinition``.

        :param initial_version: ``AWS::Greengrass::FunctionDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::FunctionDefinition.Name``.
        :param tags: ``AWS::Greengrass::FunctionDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            # variables is of type object
            
            cfn_function_definition_props = greengrass.CfnFunctionDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnFunctionDefinition.FunctionDefinitionVersionProperty(
                    functions=[greengrass.CfnFunctionDefinition.FunctionProperty(
                        function_arn="functionArn",
                        function_configuration=greengrass.CfnFunctionDefinition.FunctionConfigurationProperty(
                            encoding_type="encodingType",
                            environment=greengrass.CfnFunctionDefinition.EnvironmentProperty(
                                access_sysfs=False,
                                execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                                    isolation_mode="isolationMode",
                                    run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                        gid=123,
                                        uid=123
                                    )
                                ),
                                resource_access_policies=[greengrass.CfnFunctionDefinition.ResourceAccessPolicyProperty(
                                    resource_id="resourceId",
            
                                    # the properties below are optional
                                    permission="permission"
                                )],
                                variables=variables
                            ),
                            exec_args="execArgs",
                            executable="executable",
                            memory_size=123,
                            pinned=False,
                            timeout=123
                        ),
                        id="id"
                    )],
            
                    # the properties below are optional
                    default_config=greengrass.CfnFunctionDefinition.DefaultConfigProperty(
                        execution=greengrass.CfnFunctionDefinition.ExecutionProperty(
                            isolation_mode="isolationMode",
                            run_as=greengrass.CfnFunctionDefinition.RunAsProperty(
                                gid=123,
                                uid=123
                            )
                        )
                    )
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnFunctionDefinition.FunctionDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::FunctionDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnFunctionDefinition.FunctionDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::FunctionDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::FunctionDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinition.html#cfn-greengrass-functiondefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFunctionDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnFunctionDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::FunctionDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::FunctionDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # variables is of type object
        
        cfn_function_definition_version = greengrass.CfnFunctionDefinitionVersion(self, "MyCfnFunctionDefinitionVersion",
            function_definition_id="functionDefinitionId",
            functions=[greengrass.CfnFunctionDefinitionVersion.FunctionProperty(
                function_arn="functionArn",
                function_configuration=greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty(
                    encoding_type="encodingType",
                    environment=greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty(
                        access_sysfs=False,
                        execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                            isolation_mode="isolationMode",
                            run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                                gid=123,
                                uid=123
                            )
                        ),
                        resource_access_policies=[greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty(
                            resource_id="resourceId",
        
                            # the properties below are optional
                            permission="permission"
                        )],
                        variables=variables
                    ),
                    exec_args="execArgs",
                    executable="executable",
                    memory_size=123,
                    pinned=False,
                    timeout=123
                ),
                id="id"
            )],
        
            # the properties below are optional
            default_config=greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty(
                execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                    isolation_mode="isolationMode",
                    run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                        gid=123,
                        uid=123
                    )
                )
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_config: typing.Optional[typing.Union["CfnFunctionDefinitionVersion.DefaultConfigProperty", _IResolvable_da3f097b]] = None,
        function_definition_id: builtins.str,
        functions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnFunctionDefinitionVersion.FunctionProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::FunctionDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param default_config: ``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.
        :param function_definition_id: ``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.
        :param functions: ``AWS::Greengrass::FunctionDefinitionVersion.Functions``.
        '''
        props = CfnFunctionDefinitionVersionProps(
            default_config=default_config,
            function_definition_id=function_definition_id,
            functions=functions,
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
    @jsii.member(jsii_name="defaultConfig")
    def default_config(
        self,
    ) -> typing.Optional[typing.Union["CfnFunctionDefinitionVersion.DefaultConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinitionVersion.DefaultConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "defaultConfig"))

    @default_config.setter
    def default_config(
        self,
        value: typing.Optional[typing.Union["CfnFunctionDefinitionVersion.DefaultConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "defaultConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionDefinitionId")
    def function_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionDefinitionId"))

    @function_definition_id.setter
    def function_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "functionDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functions")
    def functions(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinitionVersion.FunctionProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinitionVersion.FunctionProperty", _IResolvable_da3f097b]]], jsii.get(self, "functions"))

    @functions.setter
    def functions(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinitionVersion.FunctionProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "functions", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"execution": "execution"},
    )
    class DefaultConfigProperty:
        def __init__(
            self,
            *,
            execution: typing.Union["CfnFunctionDefinitionVersion.ExecutionProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param execution: ``CfnFunctionDefinitionVersion.DefaultConfigProperty.Execution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                default_config_property = greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty(
                    execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                        isolation_mode="isolationMode",
                        run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                            gid=123,
                            uid=123
                        )
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "execution": execution,
            }

        @builtins.property
        def execution(
            self,
        ) -> typing.Union["CfnFunctionDefinitionVersion.ExecutionProperty", _IResolvable_da3f097b]:
            '''``CfnFunctionDefinitionVersion.DefaultConfigProperty.Execution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-defaultconfig.html#cfn-greengrass-functiondefinitionversion-defaultconfig-execution
            '''
            result = self._values.get("execution")
            assert result is not None, "Required property 'execution' is missing"
            return typing.cast(typing.Union["CfnFunctionDefinitionVersion.ExecutionProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DefaultConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty",
        jsii_struct_bases=[],
        name_mapping={
            "access_sysfs": "accessSysfs",
            "execution": "execution",
            "resource_access_policies": "resourceAccessPolicies",
            "variables": "variables",
        },
    )
    class EnvironmentProperty:
        def __init__(
            self,
            *,
            access_sysfs: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            execution: typing.Optional[typing.Union["CfnFunctionDefinitionVersion.ExecutionProperty", _IResolvable_da3f097b]] = None,
            resource_access_policies: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty", _IResolvable_da3f097b]]]] = None,
            variables: typing.Any = None,
        ) -> None:
            '''
            :param access_sysfs: ``CfnFunctionDefinitionVersion.EnvironmentProperty.AccessSysfs``.
            :param execution: ``CfnFunctionDefinitionVersion.EnvironmentProperty.Execution``.
            :param resource_access_policies: ``CfnFunctionDefinitionVersion.EnvironmentProperty.ResourceAccessPolicies``.
            :param variables: ``CfnFunctionDefinitionVersion.EnvironmentProperty.Variables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                environment_property = greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty(
                    access_sysfs=False,
                    execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                        isolation_mode="isolationMode",
                        run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                            gid=123,
                            uid=123
                        )
                    ),
                    resource_access_policies=[greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty(
                        resource_id="resourceId",
                
                        # the properties below are optional
                        permission="permission"
                    )],
                    variables=variables
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if access_sysfs is not None:
                self._values["access_sysfs"] = access_sysfs
            if execution is not None:
                self._values["execution"] = execution
            if resource_access_policies is not None:
                self._values["resource_access_policies"] = resource_access_policies
            if variables is not None:
                self._values["variables"] = variables

        @builtins.property
        def access_sysfs(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinitionVersion.EnvironmentProperty.AccessSysfs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-accesssysfs
            '''
            result = self._values.get("access_sysfs")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def execution(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinitionVersion.ExecutionProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinitionVersion.EnvironmentProperty.Execution``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-execution
            '''
            result = self._values.get("execution")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinitionVersion.ExecutionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def resource_access_policies(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty", _IResolvable_da3f097b]]]]:
            '''``CfnFunctionDefinitionVersion.EnvironmentProperty.ResourceAccessPolicies``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-resourceaccesspolicies
            '''
            result = self._values.get("resource_access_policies")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def variables(self) -> typing.Any:
            '''``CfnFunctionDefinitionVersion.EnvironmentProperty.Variables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-environment.html#cfn-greengrass-functiondefinitionversion-environment-variables
            '''
            result = self._values.get("variables")
            return typing.cast(typing.Any, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnvironmentProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.ExecutionProperty",
        jsii_struct_bases=[],
        name_mapping={"isolation_mode": "isolationMode", "run_as": "runAs"},
    )
    class ExecutionProperty:
        def __init__(
            self,
            *,
            isolation_mode: typing.Optional[builtins.str] = None,
            run_as: typing.Optional[typing.Union["CfnFunctionDefinitionVersion.RunAsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param isolation_mode: ``CfnFunctionDefinitionVersion.ExecutionProperty.IsolationMode``.
            :param run_as: ``CfnFunctionDefinitionVersion.ExecutionProperty.RunAs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                execution_property = greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                    isolation_mode="isolationMode",
                    run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                        gid=123,
                        uid=123
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if isolation_mode is not None:
                self._values["isolation_mode"] = isolation_mode
            if run_as is not None:
                self._values["run_as"] = run_as

        @builtins.property
        def isolation_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinitionVersion.ExecutionProperty.IsolationMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-isolationmode
            '''
            result = self._values.get("isolation_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def run_as(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinitionVersion.RunAsProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinitionVersion.ExecutionProperty.RunAs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-execution.html#cfn-greengrass-functiondefinitionversion-execution-runas
            '''
            result = self._values.get("run_as")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinitionVersion.RunAsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ExecutionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "encoding_type": "encodingType",
            "environment": "environment",
            "exec_args": "execArgs",
            "executable": "executable",
            "memory_size": "memorySize",
            "pinned": "pinned",
            "timeout": "timeout",
        },
    )
    class FunctionConfigurationProperty:
        def __init__(
            self,
            *,
            encoding_type: typing.Optional[builtins.str] = None,
            environment: typing.Optional[typing.Union["CfnFunctionDefinitionVersion.EnvironmentProperty", _IResolvable_da3f097b]] = None,
            exec_args: typing.Optional[builtins.str] = None,
            executable: typing.Optional[builtins.str] = None,
            memory_size: typing.Optional[jsii.Number] = None,
            pinned: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            timeout: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param encoding_type: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.EncodingType``.
            :param environment: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Environment``.
            :param exec_args: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.ExecArgs``.
            :param executable: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Executable``.
            :param memory_size: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.MemorySize``.
            :param pinned: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Pinned``.
            :param timeout: ``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Timeout``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                function_configuration_property = greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty(
                    encoding_type="encodingType",
                    environment=greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty(
                        access_sysfs=False,
                        execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                            isolation_mode="isolationMode",
                            run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                                gid=123,
                                uid=123
                            )
                        ),
                        resource_access_policies=[greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty(
                            resource_id="resourceId",
                
                            # the properties below are optional
                            permission="permission"
                        )],
                        variables=variables
                    ),
                    exec_args="execArgs",
                    executable="executable",
                    memory_size=123,
                    pinned=False,
                    timeout=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if encoding_type is not None:
                self._values["encoding_type"] = encoding_type
            if environment is not None:
                self._values["environment"] = environment
            if exec_args is not None:
                self._values["exec_args"] = exec_args
            if executable is not None:
                self._values["executable"] = executable
            if memory_size is not None:
                self._values["memory_size"] = memory_size
            if pinned is not None:
                self._values["pinned"] = pinned
            if timeout is not None:
                self._values["timeout"] = timeout

        @builtins.property
        def encoding_type(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.EncodingType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-encodingtype
            '''
            result = self._values.get("encoding_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def environment(
            self,
        ) -> typing.Optional[typing.Union["CfnFunctionDefinitionVersion.EnvironmentProperty", _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Environment``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-environment
            '''
            result = self._values.get("environment")
            return typing.cast(typing.Optional[typing.Union["CfnFunctionDefinitionVersion.EnvironmentProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def exec_args(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.ExecArgs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-execargs
            '''
            result = self._values.get("exec_args")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def executable(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Executable``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-executable
            '''
            result = self._values.get("executable")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def memory_size(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.MemorySize``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-memorysize
            '''
            result = self._values.get("memory_size")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def pinned(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Pinned``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-pinned
            '''
            result = self._values.get("pinned")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def timeout(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinitionVersion.FunctionConfigurationProperty.Timeout``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-functionconfiguration.html#cfn-greengrass-functiondefinitionversion-functionconfiguration-timeout
            '''
            result = self._values.get("timeout")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FunctionConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.FunctionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "function_arn": "functionArn",
            "function_configuration": "functionConfiguration",
            "id": "id",
        },
    )
    class FunctionProperty:
        def __init__(
            self,
            *,
            function_arn: builtins.str,
            function_configuration: typing.Union["CfnFunctionDefinitionVersion.FunctionConfigurationProperty", _IResolvable_da3f097b],
            id: builtins.str,
        ) -> None:
            '''
            :param function_arn: ``CfnFunctionDefinitionVersion.FunctionProperty.FunctionArn``.
            :param function_configuration: ``CfnFunctionDefinitionVersion.FunctionProperty.FunctionConfiguration``.
            :param id: ``CfnFunctionDefinitionVersion.FunctionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                # variables is of type object
                
                function_property = greengrass.CfnFunctionDefinitionVersion.FunctionProperty(
                    function_arn="functionArn",
                    function_configuration=greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty(
                        encoding_type="encodingType",
                        environment=greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty(
                            access_sysfs=False,
                            execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                                isolation_mode="isolationMode",
                                run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                                    gid=123,
                                    uid=123
                                )
                            ),
                            resource_access_policies=[greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty(
                                resource_id="resourceId",
                
                                # the properties below are optional
                                permission="permission"
                            )],
                            variables=variables
                        ),
                        exec_args="execArgs",
                        executable="executable",
                        memory_size=123,
                        pinned=False,
                        timeout=123
                    ),
                    id="id"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "function_arn": function_arn,
                "function_configuration": function_configuration,
                "id": id,
            }

        @builtins.property
        def function_arn(self) -> builtins.str:
            '''``CfnFunctionDefinitionVersion.FunctionProperty.FunctionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionarn
            '''
            result = self._values.get("function_arn")
            assert result is not None, "Required property 'function_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def function_configuration(
            self,
        ) -> typing.Union["CfnFunctionDefinitionVersion.FunctionConfigurationProperty", _IResolvable_da3f097b]:
            '''``CfnFunctionDefinitionVersion.FunctionProperty.FunctionConfiguration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-functionconfiguration
            '''
            result = self._values.get("function_configuration")
            assert result is not None, "Required property 'function_configuration' is missing"
            return typing.cast(typing.Union["CfnFunctionDefinitionVersion.FunctionConfigurationProperty", _IResolvable_da3f097b], result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnFunctionDefinitionVersion.FunctionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-function.html#cfn-greengrass-functiondefinitionversion-function-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FunctionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty",
        jsii_struct_bases=[],
        name_mapping={"permission": "permission", "resource_id": "resourceId"},
    )
    class ResourceAccessPolicyProperty:
        def __init__(
            self,
            *,
            permission: typing.Optional[builtins.str] = None,
            resource_id: builtins.str,
        ) -> None:
            '''
            :param permission: ``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.Permission``.
            :param resource_id: ``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.ResourceId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_access_policy_property = greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty(
                    resource_id="resourceId",
                
                    # the properties below are optional
                    permission="permission"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "resource_id": resource_id,
            }
            if permission is not None:
                self._values["permission"] = permission

        @builtins.property
        def permission(self) -> typing.Optional[builtins.str]:
            '''``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.Permission``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-permission
            '''
            result = self._values.get("permission")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def resource_id(self) -> builtins.str:
            '''``CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty.ResourceId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-resourceaccesspolicy.html#cfn-greengrass-functiondefinitionversion-resourceaccesspolicy-resourceid
            '''
            result = self._values.get("resource_id")
            assert result is not None, "Required property 'resource_id' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceAccessPolicyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersion.RunAsProperty",
        jsii_struct_bases=[],
        name_mapping={"gid": "gid", "uid": "uid"},
    )
    class RunAsProperty:
        def __init__(
            self,
            *,
            gid: typing.Optional[jsii.Number] = None,
            uid: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param gid: ``CfnFunctionDefinitionVersion.RunAsProperty.Gid``.
            :param uid: ``CfnFunctionDefinitionVersion.RunAsProperty.Uid``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                run_as_property = greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                    gid=123,
                    uid=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if gid is not None:
                self._values["gid"] = gid
            if uid is not None:
                self._values["uid"] = uid

        @builtins.property
        def gid(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinitionVersion.RunAsProperty.Gid``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-gid
            '''
            result = self._values.get("gid")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def uid(self) -> typing.Optional[jsii.Number]:
            '''``CfnFunctionDefinitionVersion.RunAsProperty.Uid``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-functiondefinitionversion-runas.html#cfn-greengrass-functiondefinitionversion-runas-uid
            '''
            result = self._values.get("uid")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RunAsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnFunctionDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={
        "default_config": "defaultConfig",
        "function_definition_id": "functionDefinitionId",
        "functions": "functions",
    },
)
class CfnFunctionDefinitionVersionProps:
    def __init__(
        self,
        *,
        default_config: typing.Optional[typing.Union[CfnFunctionDefinitionVersion.DefaultConfigProperty, _IResolvable_da3f097b]] = None,
        function_definition_id: builtins.str,
        functions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnFunctionDefinitionVersion.FunctionProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::FunctionDefinitionVersion``.

        :param default_config: ``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.
        :param function_definition_id: ``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.
        :param functions: ``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # variables is of type object
            
            cfn_function_definition_version_props = greengrass.CfnFunctionDefinitionVersionProps(
                function_definition_id="functionDefinitionId",
                functions=[greengrass.CfnFunctionDefinitionVersion.FunctionProperty(
                    function_arn="functionArn",
                    function_configuration=greengrass.CfnFunctionDefinitionVersion.FunctionConfigurationProperty(
                        encoding_type="encodingType",
                        environment=greengrass.CfnFunctionDefinitionVersion.EnvironmentProperty(
                            access_sysfs=False,
                            execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                                isolation_mode="isolationMode",
                                run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                                    gid=123,
                                    uid=123
                                )
                            ),
                            resource_access_policies=[greengrass.CfnFunctionDefinitionVersion.ResourceAccessPolicyProperty(
                                resource_id="resourceId",
            
                                # the properties below are optional
                                permission="permission"
                            )],
                            variables=variables
                        ),
                        exec_args="execArgs",
                        executable="executable",
                        memory_size=123,
                        pinned=False,
                        timeout=123
                    ),
                    id="id"
                )],
            
                # the properties below are optional
                default_config=greengrass.CfnFunctionDefinitionVersion.DefaultConfigProperty(
                    execution=greengrass.CfnFunctionDefinitionVersion.ExecutionProperty(
                        isolation_mode="isolationMode",
                        run_as=greengrass.CfnFunctionDefinitionVersion.RunAsProperty(
                            gid=123,
                            uid=123
                        )
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_definition_id": function_definition_id,
            "functions": functions,
        }
        if default_config is not None:
            self._values["default_config"] = default_config

    @builtins.property
    def default_config(
        self,
    ) -> typing.Optional[typing.Union[CfnFunctionDefinitionVersion.DefaultConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::FunctionDefinitionVersion.DefaultConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-defaultconfig
        '''
        result = self._values.get("default_config")
        return typing.cast(typing.Optional[typing.Union[CfnFunctionDefinitionVersion.DefaultConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def function_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::FunctionDefinitionVersion.FunctionDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functiondefinitionid
        '''
        result = self._values.get("function_definition_id")
        assert result is not None, "Required property 'function_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def functions(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnFunctionDefinitionVersion.FunctionProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::FunctionDefinitionVersion.Functions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-functiondefinitionversion.html#cfn-greengrass-functiondefinitionversion-functions
        '''
        result = self._values.get("functions")
        assert result is not None, "Required property 'functions' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnFunctionDefinitionVersion.FunctionProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFunctionDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnGroup(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnGroup",
):
    '''A CloudFormation ``AWS::Greengrass::Group``.

    :cloudformationResource: AWS::Greengrass::Group
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        
        cfn_group = greengrass.CfnGroup(self, "MyCfnGroup",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnGroup.GroupVersionProperty(
                connector_definition_version_arn="connectorDefinitionVersionArn",
                core_definition_version_arn="coreDefinitionVersionArn",
                device_definition_version_arn="deviceDefinitionVersionArn",
                function_definition_version_arn="functionDefinitionVersionArn",
                logger_definition_version_arn="loggerDefinitionVersionArn",
                resource_definition_version_arn="resourceDefinitionVersionArn",
                subscription_definition_version_arn="subscriptionDefinitionVersionArn"
            ),
            role_arn="roleArn",
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnGroup.GroupVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        role_arn: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::Group``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::Group.InitialVersion``.
        :param name: ``AWS::Greengrass::Group.Name``.
        :param role_arn: ``AWS::Greengrass::Group.RoleArn``.
        :param tags: ``AWS::Greengrass::Group.Tags``.
        '''
        props = CfnGroupProps(
            initial_version=initial_version, name=name, role_arn=role_arn, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrRoleArn")
    def attr_role_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: RoleArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrRoleArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrRoleAttachedAt")
    def attr_role_attached_at(self) -> builtins.str:
        '''
        :cloudformationAttribute: RoleAttachedAt
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrRoleAttachedAt"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnGroup.GroupVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::Group.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnGroup.GroupVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnGroup.GroupVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::Group.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::Group.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::Group.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnGroup.GroupVersionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "connector_definition_version_arn": "connectorDefinitionVersionArn",
            "core_definition_version_arn": "coreDefinitionVersionArn",
            "device_definition_version_arn": "deviceDefinitionVersionArn",
            "function_definition_version_arn": "functionDefinitionVersionArn",
            "logger_definition_version_arn": "loggerDefinitionVersionArn",
            "resource_definition_version_arn": "resourceDefinitionVersionArn",
            "subscription_definition_version_arn": "subscriptionDefinitionVersionArn",
        },
    )
    class GroupVersionProperty:
        def __init__(
            self,
            *,
            connector_definition_version_arn: typing.Optional[builtins.str] = None,
            core_definition_version_arn: typing.Optional[builtins.str] = None,
            device_definition_version_arn: typing.Optional[builtins.str] = None,
            function_definition_version_arn: typing.Optional[builtins.str] = None,
            logger_definition_version_arn: typing.Optional[builtins.str] = None,
            resource_definition_version_arn: typing.Optional[builtins.str] = None,
            subscription_definition_version_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param connector_definition_version_arn: ``CfnGroup.GroupVersionProperty.ConnectorDefinitionVersionArn``.
            :param core_definition_version_arn: ``CfnGroup.GroupVersionProperty.CoreDefinitionVersionArn``.
            :param device_definition_version_arn: ``CfnGroup.GroupVersionProperty.DeviceDefinitionVersionArn``.
            :param function_definition_version_arn: ``CfnGroup.GroupVersionProperty.FunctionDefinitionVersionArn``.
            :param logger_definition_version_arn: ``CfnGroup.GroupVersionProperty.LoggerDefinitionVersionArn``.
            :param resource_definition_version_arn: ``CfnGroup.GroupVersionProperty.ResourceDefinitionVersionArn``.
            :param subscription_definition_version_arn: ``CfnGroup.GroupVersionProperty.SubscriptionDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                group_version_property = greengrass.CfnGroup.GroupVersionProperty(
                    connector_definition_version_arn="connectorDefinitionVersionArn",
                    core_definition_version_arn="coreDefinitionVersionArn",
                    device_definition_version_arn="deviceDefinitionVersionArn",
                    function_definition_version_arn="functionDefinitionVersionArn",
                    logger_definition_version_arn="loggerDefinitionVersionArn",
                    resource_definition_version_arn="resourceDefinitionVersionArn",
                    subscription_definition_version_arn="subscriptionDefinitionVersionArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if connector_definition_version_arn is not None:
                self._values["connector_definition_version_arn"] = connector_definition_version_arn
            if core_definition_version_arn is not None:
                self._values["core_definition_version_arn"] = core_definition_version_arn
            if device_definition_version_arn is not None:
                self._values["device_definition_version_arn"] = device_definition_version_arn
            if function_definition_version_arn is not None:
                self._values["function_definition_version_arn"] = function_definition_version_arn
            if logger_definition_version_arn is not None:
                self._values["logger_definition_version_arn"] = logger_definition_version_arn
            if resource_definition_version_arn is not None:
                self._values["resource_definition_version_arn"] = resource_definition_version_arn
            if subscription_definition_version_arn is not None:
                self._values["subscription_definition_version_arn"] = subscription_definition_version_arn

        @builtins.property
        def connector_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.ConnectorDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-connectordefinitionversionarn
            '''
            result = self._values.get("connector_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def core_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.CoreDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-coredefinitionversionarn
            '''
            result = self._values.get("core_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def device_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.DeviceDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-devicedefinitionversionarn
            '''
            result = self._values.get("device_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def function_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.FunctionDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-functiondefinitionversionarn
            '''
            result = self._values.get("function_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def logger_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.LoggerDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-loggerdefinitionversionarn
            '''
            result = self._values.get("logger_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def resource_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.ResourceDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-resourcedefinitionversionarn
            '''
            result = self._values.get("resource_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def subscription_definition_version_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnGroup.GroupVersionProperty.SubscriptionDefinitionVersionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-group-groupversion.html#cfn-greengrass-group-groupversion-subscriptiondefinitionversionarn
            '''
            result = self._values.get("subscription_definition_version_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GroupVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "initial_version": "initialVersion",
        "name": "name",
        "role_arn": "roleArn",
        "tags": "tags",
    },
)
class CfnGroupProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnGroup.GroupVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        role_arn: typing.Optional[builtins.str] = None,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::Group``.

        :param initial_version: ``AWS::Greengrass::Group.InitialVersion``.
        :param name: ``AWS::Greengrass::Group.Name``.
        :param role_arn: ``AWS::Greengrass::Group.RoleArn``.
        :param tags: ``AWS::Greengrass::Group.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            
            cfn_group_props = greengrass.CfnGroupProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnGroup.GroupVersionProperty(
                    connector_definition_version_arn="connectorDefinitionVersionArn",
                    core_definition_version_arn="coreDefinitionVersionArn",
                    device_definition_version_arn="deviceDefinitionVersionArn",
                    function_definition_version_arn="functionDefinitionVersionArn",
                    logger_definition_version_arn="loggerDefinitionVersionArn",
                    resource_definition_version_arn="resourceDefinitionVersionArn",
                    subscription_definition_version_arn="subscriptionDefinitionVersionArn"
                ),
                role_arn="roleArn",
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnGroup.GroupVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::Group.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnGroup.GroupVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::Group.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::Group.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-rolearn
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::Group.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-group.html#cfn-greengrass-group-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnGroupVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnGroupVersion",
):
    '''A CloudFormation ``AWS::Greengrass::GroupVersion``.

    :cloudformationResource: AWS::Greengrass::GroupVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        cfn_group_version = greengrass.CfnGroupVersion(self, "MyCfnGroupVersion",
            group_id="groupId",
        
            # the properties below are optional
            connector_definition_version_arn="connectorDefinitionVersionArn",
            core_definition_version_arn="coreDefinitionVersionArn",
            device_definition_version_arn="deviceDefinitionVersionArn",
            function_definition_version_arn="functionDefinitionVersionArn",
            logger_definition_version_arn="loggerDefinitionVersionArn",
            resource_definition_version_arn="resourceDefinitionVersionArn",
            subscription_definition_version_arn="subscriptionDefinitionVersionArn"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        connector_definition_version_arn: typing.Optional[builtins.str] = None,
        core_definition_version_arn: typing.Optional[builtins.str] = None,
        device_definition_version_arn: typing.Optional[builtins.str] = None,
        function_definition_version_arn: typing.Optional[builtins.str] = None,
        group_id: builtins.str,
        logger_definition_version_arn: typing.Optional[builtins.str] = None,
        resource_definition_version_arn: typing.Optional[builtins.str] = None,
        subscription_definition_version_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::GroupVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param connector_definition_version_arn: ``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.
        :param core_definition_version_arn: ``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.
        :param device_definition_version_arn: ``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.
        :param function_definition_version_arn: ``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.
        :param group_id: ``AWS::Greengrass::GroupVersion.GroupId``.
        :param logger_definition_version_arn: ``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.
        :param resource_definition_version_arn: ``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.
        :param subscription_definition_version_arn: ``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.
        '''
        props = CfnGroupVersionProps(
            connector_definition_version_arn=connector_definition_version_arn,
            core_definition_version_arn=core_definition_version_arn,
            device_definition_version_arn=device_definition_version_arn,
            function_definition_version_arn=function_definition_version_arn,
            group_id=group_id,
            logger_definition_version_arn=logger_definition_version_arn,
            resource_definition_version_arn=resource_definition_version_arn,
            subscription_definition_version_arn=subscription_definition_version_arn,
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
    @jsii.member(jsii_name="connectorDefinitionVersionArn")
    def connector_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectorDefinitionVersionArn"))

    @connector_definition_version_arn.setter
    def connector_definition_version_arn(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "connectorDefinitionVersionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="coreDefinitionVersionArn")
    def core_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "coreDefinitionVersionArn"))

    @core_definition_version_arn.setter
    def core_definition_version_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "coreDefinitionVersionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deviceDefinitionVersionArn")
    def device_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deviceDefinitionVersionArn"))

    @device_definition_version_arn.setter
    def device_definition_version_arn(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "deviceDefinitionVersionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionDefinitionVersionArn")
    def function_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionDefinitionVersionArn"))

    @function_definition_version_arn.setter
    def function_definition_version_arn(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "functionDefinitionVersionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        '''``AWS::Greengrass::GroupVersion.GroupId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
        '''
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @group_id.setter
    def group_id(self, value: builtins.str) -> None:
        jsii.set(self, "groupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggerDefinitionVersionArn")
    def logger_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "loggerDefinitionVersionArn"))

    @logger_definition_version_arn.setter
    def logger_definition_version_arn(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "loggerDefinitionVersionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceDefinitionVersionArn")
    def resource_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceDefinitionVersionArn"))

    @resource_definition_version_arn.setter
    def resource_definition_version_arn(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "resourceDefinitionVersionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriptionDefinitionVersionArn")
    def subscription_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionDefinitionVersionArn"))

    @subscription_definition_version_arn.setter
    def subscription_definition_version_arn(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "subscriptionDefinitionVersionArn", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnGroupVersionProps",
    jsii_struct_bases=[],
    name_mapping={
        "connector_definition_version_arn": "connectorDefinitionVersionArn",
        "core_definition_version_arn": "coreDefinitionVersionArn",
        "device_definition_version_arn": "deviceDefinitionVersionArn",
        "function_definition_version_arn": "functionDefinitionVersionArn",
        "group_id": "groupId",
        "logger_definition_version_arn": "loggerDefinitionVersionArn",
        "resource_definition_version_arn": "resourceDefinitionVersionArn",
        "subscription_definition_version_arn": "subscriptionDefinitionVersionArn",
    },
)
class CfnGroupVersionProps:
    def __init__(
        self,
        *,
        connector_definition_version_arn: typing.Optional[builtins.str] = None,
        core_definition_version_arn: typing.Optional[builtins.str] = None,
        device_definition_version_arn: typing.Optional[builtins.str] = None,
        function_definition_version_arn: typing.Optional[builtins.str] = None,
        group_id: builtins.str,
        logger_definition_version_arn: typing.Optional[builtins.str] = None,
        resource_definition_version_arn: typing.Optional[builtins.str] = None,
        subscription_definition_version_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::GroupVersion``.

        :param connector_definition_version_arn: ``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.
        :param core_definition_version_arn: ``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.
        :param device_definition_version_arn: ``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.
        :param function_definition_version_arn: ``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.
        :param group_id: ``AWS::Greengrass::GroupVersion.GroupId``.
        :param logger_definition_version_arn: ``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.
        :param resource_definition_version_arn: ``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.
        :param subscription_definition_version_arn: ``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            cfn_group_version_props = greengrass.CfnGroupVersionProps(
                group_id="groupId",
            
                # the properties below are optional
                connector_definition_version_arn="connectorDefinitionVersionArn",
                core_definition_version_arn="coreDefinitionVersionArn",
                device_definition_version_arn="deviceDefinitionVersionArn",
                function_definition_version_arn="functionDefinitionVersionArn",
                logger_definition_version_arn="loggerDefinitionVersionArn",
                resource_definition_version_arn="resourceDefinitionVersionArn",
                subscription_definition_version_arn="subscriptionDefinitionVersionArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "group_id": group_id,
        }
        if connector_definition_version_arn is not None:
            self._values["connector_definition_version_arn"] = connector_definition_version_arn
        if core_definition_version_arn is not None:
            self._values["core_definition_version_arn"] = core_definition_version_arn
        if device_definition_version_arn is not None:
            self._values["device_definition_version_arn"] = device_definition_version_arn
        if function_definition_version_arn is not None:
            self._values["function_definition_version_arn"] = function_definition_version_arn
        if logger_definition_version_arn is not None:
            self._values["logger_definition_version_arn"] = logger_definition_version_arn
        if resource_definition_version_arn is not None:
            self._values["resource_definition_version_arn"] = resource_definition_version_arn
        if subscription_definition_version_arn is not None:
            self._values["subscription_definition_version_arn"] = subscription_definition_version_arn

    @builtins.property
    def connector_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.ConnectorDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-connectordefinitionversionarn
        '''
        result = self._values.get("connector_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def core_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.CoreDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-coredefinitionversionarn
        '''
        result = self._values.get("core_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def device_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.DeviceDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-devicedefinitionversionarn
        '''
        result = self._values.get("device_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def function_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.FunctionDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-functiondefinitionversionarn
        '''
        result = self._values.get("function_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_id(self) -> builtins.str:
        '''``AWS::Greengrass::GroupVersion.GroupId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-groupid
        '''
        result = self._values.get("group_id")
        assert result is not None, "Required property 'group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logger_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.LoggerDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-loggerdefinitionversionarn
        '''
        result = self._values.get("logger_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.ResourceDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-resourcedefinitionversionarn
        '''
        result = self._values.get("resource_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_definition_version_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::Greengrass::GroupVersion.SubscriptionDefinitionVersionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-groupversion.html#cfn-greengrass-groupversion-subscriptiondefinitionversionarn
        '''
        result = self._values.get("subscription_definition_version_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnGroupVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnLoggerDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::LoggerDefinition``.

    :cloudformationResource: AWS::Greengrass::LoggerDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        
        cfn_logger_definition = greengrass.CfnLoggerDefinition(self, "MyCfnLoggerDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty(
                loggers=[greengrass.CfnLoggerDefinition.LoggerProperty(
                    component="component",
                    id="id",
                    level="level",
                    type="type",
        
                    # the properties below are optional
                    space=123
                )]
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnLoggerDefinition.LoggerDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::LoggerDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::LoggerDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::LoggerDefinition.Name``.
        :param tags: ``AWS::Greengrass::LoggerDefinition.Tags``.
        '''
        props = CfnLoggerDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnLoggerDefinition.LoggerDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnLoggerDefinition.LoggerDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnLoggerDefinition.LoggerDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::LoggerDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::LoggerDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"loggers": "loggers"},
    )
    class LoggerDefinitionVersionProperty:
        def __init__(
            self,
            *,
            loggers: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnLoggerDefinition.LoggerProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param loggers: ``CfnLoggerDefinition.LoggerDefinitionVersionProperty.Loggers``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                logger_definition_version_property = greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty(
                    loggers=[greengrass.CfnLoggerDefinition.LoggerProperty(
                        component="component",
                        id="id",
                        level="level",
                        type="type",
                
                        # the properties below are optional
                        space=123
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "loggers": loggers,
            }

        @builtins.property
        def loggers(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnLoggerDefinition.LoggerProperty", _IResolvable_da3f097b]]]:
            '''``CfnLoggerDefinition.LoggerDefinitionVersionProperty.Loggers``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-loggerdefinitionversion.html#cfn-greengrass-loggerdefinition-loggerdefinitionversion-loggers
            '''
            result = self._values.get("loggers")
            assert result is not None, "Required property 'loggers' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnLoggerDefinition.LoggerProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggerDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinition.LoggerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "component": "component",
            "id": "id",
            "level": "level",
            "space": "space",
            "type": "type",
        },
    )
    class LoggerProperty:
        def __init__(
            self,
            *,
            component: builtins.str,
            id: builtins.str,
            level: builtins.str,
            space: typing.Optional[jsii.Number] = None,
            type: builtins.str,
        ) -> None:
            '''
            :param component: ``CfnLoggerDefinition.LoggerProperty.Component``.
            :param id: ``CfnLoggerDefinition.LoggerProperty.Id``.
            :param level: ``CfnLoggerDefinition.LoggerProperty.Level``.
            :param space: ``CfnLoggerDefinition.LoggerProperty.Space``.
            :param type: ``CfnLoggerDefinition.LoggerProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                logger_property = greengrass.CfnLoggerDefinition.LoggerProperty(
                    component="component",
                    id="id",
                    level="level",
                    type="type",
                
                    # the properties below are optional
                    space=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "component": component,
                "id": id,
                "level": level,
                "type": type,
            }
            if space is not None:
                self._values["space"] = space

        @builtins.property
        def component(self) -> builtins.str:
            '''``CfnLoggerDefinition.LoggerProperty.Component``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-component
            '''
            result = self._values.get("component")
            assert result is not None, "Required property 'component' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnLoggerDefinition.LoggerProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def level(self) -> builtins.str:
            '''``CfnLoggerDefinition.LoggerProperty.Level``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-level
            '''
            result = self._values.get("level")
            assert result is not None, "Required property 'level' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def space(self) -> typing.Optional[jsii.Number]:
            '''``CfnLoggerDefinition.LoggerProperty.Space``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-space
            '''
            result = self._values.get("space")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnLoggerDefinition.LoggerProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinition-logger.html#cfn-greengrass-loggerdefinition-logger-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnLoggerDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnLoggerDefinition.LoggerDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::LoggerDefinition``.

        :param initial_version: ``AWS::Greengrass::LoggerDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::LoggerDefinition.Name``.
        :param tags: ``AWS::Greengrass::LoggerDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            
            cfn_logger_definition_props = greengrass.CfnLoggerDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnLoggerDefinition.LoggerDefinitionVersionProperty(
                    loggers=[greengrass.CfnLoggerDefinition.LoggerProperty(
                        component="component",
                        id="id",
                        level="level",
                        type="type",
            
                        # the properties below are optional
                        space=123
                    )]
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnLoggerDefinition.LoggerDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::LoggerDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnLoggerDefinition.LoggerDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::LoggerDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::LoggerDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinition.html#cfn-greengrass-loggerdefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnLoggerDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnLoggerDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::LoggerDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::LoggerDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        cfn_logger_definition_version = greengrass.CfnLoggerDefinitionVersion(self, "MyCfnLoggerDefinitionVersion",
            logger_definition_id="loggerDefinitionId",
            loggers=[greengrass.CfnLoggerDefinitionVersion.LoggerProperty(
                component="component",
                id="id",
                level="level",
                type="type",
        
                # the properties below are optional
                space=123
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        logger_definition_id: builtins.str,
        loggers: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnLoggerDefinitionVersion.LoggerProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::LoggerDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param logger_definition_id: ``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.
        :param loggers: ``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.
        '''
        props = CfnLoggerDefinitionVersionProps(
            logger_definition_id=logger_definition_id, loggers=loggers
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
    @jsii.member(jsii_name="loggerDefinitionId")
    def logger_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "loggerDefinitionId"))

    @logger_definition_id.setter
    def logger_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "loggerDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggers")
    def loggers(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnLoggerDefinitionVersion.LoggerProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnLoggerDefinitionVersion.LoggerProperty", _IResolvable_da3f097b]]], jsii.get(self, "loggers"))

    @loggers.setter
    def loggers(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnLoggerDefinitionVersion.LoggerProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "loggers", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinitionVersion.LoggerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "component": "component",
            "id": "id",
            "level": "level",
            "space": "space",
            "type": "type",
        },
    )
    class LoggerProperty:
        def __init__(
            self,
            *,
            component: builtins.str,
            id: builtins.str,
            level: builtins.str,
            space: typing.Optional[jsii.Number] = None,
            type: builtins.str,
        ) -> None:
            '''
            :param component: ``CfnLoggerDefinitionVersion.LoggerProperty.Component``.
            :param id: ``CfnLoggerDefinitionVersion.LoggerProperty.Id``.
            :param level: ``CfnLoggerDefinitionVersion.LoggerProperty.Level``.
            :param space: ``CfnLoggerDefinitionVersion.LoggerProperty.Space``.
            :param type: ``CfnLoggerDefinitionVersion.LoggerProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                logger_property = greengrass.CfnLoggerDefinitionVersion.LoggerProperty(
                    component="component",
                    id="id",
                    level="level",
                    type="type",
                
                    # the properties below are optional
                    space=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "component": component,
                "id": id,
                "level": level,
                "type": type,
            }
            if space is not None:
                self._values["space"] = space

        @builtins.property
        def component(self) -> builtins.str:
            '''``CfnLoggerDefinitionVersion.LoggerProperty.Component``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-component
            '''
            result = self._values.get("component")
            assert result is not None, "Required property 'component' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnLoggerDefinitionVersion.LoggerProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def level(self) -> builtins.str:
            '''``CfnLoggerDefinitionVersion.LoggerProperty.Level``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-level
            '''
            result = self._values.get("level")
            assert result is not None, "Required property 'level' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def space(self) -> typing.Optional[jsii.Number]:
            '''``CfnLoggerDefinitionVersion.LoggerProperty.Space``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-space
            '''
            result = self._values.get("space")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnLoggerDefinitionVersion.LoggerProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-loggerdefinitionversion-logger.html#cfn-greengrass-loggerdefinitionversion-logger-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LoggerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnLoggerDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={"logger_definition_id": "loggerDefinitionId", "loggers": "loggers"},
)
class CfnLoggerDefinitionVersionProps:
    def __init__(
        self,
        *,
        logger_definition_id: builtins.str,
        loggers: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnLoggerDefinitionVersion.LoggerProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::LoggerDefinitionVersion``.

        :param logger_definition_id: ``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.
        :param loggers: ``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            cfn_logger_definition_version_props = greengrass.CfnLoggerDefinitionVersionProps(
                logger_definition_id="loggerDefinitionId",
                loggers=[greengrass.CfnLoggerDefinitionVersion.LoggerProperty(
                    component="component",
                    id="id",
                    level="level",
                    type="type",
            
                    # the properties below are optional
                    space=123
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "logger_definition_id": logger_definition_id,
            "loggers": loggers,
        }

    @builtins.property
    def logger_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::LoggerDefinitionVersion.LoggerDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggerdefinitionid
        '''
        result = self._values.get("logger_definition_id")
        assert result is not None, "Required property 'logger_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def loggers(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnLoggerDefinitionVersion.LoggerProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::LoggerDefinitionVersion.Loggers``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-loggerdefinitionversion.html#cfn-greengrass-loggerdefinitionversion-loggers
        '''
        result = self._values.get("loggers")
        assert result is not None, "Required property 'loggers' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnLoggerDefinitionVersion.LoggerProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnLoggerDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnResourceDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::ResourceDefinition``.

    :cloudformationResource: AWS::Greengrass::ResourceDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        
        cfn_resource_definition = greengrass.CfnResourceDefinition(self, "MyCfnResourceDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty(
                resources=[greengrass.CfnResourceDefinition.ResourceInstanceProperty(
                    id="id",
                    name="name",
                    resource_data_container=greengrass.CfnResourceDefinition.ResourceDataContainerProperty(
                        local_device_resource_data=greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty(
                            source_path="sourcePath",
        
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
        
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        local_volume_resource_data=greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty(
                            destination_path="destinationPath",
                            source_path="sourcePath",
        
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
        
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            s3_uri="s3Uri",
        
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            sage_maker_job_arn="sageMakerJobArn",
        
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        secrets_manager_secret_resource_data=greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty(
                            arn="arn",
        
                            # the properties below are optional
                            additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                        )
                    )
                )]
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnResourceDefinition.ResourceDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::ResourceDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::ResourceDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::ResourceDefinition.Name``.
        :param tags: ``AWS::Greengrass::ResourceDefinition.Tags``.
        '''
        props = CfnResourceDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnResourceDefinition.ResourceDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.ResourceDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnResourceDefinition.ResourceDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::ResourceDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::ResourceDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.GroupOwnerSettingProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auto_add_group_owner": "autoAddGroupOwner",
            "group_owner": "groupOwner",
        },
    )
    class GroupOwnerSettingProperty:
        def __init__(
            self,
            *,
            auto_add_group_owner: typing.Union[builtins.bool, _IResolvable_da3f097b],
            group_owner: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param auto_add_group_owner: ``CfnResourceDefinition.GroupOwnerSettingProperty.AutoAddGroupOwner``.
            :param group_owner: ``CfnResourceDefinition.GroupOwnerSettingProperty.GroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                group_owner_setting_property = greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                    auto_add_group_owner=False,
                
                    # the properties below are optional
                    group_owner="groupOwner"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "auto_add_group_owner": auto_add_group_owner,
            }
            if group_owner is not None:
                self._values["group_owner"] = group_owner

        @builtins.property
        def auto_add_group_owner(
            self,
        ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnResourceDefinition.GroupOwnerSettingProperty.AutoAddGroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-autoaddgroupowner
            '''
            result = self._values.get("auto_add_group_owner")
            assert result is not None, "Required property 'auto_add_group_owner' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def group_owner(self) -> typing.Optional[builtins.str]:
            '''``CfnResourceDefinition.GroupOwnerSettingProperty.GroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-groupownersetting.html#cfn-greengrass-resourcedefinition-groupownersetting-groupowner
            '''
            result = self._values.get("group_owner")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GroupOwnerSettingProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "group_owner_setting": "groupOwnerSetting",
            "source_path": "sourcePath",
        },
    )
    class LocalDeviceResourceDataProperty:
        def __init__(
            self,
            *,
            group_owner_setting: typing.Optional[typing.Union["CfnResourceDefinition.GroupOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            source_path: builtins.str,
        ) -> None:
            '''
            :param group_owner_setting: ``CfnResourceDefinition.LocalDeviceResourceDataProperty.GroupOwnerSetting``.
            :param source_path: ``CfnResourceDefinition.LocalDeviceResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                local_device_resource_data_property = greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty(
                    source_path="sourcePath",
                
                    # the properties below are optional
                    group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                        auto_add_group_owner=False,
                
                        # the properties below are optional
                        group_owner="groupOwner"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "source_path": source_path,
            }
            if group_owner_setting is not None:
                self._values["group_owner_setting"] = group_owner_setting

        @builtins.property
        def group_owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.GroupOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-groupownersetting
            '''
            result = self._values.get("group_owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.GroupOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def source_path(self) -> builtins.str:
            '''``CfnResourceDefinition.LocalDeviceResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localdeviceresourcedata.html#cfn-greengrass-resourcedefinition-localdeviceresourcedata-sourcepath
            '''
            result = self._values.get("source_path")
            assert result is not None, "Required property 'source_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LocalDeviceResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_path": "destinationPath",
            "group_owner_setting": "groupOwnerSetting",
            "source_path": "sourcePath",
        },
    )
    class LocalVolumeResourceDataProperty:
        def __init__(
            self,
            *,
            destination_path: builtins.str,
            group_owner_setting: typing.Optional[typing.Union["CfnResourceDefinition.GroupOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            source_path: builtins.str,
        ) -> None:
            '''
            :param destination_path: ``CfnResourceDefinition.LocalVolumeResourceDataProperty.DestinationPath``.
            :param group_owner_setting: ``CfnResourceDefinition.LocalVolumeResourceDataProperty.GroupOwnerSetting``.
            :param source_path: ``CfnResourceDefinition.LocalVolumeResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                local_volume_resource_data_property = greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty(
                    destination_path="destinationPath",
                    source_path="sourcePath",
                
                    # the properties below are optional
                    group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                        auto_add_group_owner=False,
                
                        # the properties below are optional
                        group_owner="groupOwner"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination_path": destination_path,
                "source_path": source_path,
            }
            if group_owner_setting is not None:
                self._values["group_owner_setting"] = group_owner_setting

        @builtins.property
        def destination_path(self) -> builtins.str:
            '''``CfnResourceDefinition.LocalVolumeResourceDataProperty.DestinationPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-destinationpath
            '''
            result = self._values.get("destination_path")
            assert result is not None, "Required property 'destination_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def group_owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.GroupOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-groupownersetting
            '''
            result = self._values.get("group_owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.GroupOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def source_path(self) -> builtins.str:
            '''``CfnResourceDefinition.LocalVolumeResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-localvolumeresourcedata.html#cfn-greengrass-resourcedefinition-localvolumeresourcedata-sourcepath
            '''
            result = self._values.get("source_path")
            assert result is not None, "Required property 'source_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LocalVolumeResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.ResourceDataContainerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "local_device_resource_data": "localDeviceResourceData",
            "local_volume_resource_data": "localVolumeResourceData",
            "s3_machine_learning_model_resource_data": "s3MachineLearningModelResourceData",
            "sage_maker_machine_learning_model_resource_data": "sageMakerMachineLearningModelResourceData",
            "secrets_manager_secret_resource_data": "secretsManagerSecretResourceData",
        },
    )
    class ResourceDataContainerProperty:
        def __init__(
            self,
            *,
            local_device_resource_data: typing.Optional[typing.Union["CfnResourceDefinition.LocalDeviceResourceDataProperty", _IResolvable_da3f097b]] = None,
            local_volume_resource_data: typing.Optional[typing.Union["CfnResourceDefinition.LocalVolumeResourceDataProperty", _IResolvable_da3f097b]] = None,
            s3_machine_learning_model_resource_data: typing.Optional[typing.Union["CfnResourceDefinition.S3MachineLearningModelResourceDataProperty", _IResolvable_da3f097b]] = None,
            sage_maker_machine_learning_model_resource_data: typing.Optional[typing.Union["CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty", _IResolvable_da3f097b]] = None,
            secrets_manager_secret_resource_data: typing.Optional[typing.Union["CfnResourceDefinition.SecretsManagerSecretResourceDataProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param local_device_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.LocalDeviceResourceData``.
            :param local_volume_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.LocalVolumeResourceData``.
            :param s3_machine_learning_model_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.
            :param sage_maker_machine_learning_model_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.
            :param secrets_manager_secret_resource_data: ``CfnResourceDefinition.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_data_container_property = greengrass.CfnResourceDefinition.ResourceDataContainerProperty(
                    local_device_resource_data=greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty(
                        source_path="sourcePath",
                
                        # the properties below are optional
                        group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                            auto_add_group_owner=False,
                
                            # the properties below are optional
                            group_owner="groupOwner"
                        )
                    ),
                    local_volume_resource_data=greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty(
                        destination_path="destinationPath",
                        source_path="sourcePath",
                
                        # the properties below are optional
                        group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                            auto_add_group_owner=False,
                
                            # the properties below are optional
                            group_owner="groupOwner"
                        )
                    ),
                    s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty(
                        destination_path="destinationPath",
                        s3_uri="s3Uri",
                
                        # the properties below are optional
                        owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                            group_owner="groupOwner",
                            group_permission="groupPermission"
                        )
                    ),
                    sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty(
                        destination_path="destinationPath",
                        sage_maker_job_arn="sageMakerJobArn",
                
                        # the properties below are optional
                        owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                            group_owner="groupOwner",
                            group_permission="groupPermission"
                        )
                    ),
                    secrets_manager_secret_resource_data=greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty(
                        arn="arn",
                
                        # the properties below are optional
                        additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if local_device_resource_data is not None:
                self._values["local_device_resource_data"] = local_device_resource_data
            if local_volume_resource_data is not None:
                self._values["local_volume_resource_data"] = local_volume_resource_data
            if s3_machine_learning_model_resource_data is not None:
                self._values["s3_machine_learning_model_resource_data"] = s3_machine_learning_model_resource_data
            if sage_maker_machine_learning_model_resource_data is not None:
                self._values["sage_maker_machine_learning_model_resource_data"] = sage_maker_machine_learning_model_resource_data
            if secrets_manager_secret_resource_data is not None:
                self._values["secrets_manager_secret_resource_data"] = secrets_manager_secret_resource_data

        @builtins.property
        def local_device_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.LocalDeviceResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.ResourceDataContainerProperty.LocalDeviceResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localdeviceresourcedata
            '''
            result = self._values.get("local_device_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.LocalDeviceResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def local_volume_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.LocalVolumeResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.ResourceDataContainerProperty.LocalVolumeResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-localvolumeresourcedata
            '''
            result = self._values.get("local_volume_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.LocalVolumeResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3_machine_learning_model_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.S3MachineLearningModelResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-s3machinelearningmodelresourcedata
            '''
            result = self._values.get("s3_machine_learning_model_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.S3MachineLearningModelResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sage_maker_machine_learning_model_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
            '''
            result = self._values.get("sage_maker_machine_learning_model_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def secrets_manager_secret_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.SecretsManagerSecretResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedatacontainer.html#cfn-greengrass-resourcedefinition-resourcedatacontainer-secretsmanagersecretresourcedata
            '''
            result = self._values.get("secrets_manager_secret_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.SecretsManagerSecretResourceDataProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceDataContainerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"resources": "resources"},
    )
    class ResourceDefinitionVersionProperty:
        def __init__(
            self,
            *,
            resources: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnResourceDefinition.ResourceInstanceProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param resources: ``CfnResourceDefinition.ResourceDefinitionVersionProperty.Resources``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_definition_version_property = greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty(
                    resources=[greengrass.CfnResourceDefinition.ResourceInstanceProperty(
                        id="id",
                        name="name",
                        resource_data_container=greengrass.CfnResourceDefinition.ResourceDataContainerProperty(
                            local_device_resource_data=greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty(
                                source_path="sourcePath",
                
                                # the properties below are optional
                                group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                    auto_add_group_owner=False,
                
                                    # the properties below are optional
                                    group_owner="groupOwner"
                                )
                            ),
                            local_volume_resource_data=greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty(
                                destination_path="destinationPath",
                                source_path="sourcePath",
                
                                # the properties below are optional
                                group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                    auto_add_group_owner=False,
                
                                    # the properties below are optional
                                    group_owner="groupOwner"
                                )
                            ),
                            s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty(
                                destination_path="destinationPath",
                                s3_uri="s3Uri",
                
                                # the properties below are optional
                                owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                    group_owner="groupOwner",
                                    group_permission="groupPermission"
                                )
                            ),
                            sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty(
                                destination_path="destinationPath",
                                sage_maker_job_arn="sageMakerJobArn",
                
                                # the properties below are optional
                                owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                    group_owner="groupOwner",
                                    group_permission="groupPermission"
                                )
                            ),
                            secrets_manager_secret_resource_data=greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty(
                                arn="arn",
                
                                # the properties below are optional
                                additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                            )
                        )
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "resources": resources,
            }

        @builtins.property
        def resources(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnResourceDefinition.ResourceInstanceProperty", _IResolvable_da3f097b]]]:
            '''``CfnResourceDefinition.ResourceDefinitionVersionProperty.Resources``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedefinitionversion.html#cfn-greengrass-resourcedefinition-resourcedefinitionversion-resources
            '''
            result = self._values.get("resources")
            assert result is not None, "Required property 'resources' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnResourceDefinition.ResourceInstanceProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty",
        jsii_struct_bases=[],
        name_mapping={
            "group_owner": "groupOwner",
            "group_permission": "groupPermission",
        },
    )
    class ResourceDownloadOwnerSettingProperty:
        def __init__(
            self,
            *,
            group_owner: builtins.str,
            group_permission: builtins.str,
        ) -> None:
            '''
            :param group_owner: ``CfnResourceDefinition.ResourceDownloadOwnerSettingProperty.GroupOwner``.
            :param group_permission: ``CfnResourceDefinition.ResourceDownloadOwnerSettingProperty.GroupPermission``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedownloadownersetting.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_download_owner_setting_property = greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                    group_owner="groupOwner",
                    group_permission="groupPermission"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "group_owner": group_owner,
                "group_permission": group_permission,
            }

        @builtins.property
        def group_owner(self) -> builtins.str:
            '''``CfnResourceDefinition.ResourceDownloadOwnerSettingProperty.GroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedownloadownersetting.html#cfn-greengrass-resourcedefinition-resourcedownloadownersetting-groupowner
            '''
            result = self._values.get("group_owner")
            assert result is not None, "Required property 'group_owner' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def group_permission(self) -> builtins.str:
            '''``CfnResourceDefinition.ResourceDownloadOwnerSettingProperty.GroupPermission``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourcedownloadownersetting.html#cfn-greengrass-resourcedefinition-resourcedownloadownersetting-grouppermission
            '''
            result = self._values.get("group_permission")
            assert result is not None, "Required property 'group_permission' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceDownloadOwnerSettingProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.ResourceInstanceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "id": "id",
            "name": "name",
            "resource_data_container": "resourceDataContainer",
        },
    )
    class ResourceInstanceProperty:
        def __init__(
            self,
            *,
            id: builtins.str,
            name: builtins.str,
            resource_data_container: typing.Union["CfnResourceDefinition.ResourceDataContainerProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param id: ``CfnResourceDefinition.ResourceInstanceProperty.Id``.
            :param name: ``CfnResourceDefinition.ResourceInstanceProperty.Name``.
            :param resource_data_container: ``CfnResourceDefinition.ResourceInstanceProperty.ResourceDataContainer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_instance_property = greengrass.CfnResourceDefinition.ResourceInstanceProperty(
                    id="id",
                    name="name",
                    resource_data_container=greengrass.CfnResourceDefinition.ResourceDataContainerProperty(
                        local_device_resource_data=greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty(
                            source_path="sourcePath",
                
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
                
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        local_volume_resource_data=greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty(
                            destination_path="destinationPath",
                            source_path="sourcePath",
                
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
                
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            s3_uri="s3Uri",
                
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            sage_maker_job_arn="sageMakerJobArn",
                
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        secrets_manager_secret_resource_data=greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty(
                            arn="arn",
                
                            # the properties below are optional
                            additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                        )
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "id": id,
                "name": name,
                "resource_data_container": resource_data_container,
            }

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnResourceDefinition.ResourceInstanceProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnResourceDefinition.ResourceInstanceProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def resource_data_container(
            self,
        ) -> typing.Union["CfnResourceDefinition.ResourceDataContainerProperty", _IResolvable_da3f097b]:
            '''``CfnResourceDefinition.ResourceInstanceProperty.ResourceDataContainer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-resourceinstance.html#cfn-greengrass-resourcedefinition-resourceinstance-resourcedatacontainer
            '''
            result = self._values.get("resource_data_container")
            assert result is not None, "Required property 'resource_data_container' is missing"
            return typing.cast(typing.Union["CfnResourceDefinition.ResourceDataContainerProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceInstanceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_path": "destinationPath",
            "owner_setting": "ownerSetting",
            "s3_uri": "s3Uri",
        },
    )
    class S3MachineLearningModelResourceDataProperty:
        def __init__(
            self,
            *,
            destination_path: builtins.str,
            owner_setting: typing.Optional[typing.Union["CfnResourceDefinition.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            s3_uri: builtins.str,
        ) -> None:
            '''
            :param destination_path: ``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.DestinationPath``.
            :param owner_setting: ``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.OwnerSetting``.
            :param s3_uri: ``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.S3Uri``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                s3_machine_learning_model_resource_data_property = greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty(
                    destination_path="destinationPath",
                    s3_uri="s3Uri",
                
                    # the properties below are optional
                    owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                        group_owner="groupOwner",
                        group_permission="groupPermission"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination_path": destination_path,
                "s3_uri": s3_uri,
            }
            if owner_setting is not None:
                self._values["owner_setting"] = owner_setting

        @builtins.property
        def destination_path(self) -> builtins.str:
            '''``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.DestinationPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-destinationpath
            '''
            result = self._values.get("destination_path")
            assert result is not None, "Required property 'destination_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.OwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-ownersetting
            '''
            result = self._values.get("owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3_uri(self) -> builtins.str:
            '''``CfnResourceDefinition.S3MachineLearningModelResourceDataProperty.S3Uri``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-s3machinelearningmodelresourcedata-s3uri
            '''
            result = self._values.get("s3_uri")
            assert result is not None, "Required property 's3_uri' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3MachineLearningModelResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_path": "destinationPath",
            "owner_setting": "ownerSetting",
            "sage_maker_job_arn": "sageMakerJobArn",
        },
    )
    class SageMakerMachineLearningModelResourceDataProperty:
        def __init__(
            self,
            *,
            destination_path: builtins.str,
            owner_setting: typing.Optional[typing.Union["CfnResourceDefinition.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            sage_maker_job_arn: builtins.str,
        ) -> None:
            '''
            :param destination_path: ``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.
            :param owner_setting: ``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.OwnerSetting``.
            :param sage_maker_job_arn: ``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                sage_maker_machine_learning_model_resource_data_property = greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty(
                    destination_path="destinationPath",
                    sage_maker_job_arn="sageMakerJobArn",
                
                    # the properties below are optional
                    owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                        group_owner="groupOwner",
                        group_permission="groupPermission"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination_path": destination_path,
                "sage_maker_job_arn": sage_maker_job_arn,
            }
            if owner_setting is not None:
                self._values["owner_setting"] = owner_setting

        @builtins.property
        def destination_path(self) -> builtins.str:
            '''``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-destinationpath
            '''
            result = self._values.get("destination_path")
            assert result is not None, "Required property 'destination_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinition.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.OwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-ownersetting
            '''
            result = self._values.get("owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinition.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sage_maker_job_arn(self) -> builtins.str:
            '''``CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinition-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
            '''
            result = self._values.get("sage_maker_job_arn")
            assert result is not None, "Required property 'sage_maker_job_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SageMakerMachineLearningModelResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "additional_staging_labels_to_download": "additionalStagingLabelsToDownload",
            "arn": "arn",
        },
    )
    class SecretsManagerSecretResourceDataProperty:
        def __init__(
            self,
            *,
            additional_staging_labels_to_download: typing.Optional[typing.Sequence[builtins.str]] = None,
            arn: builtins.str,
        ) -> None:
            '''
            :param additional_staging_labels_to_download: ``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.
            :param arn: ``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.ARN``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                secrets_manager_secret_resource_data_property = greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty(
                    arn="arn",
                
                    # the properties below are optional
                    additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "arn": arn,
            }
            if additional_staging_labels_to_download is not None:
                self._values["additional_staging_labels_to_download"] = additional_staging_labels_to_download

        @builtins.property
        def additional_staging_labels_to_download(
            self,
        ) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
            '''
            result = self._values.get("additional_staging_labels_to_download")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def arn(self) -> builtins.str:
            '''``CfnResourceDefinition.SecretsManagerSecretResourceDataProperty.ARN``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinition-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinition-secretsmanagersecretresourcedata-arn
            '''
            result = self._values.get("arn")
            assert result is not None, "Required property 'arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SecretsManagerSecretResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnResourceDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnResourceDefinition.ResourceDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::ResourceDefinition``.

        :param initial_version: ``AWS::Greengrass::ResourceDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::ResourceDefinition.Name``.
        :param tags: ``AWS::Greengrass::ResourceDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            
            cfn_resource_definition_props = greengrass.CfnResourceDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnResourceDefinition.ResourceDefinitionVersionProperty(
                    resources=[greengrass.CfnResourceDefinition.ResourceInstanceProperty(
                        id="id",
                        name="name",
                        resource_data_container=greengrass.CfnResourceDefinition.ResourceDataContainerProperty(
                            local_device_resource_data=greengrass.CfnResourceDefinition.LocalDeviceResourceDataProperty(
                                source_path="sourcePath",
            
                                # the properties below are optional
                                group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                    auto_add_group_owner=False,
            
                                    # the properties below are optional
                                    group_owner="groupOwner"
                                )
                            ),
                            local_volume_resource_data=greengrass.CfnResourceDefinition.LocalVolumeResourceDataProperty(
                                destination_path="destinationPath",
                                source_path="sourcePath",
            
                                # the properties below are optional
                                group_owner_setting=greengrass.CfnResourceDefinition.GroupOwnerSettingProperty(
                                    auto_add_group_owner=False,
            
                                    # the properties below are optional
                                    group_owner="groupOwner"
                                )
                            ),
                            s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.S3MachineLearningModelResourceDataProperty(
                                destination_path="destinationPath",
                                s3_uri="s3Uri",
            
                                # the properties below are optional
                                owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                    group_owner="groupOwner",
                                    group_permission="groupPermission"
                                )
                            ),
                            sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinition.SageMakerMachineLearningModelResourceDataProperty(
                                destination_path="destinationPath",
                                sage_maker_job_arn="sageMakerJobArn",
            
                                # the properties below are optional
                                owner_setting=greengrass.CfnResourceDefinition.ResourceDownloadOwnerSettingProperty(
                                    group_owner="groupOwner",
                                    group_permission="groupPermission"
                                )
                            ),
                            secrets_manager_secret_resource_data=greengrass.CfnResourceDefinition.SecretsManagerSecretResourceDataProperty(
                                arn="arn",
            
                                # the properties below are optional
                                additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                            )
                        )
                    )]
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnResourceDefinition.ResourceDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::ResourceDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnResourceDefinition.ResourceDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::ResourceDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::ResourceDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinition.html#cfn-greengrass-resourcedefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResourceDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnResourceDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::ResourceDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::ResourceDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        cfn_resource_definition_version = greengrass.CfnResourceDefinitionVersion(self, "MyCfnResourceDefinitionVersion",
            resource_definition_id="resourceDefinitionId",
            resources=[greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty(
                id="id",
                name="name",
                resource_data_container=greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty(
                    local_device_resource_data=greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty(
                        source_path="sourcePath",
        
                        # the properties below are optional
                        group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                            auto_add_group_owner=False,
        
                            # the properties below are optional
                            group_owner="groupOwner"
                        )
                    ),
                    local_volume_resource_data=greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty(
                        destination_path="destinationPath",
                        source_path="sourcePath",
        
                        # the properties below are optional
                        group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                            auto_add_group_owner=False,
        
                            # the properties below are optional
                            group_owner="groupOwner"
                        )
                    ),
                    s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty(
                        destination_path="destinationPath",
                        s3_uri="s3Uri",
        
                        # the properties below are optional
                        owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                            group_owner="groupOwner",
                            group_permission="groupPermission"
                        )
                    ),
                    sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty(
                        destination_path="destinationPath",
                        sage_maker_job_arn="sageMakerJobArn",
        
                        # the properties below are optional
                        owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                            group_owner="groupOwner",
                            group_permission="groupPermission"
                        )
                    ),
                    secrets_manager_secret_resource_data=greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty(
                        arn="arn",
        
                        # the properties below are optional
                        additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                    )
                )
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        resource_definition_id: builtins.str,
        resources: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnResourceDefinitionVersion.ResourceInstanceProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::ResourceDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param resource_definition_id: ``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.
        :param resources: ``AWS::Greengrass::ResourceDefinitionVersion.Resources``.
        '''
        props = CfnResourceDefinitionVersionProps(
            resource_definition_id=resource_definition_id, resources=resources
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
    @jsii.member(jsii_name="resourceDefinitionId")
    def resource_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "resourceDefinitionId"))

    @resource_definition_id.setter
    def resource_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "resourceDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resources")
    def resources(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnResourceDefinitionVersion.ResourceInstanceProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnResourceDefinitionVersion.ResourceInstanceProperty", _IResolvable_da3f097b]]], jsii.get(self, "resources"))

    @resources.setter
    def resources(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnResourceDefinitionVersion.ResourceInstanceProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "resources", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auto_add_group_owner": "autoAddGroupOwner",
            "group_owner": "groupOwner",
        },
    )
    class GroupOwnerSettingProperty:
        def __init__(
            self,
            *,
            auto_add_group_owner: typing.Union[builtins.bool, _IResolvable_da3f097b],
            group_owner: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param auto_add_group_owner: ``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.AutoAddGroupOwner``.
            :param group_owner: ``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.GroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                group_owner_setting_property = greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                    auto_add_group_owner=False,
                
                    # the properties below are optional
                    group_owner="groupOwner"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "auto_add_group_owner": auto_add_group_owner,
            }
            if group_owner is not None:
                self._values["group_owner"] = group_owner

        @builtins.property
        def auto_add_group_owner(
            self,
        ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.AutoAddGroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-autoaddgroupowner
            '''
            result = self._values.get("auto_add_group_owner")
            assert result is not None, "Required property 'auto_add_group_owner' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def group_owner(self) -> typing.Optional[builtins.str]:
            '''``CfnResourceDefinitionVersion.GroupOwnerSettingProperty.GroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-groupownersetting.html#cfn-greengrass-resourcedefinitionversion-groupownersetting-groupowner
            '''
            result = self._values.get("group_owner")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "GroupOwnerSettingProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "group_owner_setting": "groupOwnerSetting",
            "source_path": "sourcePath",
        },
    )
    class LocalDeviceResourceDataProperty:
        def __init__(
            self,
            *,
            group_owner_setting: typing.Optional[typing.Union["CfnResourceDefinitionVersion.GroupOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            source_path: builtins.str,
        ) -> None:
            '''
            :param group_owner_setting: ``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.GroupOwnerSetting``.
            :param source_path: ``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                local_device_resource_data_property = greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty(
                    source_path="sourcePath",
                
                    # the properties below are optional
                    group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                        auto_add_group_owner=False,
                
                        # the properties below are optional
                        group_owner="groupOwner"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "source_path": source_path,
            }
            if group_owner_setting is not None:
                self._values["group_owner_setting"] = group_owner_setting

        @builtins.property
        def group_owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.GroupOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.GroupOwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-groupownersetting
            '''
            result = self._values.get("group_owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.GroupOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def source_path(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localdeviceresourcedata.html#cfn-greengrass-resourcedefinitionversion-localdeviceresourcedata-sourcepath
            '''
            result = self._values.get("source_path")
            assert result is not None, "Required property 'source_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LocalDeviceResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_path": "destinationPath",
            "group_owner_setting": "groupOwnerSetting",
            "source_path": "sourcePath",
        },
    )
    class LocalVolumeResourceDataProperty:
        def __init__(
            self,
            *,
            destination_path: builtins.str,
            group_owner_setting: typing.Optional[typing.Union["CfnResourceDefinitionVersion.GroupOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            source_path: builtins.str,
        ) -> None:
            '''
            :param destination_path: ``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.DestinationPath``.
            :param group_owner_setting: ``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.GroupOwnerSetting``.
            :param source_path: ``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                local_volume_resource_data_property = greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty(
                    destination_path="destinationPath",
                    source_path="sourcePath",
                
                    # the properties below are optional
                    group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                        auto_add_group_owner=False,
                
                        # the properties below are optional
                        group_owner="groupOwner"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination_path": destination_path,
                "source_path": source_path,
            }
            if group_owner_setting is not None:
                self._values["group_owner_setting"] = group_owner_setting

        @builtins.property
        def destination_path(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.DestinationPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-destinationpath
            '''
            result = self._values.get("destination_path")
            assert result is not None, "Required property 'destination_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def group_owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.GroupOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.GroupOwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-groupownersetting
            '''
            result = self._values.get("group_owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.GroupOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def source_path(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty.SourcePath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-localvolumeresourcedata.html#cfn-greengrass-resourcedefinitionversion-localvolumeresourcedata-sourcepath
            '''
            result = self._values.get("source_path")
            assert result is not None, "Required property 'source_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LocalVolumeResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "local_device_resource_data": "localDeviceResourceData",
            "local_volume_resource_data": "localVolumeResourceData",
            "s3_machine_learning_model_resource_data": "s3MachineLearningModelResourceData",
            "sage_maker_machine_learning_model_resource_data": "sageMakerMachineLearningModelResourceData",
            "secrets_manager_secret_resource_data": "secretsManagerSecretResourceData",
        },
    )
    class ResourceDataContainerProperty:
        def __init__(
            self,
            *,
            local_device_resource_data: typing.Optional[typing.Union["CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty", _IResolvable_da3f097b]] = None,
            local_volume_resource_data: typing.Optional[typing.Union["CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty", _IResolvable_da3f097b]] = None,
            s3_machine_learning_model_resource_data: typing.Optional[typing.Union["CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty", _IResolvable_da3f097b]] = None,
            sage_maker_machine_learning_model_resource_data: typing.Optional[typing.Union["CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty", _IResolvable_da3f097b]] = None,
            secrets_manager_secret_resource_data: typing.Optional[typing.Union["CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param local_device_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalDeviceResourceData``.
            :param local_volume_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalVolumeResourceData``.
            :param s3_machine_learning_model_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.
            :param sage_maker_machine_learning_model_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.
            :param secrets_manager_secret_resource_data: ``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_data_container_property = greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty(
                    local_device_resource_data=greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty(
                        source_path="sourcePath",
                
                        # the properties below are optional
                        group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                            auto_add_group_owner=False,
                
                            # the properties below are optional
                            group_owner="groupOwner"
                        )
                    ),
                    local_volume_resource_data=greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty(
                        destination_path="destinationPath",
                        source_path="sourcePath",
                
                        # the properties below are optional
                        group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                            auto_add_group_owner=False,
                
                            # the properties below are optional
                            group_owner="groupOwner"
                        )
                    ),
                    s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty(
                        destination_path="destinationPath",
                        s3_uri="s3Uri",
                
                        # the properties below are optional
                        owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                            group_owner="groupOwner",
                            group_permission="groupPermission"
                        )
                    ),
                    sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty(
                        destination_path="destinationPath",
                        sage_maker_job_arn="sageMakerJobArn",
                
                        # the properties below are optional
                        owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                            group_owner="groupOwner",
                            group_permission="groupPermission"
                        )
                    ),
                    secrets_manager_secret_resource_data=greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty(
                        arn="arn",
                
                        # the properties below are optional
                        additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if local_device_resource_data is not None:
                self._values["local_device_resource_data"] = local_device_resource_data
            if local_volume_resource_data is not None:
                self._values["local_volume_resource_data"] = local_volume_resource_data
            if s3_machine_learning_model_resource_data is not None:
                self._values["s3_machine_learning_model_resource_data"] = s3_machine_learning_model_resource_data
            if sage_maker_machine_learning_model_resource_data is not None:
                self._values["sage_maker_machine_learning_model_resource_data"] = sage_maker_machine_learning_model_resource_data
            if secrets_manager_secret_resource_data is not None:
                self._values["secrets_manager_secret_resource_data"] = secrets_manager_secret_resource_data

        @builtins.property
        def local_device_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalDeviceResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localdeviceresourcedata
            '''
            result = self._values.get("local_device_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def local_volume_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.ResourceDataContainerProperty.LocalVolumeResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-localvolumeresourcedata
            '''
            result = self._values.get("local_volume_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3_machine_learning_model_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.ResourceDataContainerProperty.S3MachineLearningModelResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-s3machinelearningmodelresourcedata
            '''
            result = self._values.get("s3_machine_learning_model_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sage_maker_machine_learning_model_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SageMakerMachineLearningModelResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-sagemakermachinelearningmodelresourcedata
            '''
            result = self._values.get("sage_maker_machine_learning_model_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def secrets_manager_secret_resource_data(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.ResourceDataContainerProperty.SecretsManagerSecretResourceData``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedatacontainer.html#cfn-greengrass-resourcedefinitionversion-resourcedatacontainer-secretsmanagersecretresourcedata
            '''
            result = self._values.get("secrets_manager_secret_resource_data")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceDataContainerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty",
        jsii_struct_bases=[],
        name_mapping={
            "group_owner": "groupOwner",
            "group_permission": "groupPermission",
        },
    )
    class ResourceDownloadOwnerSettingProperty:
        def __init__(
            self,
            *,
            group_owner: builtins.str,
            group_permission: builtins.str,
        ) -> None:
            '''
            :param group_owner: ``CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty.GroupOwner``.
            :param group_permission: ``CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty.GroupPermission``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedownloadownersetting.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_download_owner_setting_property = greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                    group_owner="groupOwner",
                    group_permission="groupPermission"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "group_owner": group_owner,
                "group_permission": group_permission,
            }

        @builtins.property
        def group_owner(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty.GroupOwner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedownloadownersetting.html#cfn-greengrass-resourcedefinitionversion-resourcedownloadownersetting-groupowner
            '''
            result = self._values.get("group_owner")
            assert result is not None, "Required property 'group_owner' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def group_permission(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty.GroupPermission``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourcedownloadownersetting.html#cfn-greengrass-resourcedefinitionversion-resourcedownloadownersetting-grouppermission
            '''
            result = self._values.get("group_permission")
            assert result is not None, "Required property 'group_permission' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceDownloadOwnerSettingProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "id": "id",
            "name": "name",
            "resource_data_container": "resourceDataContainer",
        },
    )
    class ResourceInstanceProperty:
        def __init__(
            self,
            *,
            id: builtins.str,
            name: builtins.str,
            resource_data_container: typing.Union["CfnResourceDefinitionVersion.ResourceDataContainerProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param id: ``CfnResourceDefinitionVersion.ResourceInstanceProperty.Id``.
            :param name: ``CfnResourceDefinitionVersion.ResourceInstanceProperty.Name``.
            :param resource_data_container: ``CfnResourceDefinitionVersion.ResourceInstanceProperty.ResourceDataContainer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                resource_instance_property = greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty(
                    id="id",
                    name="name",
                    resource_data_container=greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty(
                        local_device_resource_data=greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty(
                            source_path="sourcePath",
                
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
                
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        local_volume_resource_data=greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty(
                            destination_path="destinationPath",
                            source_path="sourcePath",
                
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
                
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            s3_uri="s3Uri",
                
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            sage_maker_job_arn="sageMakerJobArn",
                
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        secrets_manager_secret_resource_data=greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty(
                            arn="arn",
                
                            # the properties below are optional
                            additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                        )
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "id": id,
                "name": name,
                "resource_data_container": resource_data_container,
            }

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.ResourceInstanceProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.ResourceInstanceProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def resource_data_container(
            self,
        ) -> typing.Union["CfnResourceDefinitionVersion.ResourceDataContainerProperty", _IResolvable_da3f097b]:
            '''``CfnResourceDefinitionVersion.ResourceInstanceProperty.ResourceDataContainer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-resourceinstance.html#cfn-greengrass-resourcedefinitionversion-resourceinstance-resourcedatacontainer
            '''
            result = self._values.get("resource_data_container")
            assert result is not None, "Required property 'resource_data_container' is missing"
            return typing.cast(typing.Union["CfnResourceDefinitionVersion.ResourceDataContainerProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceInstanceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_path": "destinationPath",
            "owner_setting": "ownerSetting",
            "s3_uri": "s3Uri",
        },
    )
    class S3MachineLearningModelResourceDataProperty:
        def __init__(
            self,
            *,
            destination_path: builtins.str,
            owner_setting: typing.Optional[typing.Union["CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            s3_uri: builtins.str,
        ) -> None:
            '''
            :param destination_path: ``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.DestinationPath``.
            :param owner_setting: ``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.OwnerSetting``.
            :param s3_uri: ``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.S3Uri``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                s3_machine_learning_model_resource_data_property = greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty(
                    destination_path="destinationPath",
                    s3_uri="s3Uri",
                
                    # the properties below are optional
                    owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                        group_owner="groupOwner",
                        group_permission="groupPermission"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination_path": destination_path,
                "s3_uri": s3_uri,
            }
            if owner_setting is not None:
                self._values["owner_setting"] = owner_setting

        @builtins.property
        def destination_path(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.DestinationPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-destinationpath
            '''
            result = self._values.get("destination_path")
            assert result is not None, "Required property 'destination_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.OwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-ownersetting
            '''
            result = self._values.get("owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3_uri(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty.S3Uri``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-s3machinelearningmodelresourcedata-s3uri
            '''
            result = self._values.get("s3_uri")
            assert result is not None, "Required property 's3_uri' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3MachineLearningModelResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "destination_path": "destinationPath",
            "owner_setting": "ownerSetting",
            "sage_maker_job_arn": "sageMakerJobArn",
        },
    )
    class SageMakerMachineLearningModelResourceDataProperty:
        def __init__(
            self,
            *,
            destination_path: builtins.str,
            owner_setting: typing.Optional[typing.Union["CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]] = None,
            sage_maker_job_arn: builtins.str,
        ) -> None:
            '''
            :param destination_path: ``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.
            :param owner_setting: ``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.OwnerSetting``.
            :param sage_maker_job_arn: ``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                sage_maker_machine_learning_model_resource_data_property = greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty(
                    destination_path="destinationPath",
                    sage_maker_job_arn="sageMakerJobArn",
                
                    # the properties below are optional
                    owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                        group_owner="groupOwner",
                        group_permission="groupPermission"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "destination_path": destination_path,
                "sage_maker_job_arn": sage_maker_job_arn,
            }
            if owner_setting is not None:
                self._values["owner_setting"] = owner_setting

        @builtins.property
        def destination_path(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.DestinationPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-destinationpath
            '''
            result = self._values.get("destination_path")
            assert result is not None, "Required property 'destination_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner_setting(
            self,
        ) -> typing.Optional[typing.Union["CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]]:
            '''``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.OwnerSetting``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-ownersetting
            '''
            result = self._values.get("owner_setting")
            return typing.cast(typing.Optional[typing.Union["CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sage_maker_job_arn(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty.SageMakerJobArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata.html#cfn-greengrass-resourcedefinitionversion-sagemakermachinelearningmodelresourcedata-sagemakerjobarn
            '''
            result = self._values.get("sage_maker_job_arn")
            assert result is not None, "Required property 'sage_maker_job_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SageMakerMachineLearningModelResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "additional_staging_labels_to_download": "additionalStagingLabelsToDownload",
            "arn": "arn",
        },
    )
    class SecretsManagerSecretResourceDataProperty:
        def __init__(
            self,
            *,
            additional_staging_labels_to_download: typing.Optional[typing.Sequence[builtins.str]] = None,
            arn: builtins.str,
        ) -> None:
            '''
            :param additional_staging_labels_to_download: ``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.
            :param arn: ``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.ARN``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                secrets_manager_secret_resource_data_property = greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty(
                    arn="arn",
                
                    # the properties below are optional
                    additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "arn": arn,
            }
            if additional_staging_labels_to_download is not None:
                self._values["additional_staging_labels_to_download"] = additional_staging_labels_to_download

        @builtins.property
        def additional_staging_labels_to_download(
            self,
        ) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.AdditionalStagingLabelsToDownload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-additionalstaginglabelstodownload
            '''
            result = self._values.get("additional_staging_labels_to_download")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def arn(self) -> builtins.str:
            '''``CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty.ARN``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata.html#cfn-greengrass-resourcedefinitionversion-secretsmanagersecretresourcedata-arn
            '''
            result = self._values.get("arn")
            assert result is not None, "Required property 'arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SecretsManagerSecretResourceDataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnResourceDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={
        "resource_definition_id": "resourceDefinitionId",
        "resources": "resources",
    },
)
class CfnResourceDefinitionVersionProps:
    def __init__(
        self,
        *,
        resource_definition_id: builtins.str,
        resources: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnResourceDefinitionVersion.ResourceInstanceProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::ResourceDefinitionVersion``.

        :param resource_definition_id: ``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.
        :param resources: ``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            cfn_resource_definition_version_props = greengrass.CfnResourceDefinitionVersionProps(
                resource_definition_id="resourceDefinitionId",
                resources=[greengrass.CfnResourceDefinitionVersion.ResourceInstanceProperty(
                    id="id",
                    name="name",
                    resource_data_container=greengrass.CfnResourceDefinitionVersion.ResourceDataContainerProperty(
                        local_device_resource_data=greengrass.CfnResourceDefinitionVersion.LocalDeviceResourceDataProperty(
                            source_path="sourcePath",
            
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
            
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        local_volume_resource_data=greengrass.CfnResourceDefinitionVersion.LocalVolumeResourceDataProperty(
                            destination_path="destinationPath",
                            source_path="sourcePath",
            
                            # the properties below are optional
                            group_owner_setting=greengrass.CfnResourceDefinitionVersion.GroupOwnerSettingProperty(
                                auto_add_group_owner=False,
            
                                # the properties below are optional
                                group_owner="groupOwner"
                            )
                        ),
                        s3_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.S3MachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            s3_uri="s3Uri",
            
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        sage_maker_machine_learning_model_resource_data=greengrass.CfnResourceDefinitionVersion.SageMakerMachineLearningModelResourceDataProperty(
                            destination_path="destinationPath",
                            sage_maker_job_arn="sageMakerJobArn",
            
                            # the properties below are optional
                            owner_setting=greengrass.CfnResourceDefinitionVersion.ResourceDownloadOwnerSettingProperty(
                                group_owner="groupOwner",
                                group_permission="groupPermission"
                            )
                        ),
                        secrets_manager_secret_resource_data=greengrass.CfnResourceDefinitionVersion.SecretsManagerSecretResourceDataProperty(
                            arn="arn",
            
                            # the properties below are optional
                            additional_staging_labels_to_download=["additionalStagingLabelsToDownload"]
                        )
                    )
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource_definition_id": resource_definition_id,
            "resources": resources,
        }

    @builtins.property
    def resource_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::ResourceDefinitionVersion.ResourceDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resourcedefinitionid
        '''
        result = self._values.get("resource_definition_id")
        assert result is not None, "Required property 'resource_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resources(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnResourceDefinitionVersion.ResourceInstanceProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::ResourceDefinitionVersion.Resources``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-resourcedefinitionversion.html#cfn-greengrass-resourcedefinitionversion-resources
        '''
        result = self._values.get("resources")
        assert result is not None, "Required property 'resources' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnResourceDefinitionVersion.ResourceInstanceProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResourceDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSubscriptionDefinition(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinition",
):
    '''A CloudFormation ``AWS::Greengrass::SubscriptionDefinition``.

    :cloudformationResource: AWS::Greengrass::SubscriptionDefinition
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        # tags is of type object
        
        cfn_subscription_definition = greengrass.CfnSubscriptionDefinition(self, "MyCfnSubscriptionDefinition",
            name="name",
        
            # the properties below are optional
            initial_version=greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty(
                subscriptions=[greengrass.CfnSubscriptionDefinition.SubscriptionProperty(
                    id="id",
                    source="source",
                    subject="subject",
                    target="target"
                )]
            ),
            tags=tags
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        initial_version: typing.Optional[typing.Union["CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::Greengrass::SubscriptionDefinition``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param initial_version: ``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::SubscriptionDefinition.Name``.
        :param tags: ``AWS::Greengrass::SubscriptionDefinition.Tags``.
        '''
        props = CfnSubscriptionDefinitionProps(
            initial_version=initial_version, name=name, tags=tags
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
        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLatestVersionArn")
    def attr_latest_version_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: LatestVersionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrLatestVersionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''
        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

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
    @jsii.member(jsii_name="initialVersion")
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union["CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
        '''
        return typing.cast(typing.Optional[typing.Union["CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", _IResolvable_da3f097b]], jsii.get(self, "initialVersion"))

    @initial_version.setter
    def initial_version(
        self,
        value: typing.Optional[typing.Union["CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "initialVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::SubscriptionDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Greengrass::SubscriptionDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty",
        jsii_struct_bases=[],
        name_mapping={"subscriptions": "subscriptions"},
    )
    class SubscriptionDefinitionVersionProperty:
        def __init__(
            self,
            *,
            subscriptions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnSubscriptionDefinition.SubscriptionProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param subscriptions: ``CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty.Subscriptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                subscription_definition_version_property = greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty(
                    subscriptions=[greengrass.CfnSubscriptionDefinition.SubscriptionProperty(
                        id="id",
                        source="source",
                        subject="subject",
                        target="target"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "subscriptions": subscriptions,
            }

        @builtins.property
        def subscriptions(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSubscriptionDefinition.SubscriptionProperty", _IResolvable_da3f097b]]]:
            '''``CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty.Subscriptions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinition-subscriptiondefinitionversion-subscriptions
            '''
            result = self._values.get("subscriptions")
            assert result is not None, "Required property 'subscriptions' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSubscriptionDefinition.SubscriptionProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SubscriptionDefinitionVersionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinition.SubscriptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "id": "id",
            "source": "source",
            "subject": "subject",
            "target": "target",
        },
    )
    class SubscriptionProperty:
        def __init__(
            self,
            *,
            id: builtins.str,
            source: builtins.str,
            subject: builtins.str,
            target: builtins.str,
        ) -> None:
            '''
            :param id: ``CfnSubscriptionDefinition.SubscriptionProperty.Id``.
            :param source: ``CfnSubscriptionDefinition.SubscriptionProperty.Source``.
            :param subject: ``CfnSubscriptionDefinition.SubscriptionProperty.Subject``.
            :param target: ``CfnSubscriptionDefinition.SubscriptionProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                subscription_property = greengrass.CfnSubscriptionDefinition.SubscriptionProperty(
                    id="id",
                    source="source",
                    subject="subject",
                    target="target"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "id": id,
                "source": source,
                "subject": subject,
                "target": target,
            }

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnSubscriptionDefinition.SubscriptionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def source(self) -> builtins.str:
            '''``CfnSubscriptionDefinition.SubscriptionProperty.Source``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-source
            '''
            result = self._values.get("source")
            assert result is not None, "Required property 'source' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def subject(self) -> builtins.str:
            '''``CfnSubscriptionDefinition.SubscriptionProperty.Subject``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-subject
            '''
            result = self._values.get("subject")
            assert result is not None, "Required property 'subject' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def target(self) -> builtins.str:
            '''``CfnSubscriptionDefinition.SubscriptionProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinition-subscription.html#cfn-greengrass-subscriptiondefinition-subscription-target
            '''
            result = self._values.get("target")
            assert result is not None, "Required property 'target' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SubscriptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinitionProps",
    jsii_struct_bases=[],
    name_mapping={"initial_version": "initialVersion", "name": "name", "tags": "tags"},
)
class CfnSubscriptionDefinitionProps:
    def __init__(
        self,
        *,
        initial_version: typing.Optional[typing.Union[CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty, _IResolvable_da3f097b]] = None,
        name: builtins.str,
        tags: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::SubscriptionDefinition``.

        :param initial_version: ``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.
        :param name: ``AWS::Greengrass::SubscriptionDefinition.Name``.
        :param tags: ``AWS::Greengrass::SubscriptionDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            # tags is of type object
            
            cfn_subscription_definition_props = greengrass.CfnSubscriptionDefinitionProps(
                name="name",
            
                # the properties below are optional
                initial_version=greengrass.CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty(
                    subscriptions=[greengrass.CfnSubscriptionDefinition.SubscriptionProperty(
                        id="id",
                        source="source",
                        subject="subject",
                        target="target"
                    )]
                ),
                tags=tags
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if initial_version is not None:
            self._values["initial_version"] = initial_version
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def initial_version(
        self,
    ) -> typing.Optional[typing.Union[CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty, _IResolvable_da3f097b]]:
        '''``AWS::Greengrass::SubscriptionDefinition.InitialVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-initialversion
        '''
        result = self._values.get("initial_version")
        return typing.cast(typing.Optional[typing.Union[CfnSubscriptionDefinition.SubscriptionDefinitionVersionProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Greengrass::SubscriptionDefinition.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Any:
        '''``AWS::Greengrass::SubscriptionDefinition.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinition.html#cfn-greengrass-subscriptiondefinition-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSubscriptionDefinitionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSubscriptionDefinitionVersion(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinitionVersion",
):
    '''A CloudFormation ``AWS::Greengrass::SubscriptionDefinitionVersion``.

    :cloudformationResource: AWS::Greengrass::SubscriptionDefinitionVersion
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_greengrass as greengrass
        
        cfn_subscription_definition_version = greengrass.CfnSubscriptionDefinitionVersion(self, "MyCfnSubscriptionDefinitionVersion",
            subscription_definition_id="subscriptionDefinitionId",
            subscriptions=[greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty(
                id="id",
                source="source",
                subject="subject",
                target="target"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        subscription_definition_id: builtins.str,
        subscriptions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnSubscriptionDefinitionVersion.SubscriptionProperty", _IResolvable_da3f097b]]],
    ) -> None:
        '''Create a new ``AWS::Greengrass::SubscriptionDefinitionVersion``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param subscription_definition_id: ``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.
        :param subscriptions: ``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.
        '''
        props = CfnSubscriptionDefinitionVersionProps(
            subscription_definition_id=subscription_definition_id,
            subscriptions=subscriptions,
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
    @jsii.member(jsii_name="subscriptionDefinitionId")
    def subscription_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
        '''
        return typing.cast(builtins.str, jsii.get(self, "subscriptionDefinitionId"))

    @subscription_definition_id.setter
    def subscription_definition_id(self, value: builtins.str) -> None:
        jsii.set(self, "subscriptionDefinitionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriptions")
    def subscriptions(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSubscriptionDefinitionVersion.SubscriptionProperty", _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSubscriptionDefinitionVersion.SubscriptionProperty", _IResolvable_da3f097b]]], jsii.get(self, "subscriptions"))

    @subscriptions.setter
    def subscriptions(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSubscriptionDefinitionVersion.SubscriptionProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "subscriptions", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "id": "id",
            "source": "source",
            "subject": "subject",
            "target": "target",
        },
    )
    class SubscriptionProperty:
        def __init__(
            self,
            *,
            id: builtins.str,
            source: builtins.str,
            subject: builtins.str,
            target: builtins.str,
        ) -> None:
            '''
            :param id: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Id``.
            :param source: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Source``.
            :param subject: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Subject``.
            :param target: ``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_greengrass as greengrass
                
                subscription_property = greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty(
                    id="id",
                    source="source",
                    subject="subject",
                    target="target"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "id": id,
                "source": source,
                "subject": subject,
                "target": target,
            }

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def source(self) -> builtins.str:
            '''``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Source``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-source
            '''
            result = self._values.get("source")
            assert result is not None, "Required property 'source' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def subject(self) -> builtins.str:
            '''``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Subject``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-subject
            '''
            result = self._values.get("subject")
            assert result is not None, "Required property 'subject' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def target(self) -> builtins.str:
            '''``CfnSubscriptionDefinitionVersion.SubscriptionProperty.Target``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-greengrass-subscriptiondefinitionversion-subscription.html#cfn-greengrass-subscriptiondefinitionversion-subscription-target
            '''
            result = self._values.get("target")
            assert result is not None, "Required property 'target' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SubscriptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_greengrass.CfnSubscriptionDefinitionVersionProps",
    jsii_struct_bases=[],
    name_mapping={
        "subscription_definition_id": "subscriptionDefinitionId",
        "subscriptions": "subscriptions",
    },
)
class CfnSubscriptionDefinitionVersionProps:
    def __init__(
        self,
        *,
        subscription_definition_id: builtins.str,
        subscriptions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnSubscriptionDefinitionVersion.SubscriptionProperty, _IResolvable_da3f097b]]],
    ) -> None:
        '''Properties for defining a ``AWS::Greengrass::SubscriptionDefinitionVersion``.

        :param subscription_definition_id: ``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.
        :param subscriptions: ``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_greengrass as greengrass
            
            cfn_subscription_definition_version_props = greengrass.CfnSubscriptionDefinitionVersionProps(
                subscription_definition_id="subscriptionDefinitionId",
                subscriptions=[greengrass.CfnSubscriptionDefinitionVersion.SubscriptionProperty(
                    id="id",
                    source="source",
                    subject="subject",
                    target="target"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "subscription_definition_id": subscription_definition_id,
            "subscriptions": subscriptions,
        }

    @builtins.property
    def subscription_definition_id(self) -> builtins.str:
        '''``AWS::Greengrass::SubscriptionDefinitionVersion.SubscriptionDefinitionId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptiondefinitionid
        '''
        result = self._values.get("subscription_definition_id")
        assert result is not None, "Required property 'subscription_definition_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscriptions(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnSubscriptionDefinitionVersion.SubscriptionProperty, _IResolvable_da3f097b]]]:
        '''``AWS::Greengrass::SubscriptionDefinitionVersion.Subscriptions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-greengrass-subscriptiondefinitionversion.html#cfn-greengrass-subscriptiondefinitionversion-subscriptions
        '''
        result = self._values.get("subscriptions")
        assert result is not None, "Required property 'subscriptions' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnSubscriptionDefinitionVersion.SubscriptionProperty, _IResolvable_da3f097b]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSubscriptionDefinitionVersionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnConnectorDefinition",
    "CfnConnectorDefinitionProps",
    "CfnConnectorDefinitionVersion",
    "CfnConnectorDefinitionVersionProps",
    "CfnCoreDefinition",
    "CfnCoreDefinitionProps",
    "CfnCoreDefinitionVersion",
    "CfnCoreDefinitionVersionProps",
    "CfnDeviceDefinition",
    "CfnDeviceDefinitionProps",
    "CfnDeviceDefinitionVersion",
    "CfnDeviceDefinitionVersionProps",
    "CfnFunctionDefinition",
    "CfnFunctionDefinitionProps",
    "CfnFunctionDefinitionVersion",
    "CfnFunctionDefinitionVersionProps",
    "CfnGroup",
    "CfnGroupProps",
    "CfnGroupVersion",
    "CfnGroupVersionProps",
    "CfnLoggerDefinition",
    "CfnLoggerDefinitionProps",
    "CfnLoggerDefinitionVersion",
    "CfnLoggerDefinitionVersionProps",
    "CfnResourceDefinition",
    "CfnResourceDefinitionProps",
    "CfnResourceDefinitionVersion",
    "CfnResourceDefinitionVersionProps",
    "CfnSubscriptionDefinition",
    "CfnSubscriptionDefinitionProps",
    "CfnSubscriptionDefinitionVersion",
    "CfnSubscriptionDefinitionVersionProps",
]

publication.publish()
