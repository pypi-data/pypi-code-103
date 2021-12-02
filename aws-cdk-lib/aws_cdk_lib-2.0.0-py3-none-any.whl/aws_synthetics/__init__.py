'''
# AWS::Synthetics Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_synthetics as aws_synthetics
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
class CfnCanary(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary",
):
    '''A CloudFormation ``AWS::Synthetics::Canary``.

    :cloudformationResource: AWS::Synthetics::Canary
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_synthetics as synthetics
        
        cfn_canary = synthetics.CfnCanary(self, "MyCfnCanary",
            artifact_s3_location="artifactS3Location",
            code=synthetics.CfnCanary.CodeProperty(
                handler="handler",
        
                # the properties below are optional
                s3_bucket="s3Bucket",
                s3_key="s3Key",
                s3_object_version="s3ObjectVersion",
                script="script"
            ),
            execution_role_arn="executionRoleArn",
            name="name",
            runtime_version="runtimeVersion",
            schedule=synthetics.CfnCanary.ScheduleProperty(
                expression="expression",
        
                # the properties below are optional
                duration_in_seconds="durationInSeconds"
            ),
            start_canary_after_creation=False,
        
            # the properties below are optional
            artifact_config=synthetics.CfnCanary.ArtifactConfigProperty(
                s3_encryption=synthetics.CfnCanary.S3EncryptionProperty(
                    encryption_mode="encryptionMode",
                    kms_key_arn="kmsKeyArn"
                )
            ),
            failure_retention_period=123,
            run_config=synthetics.CfnCanary.RunConfigProperty(
                active_tracing=False,
                environment_variables={
                    "environment_variables_key": "environmentVariables"
                },
                memory_in_mb=123,
                timeout_in_seconds=123
            ),
            success_retention_period=123,
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            visual_reference=synthetics.CfnCanary.VisualReferenceProperty(
                base_canary_run_id="baseCanaryRunId",
        
                # the properties below are optional
                base_screenshots=[synthetics.CfnCanary.BaseScreenshotProperty(
                    screenshot_name="screenshotName",
        
                    # the properties below are optional
                    ignore_coordinates=["ignoreCoordinates"]
                )]
            ),
            vpc_config=synthetics.CfnCanary.VPCConfigProperty(
                security_group_ids=["securityGroupIds"],
                subnet_ids=["subnetIds"],
        
                # the properties below are optional
                vpc_id="vpcId"
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        artifact_config: typing.Optional[typing.Union["CfnCanary.ArtifactConfigProperty", _IResolvable_da3f097b]] = None,
        artifact_s3_location: builtins.str,
        code: typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b],
        execution_role_arn: builtins.str,
        failure_retention_period: typing.Optional[jsii.Number] = None,
        name: builtins.str,
        run_config: typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]] = None,
        runtime_version: builtins.str,
        schedule: typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b],
        start_canary_after_creation: typing.Union[builtins.bool, _IResolvable_da3f097b],
        success_retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        visual_reference: typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]] = None,
        vpc_config: typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::Synthetics::Canary``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param artifact_config: ``AWS::Synthetics::Canary.ArtifactConfig``.
        :param artifact_s3_location: ``AWS::Synthetics::Canary.ArtifactS3Location``.
        :param code: ``AWS::Synthetics::Canary.Code``.
        :param execution_role_arn: ``AWS::Synthetics::Canary.ExecutionRoleArn``.
        :param failure_retention_period: ``AWS::Synthetics::Canary.FailureRetentionPeriod``.
        :param name: ``AWS::Synthetics::Canary.Name``.
        :param run_config: ``AWS::Synthetics::Canary.RunConfig``.
        :param runtime_version: ``AWS::Synthetics::Canary.RuntimeVersion``.
        :param schedule: ``AWS::Synthetics::Canary.Schedule``.
        :param start_canary_after_creation: ``AWS::Synthetics::Canary.StartCanaryAfterCreation``.
        :param success_retention_period: ``AWS::Synthetics::Canary.SuccessRetentionPeriod``.
        :param tags: ``AWS::Synthetics::Canary.Tags``.
        :param visual_reference: ``AWS::Synthetics::Canary.VisualReference``.
        :param vpc_config: ``AWS::Synthetics::Canary.VPCConfig``.
        '''
        props = CfnCanaryProps(
            artifact_config=artifact_config,
            artifact_s3_location=artifact_s3_location,
            code=code,
            execution_role_arn=execution_role_arn,
            failure_retention_period=failure_retention_period,
            name=name,
            run_config=run_config,
            runtime_version=runtime_version,
            schedule=schedule,
            start_canary_after_creation=start_canary_after_creation,
            success_retention_period=success_retention_period,
            tags=tags,
            visual_reference=visual_reference,
            vpc_config=vpc_config,
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
    @jsii.member(jsii_name="artifactConfig")
    def artifact_config(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.ArtifactConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.ArtifactConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-artifactconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.ArtifactConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "artifactConfig"))

    @artifact_config.setter
    def artifact_config(
        self,
        value: typing.Optional[typing.Union["CfnCanary.ArtifactConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "artifactConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactS3Location")
    def artifact_s3_location(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ArtifactS3Location``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-artifacts3location
        '''
        return typing.cast(builtins.str, jsii.get(self, "artifactS3Location"))

    @artifact_s3_location.setter
    def artifact_s3_location(self, value: builtins.str) -> None:
        jsii.set(self, "artifactS3Location", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrId")
    def attr_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: Id
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrState")
    def attr_state(self) -> builtins.str:
        '''
        :cloudformationAttribute: State
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrState"))

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
    @jsii.member(jsii_name="code")
    def code(self) -> typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Code``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-code
        '''
        return typing.cast(typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b], jsii.get(self, "code"))

    @code.setter
    def code(
        self,
        value: typing.Union["CfnCanary.CodeProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "code", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ExecutionRoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-executionrolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureRetentionPeriod")
    def failure_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.FailureRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-failureretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failureRetentionPeriod"))

    @failure_retention_period.setter
    def failure_retention_period(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "failureRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-name
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runConfig")
    def run_config(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.RunConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "runConfig"))

    @run_config.setter
    def run_config(
        self,
        value: typing.Optional[typing.Union["CfnCanary.RunConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "runConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeVersion")
    def runtime_version(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.RuntimeVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runtimeversion
        '''
        return typing.cast(builtins.str, jsii.get(self, "runtimeVersion"))

    @runtime_version.setter
    def runtime_version(self, value: builtins.str) -> None:
        jsii.set(self, "runtimeVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(
        self,
    ) -> typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-schedule
        '''
        return typing.cast(typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b], jsii.get(self, "schedule"))

    @schedule.setter
    def schedule(
        self,
        value: typing.Union["CfnCanary.ScheduleProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "schedule", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startCanaryAfterCreation")
    def start_canary_after_creation(
        self,
    ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.StartCanaryAfterCreation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-startcanaryaftercreation
        '''
        return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], jsii.get(self, "startCanaryAfterCreation"))

    @start_canary_after_creation.setter
    def start_canary_after_creation(
        self,
        value: typing.Union[builtins.bool, _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "startCanaryAfterCreation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successRetentionPeriod")
    def success_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.SuccessRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-successretentionperiod
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "successRetentionPeriod"))

    @success_retention_period.setter
    def success_retention_period(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "successRetentionPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::Synthetics::Canary.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="visualReference")
    def visual_reference(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VisualReference``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-visualreference
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]], jsii.get(self, "visualReference"))

    @visual_reference.setter
    def visual_reference(
        self,
        value: typing.Optional[typing.Union["CfnCanary.VisualReferenceProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "visualReference", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcConfig")
    def vpc_config(
        self,
    ) -> typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VPCConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-vpcconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "vpcConfig"))

    @vpc_config.setter
    def vpc_config(
        self,
        value: typing.Optional[typing.Union["CfnCanary.VPCConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "vpcConfig", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.ArtifactConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"s3_encryption": "s3Encryption"},
    )
    class ArtifactConfigProperty:
        def __init__(
            self,
            *,
            s3_encryption: typing.Optional[typing.Union["CfnCanary.S3EncryptionProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param s3_encryption: ``CfnCanary.ArtifactConfigProperty.S3Encryption``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-artifactconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                artifact_config_property = synthetics.CfnCanary.ArtifactConfigProperty(
                    s3_encryption=synthetics.CfnCanary.S3EncryptionProperty(
                        encryption_mode="encryptionMode",
                        kms_key_arn="kmsKeyArn"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if s3_encryption is not None:
                self._values["s3_encryption"] = s3_encryption

        @builtins.property
        def s3_encryption(
            self,
        ) -> typing.Optional[typing.Union["CfnCanary.S3EncryptionProperty", _IResolvable_da3f097b]]:
            '''``CfnCanary.ArtifactConfigProperty.S3Encryption``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-artifactconfig.html#cfn-synthetics-canary-artifactconfig-s3encryption
            '''
            result = self._values.get("s3_encryption")
            return typing.cast(typing.Optional[typing.Union["CfnCanary.S3EncryptionProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.BaseScreenshotProperty",
        jsii_struct_bases=[],
        name_mapping={
            "ignore_coordinates": "ignoreCoordinates",
            "screenshot_name": "screenshotName",
        },
    )
    class BaseScreenshotProperty:
        def __init__(
            self,
            *,
            ignore_coordinates: typing.Optional[typing.Sequence[builtins.str]] = None,
            screenshot_name: builtins.str,
        ) -> None:
            '''
            :param ignore_coordinates: ``CfnCanary.BaseScreenshotProperty.IgnoreCoordinates``.
            :param screenshot_name: ``CfnCanary.BaseScreenshotProperty.ScreenshotName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-basescreenshot.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                base_screenshot_property = synthetics.CfnCanary.BaseScreenshotProperty(
                    screenshot_name="screenshotName",
                
                    # the properties below are optional
                    ignore_coordinates=["ignoreCoordinates"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "screenshot_name": screenshot_name,
            }
            if ignore_coordinates is not None:
                self._values["ignore_coordinates"] = ignore_coordinates

        @builtins.property
        def ignore_coordinates(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnCanary.BaseScreenshotProperty.IgnoreCoordinates``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-basescreenshot.html#cfn-synthetics-canary-basescreenshot-ignorecoordinates
            '''
            result = self._values.get("ignore_coordinates")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def screenshot_name(self) -> builtins.str:
            '''``CfnCanary.BaseScreenshotProperty.ScreenshotName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-basescreenshot.html#cfn-synthetics-canary-basescreenshot-screenshotname
            '''
            result = self._values.get("screenshot_name")
            assert result is not None, "Required property 'screenshot_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BaseScreenshotProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.CodeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "handler": "handler",
            "s3_bucket": "s3Bucket",
            "s3_key": "s3Key",
            "s3_object_version": "s3ObjectVersion",
            "script": "script",
        },
    )
    class CodeProperty:
        def __init__(
            self,
            *,
            handler: builtins.str,
            s3_bucket: typing.Optional[builtins.str] = None,
            s3_key: typing.Optional[builtins.str] = None,
            s3_object_version: typing.Optional[builtins.str] = None,
            script: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param handler: ``CfnCanary.CodeProperty.Handler``.
            :param s3_bucket: ``CfnCanary.CodeProperty.S3Bucket``.
            :param s3_key: ``CfnCanary.CodeProperty.S3Key``.
            :param s3_object_version: ``CfnCanary.CodeProperty.S3ObjectVersion``.
            :param script: ``CfnCanary.CodeProperty.Script``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                code_property = synthetics.CfnCanary.CodeProperty(
                    handler="handler",
                
                    # the properties below are optional
                    s3_bucket="s3Bucket",
                    s3_key="s3Key",
                    s3_object_version="s3ObjectVersion",
                    script="script"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "handler": handler,
            }
            if s3_bucket is not None:
                self._values["s3_bucket"] = s3_bucket
            if s3_key is not None:
                self._values["s3_key"] = s3_key
            if s3_object_version is not None:
                self._values["s3_object_version"] = s3_object_version
            if script is not None:
                self._values["script"] = script

        @builtins.property
        def handler(self) -> builtins.str:
            '''``CfnCanary.CodeProperty.Handler``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-handler
            '''
            result = self._values.get("handler")
            assert result is not None, "Required property 'handler' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def s3_bucket(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.S3Bucket``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-s3bucket
            '''
            result = self._values.get("s3_bucket")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_key(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.S3Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-s3key
            '''
            result = self._values.get("s3_key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def s3_object_version(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.S3ObjectVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-s3objectversion
            '''
            result = self._values.get("s3_object_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def script(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.CodeProperty.Script``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-code.html#cfn-synthetics-canary-code-script
            '''
            result = self._values.get("script")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CodeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.RunConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "active_tracing": "activeTracing",
            "environment_variables": "environmentVariables",
            "memory_in_mb": "memoryInMb",
            "timeout_in_seconds": "timeoutInSeconds",
        },
    )
    class RunConfigProperty:
        def __init__(
            self,
            *,
            active_tracing: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            environment_variables: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]] = None,
            memory_in_mb: typing.Optional[jsii.Number] = None,
            timeout_in_seconds: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param active_tracing: ``CfnCanary.RunConfigProperty.ActiveTracing``.
            :param environment_variables: ``CfnCanary.RunConfigProperty.EnvironmentVariables``.
            :param memory_in_mb: ``CfnCanary.RunConfigProperty.MemoryInMB``.
            :param timeout_in_seconds: ``CfnCanary.RunConfigProperty.TimeoutInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                run_config_property = synthetics.CfnCanary.RunConfigProperty(
                    active_tracing=False,
                    environment_variables={
                        "environment_variables_key": "environmentVariables"
                    },
                    memory_in_mb=123,
                    timeout_in_seconds=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if active_tracing is not None:
                self._values["active_tracing"] = active_tracing
            if environment_variables is not None:
                self._values["environment_variables"] = environment_variables
            if memory_in_mb is not None:
                self._values["memory_in_mb"] = memory_in_mb
            if timeout_in_seconds is not None:
                self._values["timeout_in_seconds"] = timeout_in_seconds

        @builtins.property
        def active_tracing(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnCanary.RunConfigProperty.ActiveTracing``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-activetracing
            '''
            result = self._values.get("active_tracing")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def environment_variables(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]]:
            '''``CfnCanary.RunConfigProperty.EnvironmentVariables``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-environmentvariables
            '''
            result = self._values.get("environment_variables")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]], result)

        @builtins.property
        def memory_in_mb(self) -> typing.Optional[jsii.Number]:
            '''``CfnCanary.RunConfigProperty.MemoryInMB``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-memoryinmb
            '''
            result = self._values.get("memory_in_mb")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def timeout_in_seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnCanary.RunConfigProperty.TimeoutInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-runconfig.html#cfn-synthetics-canary-runconfig-timeoutinseconds
            '''
            result = self._values.get("timeout_in_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RunConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.S3EncryptionProperty",
        jsii_struct_bases=[],
        name_mapping={"encryption_mode": "encryptionMode", "kms_key_arn": "kmsKeyArn"},
    )
    class S3EncryptionProperty:
        def __init__(
            self,
            *,
            encryption_mode: typing.Optional[builtins.str] = None,
            kms_key_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param encryption_mode: ``CfnCanary.S3EncryptionProperty.EncryptionMode``.
            :param kms_key_arn: ``CfnCanary.S3EncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-s3encryption.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                s3_encryption_property = synthetics.CfnCanary.S3EncryptionProperty(
                    encryption_mode="encryptionMode",
                    kms_key_arn="kmsKeyArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if encryption_mode is not None:
                self._values["encryption_mode"] = encryption_mode
            if kms_key_arn is not None:
                self._values["kms_key_arn"] = kms_key_arn

        @builtins.property
        def encryption_mode(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.S3EncryptionProperty.EncryptionMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-s3encryption.html#cfn-synthetics-canary-s3encryption-encryptionmode
            '''
            result = self._values.get("encryption_mode")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def kms_key_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.S3EncryptionProperty.KmsKeyArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-s3encryption.html#cfn-synthetics-canary-s3encryption-kmskeyarn
            '''
            result = self._values.get("kms_key_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3EncryptionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.ScheduleProperty",
        jsii_struct_bases=[],
        name_mapping={
            "duration_in_seconds": "durationInSeconds",
            "expression": "expression",
        },
    )
    class ScheduleProperty:
        def __init__(
            self,
            *,
            duration_in_seconds: typing.Optional[builtins.str] = None,
            expression: builtins.str,
        ) -> None:
            '''
            :param duration_in_seconds: ``CfnCanary.ScheduleProperty.DurationInSeconds``.
            :param expression: ``CfnCanary.ScheduleProperty.Expression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-schedule.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                schedule_property = synthetics.CfnCanary.ScheduleProperty(
                    expression="expression",
                
                    # the properties below are optional
                    duration_in_seconds="durationInSeconds"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "expression": expression,
            }
            if duration_in_seconds is not None:
                self._values["duration_in_seconds"] = duration_in_seconds

        @builtins.property
        def duration_in_seconds(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.ScheduleProperty.DurationInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-schedule.html#cfn-synthetics-canary-schedule-durationinseconds
            '''
            result = self._values.get("duration_in_seconds")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def expression(self) -> builtins.str:
            '''``CfnCanary.ScheduleProperty.Expression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-schedule.html#cfn-synthetics-canary-schedule-expression
            '''
            result = self._values.get("expression")
            assert result is not None, "Required property 'expression' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ScheduleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.VPCConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "security_group_ids": "securityGroupIds",
            "subnet_ids": "subnetIds",
            "vpc_id": "vpcId",
        },
    )
    class VPCConfigProperty:
        def __init__(
            self,
            *,
            security_group_ids: typing.Sequence[builtins.str],
            subnet_ids: typing.Sequence[builtins.str],
            vpc_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param security_group_ids: ``CfnCanary.VPCConfigProperty.SecurityGroupIds``.
            :param subnet_ids: ``CfnCanary.VPCConfigProperty.SubnetIds``.
            :param vpc_id: ``CfnCanary.VPCConfigProperty.VpcId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                v_pCConfig_property = synthetics.CfnCanary.VPCConfigProperty(
                    security_group_ids=["securityGroupIds"],
                    subnet_ids=["subnetIds"],
                
                    # the properties below are optional
                    vpc_id="vpcId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "security_group_ids": security_group_ids,
                "subnet_ids": subnet_ids,
            }
            if vpc_id is not None:
                self._values["vpc_id"] = vpc_id

        @builtins.property
        def security_group_ids(self) -> typing.List[builtins.str]:
            '''``CfnCanary.VPCConfigProperty.SecurityGroupIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html#cfn-synthetics-canary-vpcconfig-securitygroupids
            '''
            result = self._values.get("security_group_ids")
            assert result is not None, "Required property 'security_group_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def subnet_ids(self) -> typing.List[builtins.str]:
            '''``CfnCanary.VPCConfigProperty.SubnetIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html#cfn-synthetics-canary-vpcconfig-subnetids
            '''
            result = self._values.get("subnet_ids")
            assert result is not None, "Required property 'subnet_ids' is missing"
            return typing.cast(typing.List[builtins.str], result)

        @builtins.property
        def vpc_id(self) -> typing.Optional[builtins.str]:
            '''``CfnCanary.VPCConfigProperty.VpcId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-vpcconfig.html#cfn-synthetics-canary-vpcconfig-vpcid
            '''
            result = self._values.get("vpc_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VPCConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_synthetics.CfnCanary.VisualReferenceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "base_canary_run_id": "baseCanaryRunId",
            "base_screenshots": "baseScreenshots",
        },
    )
    class VisualReferenceProperty:
        def __init__(
            self,
            *,
            base_canary_run_id: builtins.str,
            base_screenshots: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCanary.BaseScreenshotProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param base_canary_run_id: ``CfnCanary.VisualReferenceProperty.BaseCanaryRunId``.
            :param base_screenshots: ``CfnCanary.VisualReferenceProperty.BaseScreenshots``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-visualreference.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_synthetics as synthetics
                
                visual_reference_property = synthetics.CfnCanary.VisualReferenceProperty(
                    base_canary_run_id="baseCanaryRunId",
                
                    # the properties below are optional
                    base_screenshots=[synthetics.CfnCanary.BaseScreenshotProperty(
                        screenshot_name="screenshotName",
                
                        # the properties below are optional
                        ignore_coordinates=["ignoreCoordinates"]
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "base_canary_run_id": base_canary_run_id,
            }
            if base_screenshots is not None:
                self._values["base_screenshots"] = base_screenshots

        @builtins.property
        def base_canary_run_id(self) -> builtins.str:
            '''``CfnCanary.VisualReferenceProperty.BaseCanaryRunId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-visualreference.html#cfn-synthetics-canary-visualreference-basecanaryrunid
            '''
            result = self._values.get("base_canary_run_id")
            assert result is not None, "Required property 'base_canary_run_id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def base_screenshots(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCanary.BaseScreenshotProperty", _IResolvable_da3f097b]]]]:
            '''``CfnCanary.VisualReferenceProperty.BaseScreenshots``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-synthetics-canary-visualreference.html#cfn-synthetics-canary-visualreference-basescreenshots
            '''
            result = self._values.get("base_screenshots")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCanary.BaseScreenshotProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VisualReferenceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_synthetics.CfnCanaryProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_config": "artifactConfig",
        "artifact_s3_location": "artifactS3Location",
        "code": "code",
        "execution_role_arn": "executionRoleArn",
        "failure_retention_period": "failureRetentionPeriod",
        "name": "name",
        "run_config": "runConfig",
        "runtime_version": "runtimeVersion",
        "schedule": "schedule",
        "start_canary_after_creation": "startCanaryAfterCreation",
        "success_retention_period": "successRetentionPeriod",
        "tags": "tags",
        "visual_reference": "visualReference",
        "vpc_config": "vpcConfig",
    },
)
class CfnCanaryProps:
    def __init__(
        self,
        *,
        artifact_config: typing.Optional[typing.Union[CfnCanary.ArtifactConfigProperty, _IResolvable_da3f097b]] = None,
        artifact_s3_location: builtins.str,
        code: typing.Union[CfnCanary.CodeProperty, _IResolvable_da3f097b],
        execution_role_arn: builtins.str,
        failure_retention_period: typing.Optional[jsii.Number] = None,
        name: builtins.str,
        run_config: typing.Optional[typing.Union[CfnCanary.RunConfigProperty, _IResolvable_da3f097b]] = None,
        runtime_version: builtins.str,
        schedule: typing.Union[CfnCanary.ScheduleProperty, _IResolvable_da3f097b],
        start_canary_after_creation: typing.Union[builtins.bool, _IResolvable_da3f097b],
        success_retention_period: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        visual_reference: typing.Optional[typing.Union[CfnCanary.VisualReferenceProperty, _IResolvable_da3f097b]] = None,
        vpc_config: typing.Optional[typing.Union[CfnCanary.VPCConfigProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::Synthetics::Canary``.

        :param artifact_config: ``AWS::Synthetics::Canary.ArtifactConfig``.
        :param artifact_s3_location: ``AWS::Synthetics::Canary.ArtifactS3Location``.
        :param code: ``AWS::Synthetics::Canary.Code``.
        :param execution_role_arn: ``AWS::Synthetics::Canary.ExecutionRoleArn``.
        :param failure_retention_period: ``AWS::Synthetics::Canary.FailureRetentionPeriod``.
        :param name: ``AWS::Synthetics::Canary.Name``.
        :param run_config: ``AWS::Synthetics::Canary.RunConfig``.
        :param runtime_version: ``AWS::Synthetics::Canary.RuntimeVersion``.
        :param schedule: ``AWS::Synthetics::Canary.Schedule``.
        :param start_canary_after_creation: ``AWS::Synthetics::Canary.StartCanaryAfterCreation``.
        :param success_retention_period: ``AWS::Synthetics::Canary.SuccessRetentionPeriod``.
        :param tags: ``AWS::Synthetics::Canary.Tags``.
        :param visual_reference: ``AWS::Synthetics::Canary.VisualReference``.
        :param vpc_config: ``AWS::Synthetics::Canary.VPCConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_synthetics as synthetics
            
            cfn_canary_props = synthetics.CfnCanaryProps(
                artifact_s3_location="artifactS3Location",
                code=synthetics.CfnCanary.CodeProperty(
                    handler="handler",
            
                    # the properties below are optional
                    s3_bucket="s3Bucket",
                    s3_key="s3Key",
                    s3_object_version="s3ObjectVersion",
                    script="script"
                ),
                execution_role_arn="executionRoleArn",
                name="name",
                runtime_version="runtimeVersion",
                schedule=synthetics.CfnCanary.ScheduleProperty(
                    expression="expression",
            
                    # the properties below are optional
                    duration_in_seconds="durationInSeconds"
                ),
                start_canary_after_creation=False,
            
                # the properties below are optional
                artifact_config=synthetics.CfnCanary.ArtifactConfigProperty(
                    s3_encryption=synthetics.CfnCanary.S3EncryptionProperty(
                        encryption_mode="encryptionMode",
                        kms_key_arn="kmsKeyArn"
                    )
                ),
                failure_retention_period=123,
                run_config=synthetics.CfnCanary.RunConfigProperty(
                    active_tracing=False,
                    environment_variables={
                        "environment_variables_key": "environmentVariables"
                    },
                    memory_in_mb=123,
                    timeout_in_seconds=123
                ),
                success_retention_period=123,
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                visual_reference=synthetics.CfnCanary.VisualReferenceProperty(
                    base_canary_run_id="baseCanaryRunId",
            
                    # the properties below are optional
                    base_screenshots=[synthetics.CfnCanary.BaseScreenshotProperty(
                        screenshot_name="screenshotName",
            
                        # the properties below are optional
                        ignore_coordinates=["ignoreCoordinates"]
                    )]
                ),
                vpc_config=synthetics.CfnCanary.VPCConfigProperty(
                    security_group_ids=["securityGroupIds"],
                    subnet_ids=["subnetIds"],
            
                    # the properties below are optional
                    vpc_id="vpcId"
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_s3_location": artifact_s3_location,
            "code": code,
            "execution_role_arn": execution_role_arn,
            "name": name,
            "runtime_version": runtime_version,
            "schedule": schedule,
            "start_canary_after_creation": start_canary_after_creation,
        }
        if artifact_config is not None:
            self._values["artifact_config"] = artifact_config
        if failure_retention_period is not None:
            self._values["failure_retention_period"] = failure_retention_period
        if run_config is not None:
            self._values["run_config"] = run_config
        if success_retention_period is not None:
            self._values["success_retention_period"] = success_retention_period
        if tags is not None:
            self._values["tags"] = tags
        if visual_reference is not None:
            self._values["visual_reference"] = visual_reference
        if vpc_config is not None:
            self._values["vpc_config"] = vpc_config

    @builtins.property
    def artifact_config(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.ArtifactConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.ArtifactConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-artifactconfig
        '''
        result = self._values.get("artifact_config")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.ArtifactConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def artifact_s3_location(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ArtifactS3Location``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-artifacts3location
        '''
        result = self._values.get("artifact_s3_location")
        assert result is not None, "Required property 'artifact_s3_location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def code(self) -> typing.Union[CfnCanary.CodeProperty, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Code``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-code
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(typing.Union[CfnCanary.CodeProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.ExecutionRoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-executionrolearn
        '''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def failure_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.FailureRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-failureretentionperiod
        '''
        result = self._values.get("failure_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-name
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_config(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.RunConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.RunConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runconfig
        '''
        result = self._values.get("run_config")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.RunConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def runtime_version(self) -> builtins.str:
        '''``AWS::Synthetics::Canary.RuntimeVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-runtimeversion
        '''
        result = self._values.get("runtime_version")
        assert result is not None, "Required property 'runtime_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def schedule(
        self,
    ) -> typing.Union[CfnCanary.ScheduleProperty, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.Schedule``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-schedule
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(typing.Union[CfnCanary.ScheduleProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def start_canary_after_creation(
        self,
    ) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
        '''``AWS::Synthetics::Canary.StartCanaryAfterCreation``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-startcanaryaftercreation
        '''
        result = self._values.get("start_canary_after_creation")
        assert result is not None, "Required property 'start_canary_after_creation' is missing"
        return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

    @builtins.property
    def success_retention_period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::Synthetics::Canary.SuccessRetentionPeriod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-successretentionperiod
        '''
        result = self._values.get("success_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::Synthetics::Canary.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def visual_reference(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.VisualReferenceProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VisualReference``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-visualreference
        '''
        result = self._values.get("visual_reference")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.VisualReferenceProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def vpc_config(
        self,
    ) -> typing.Optional[typing.Union[CfnCanary.VPCConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::Synthetics::Canary.VPCConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-vpcconfig
        '''
        result = self._values.get("vpc_config")
        return typing.cast(typing.Optional[typing.Union[CfnCanary.VPCConfigProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCanaryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnCanary",
    "CfnCanaryProps",
]

publication.publish()
