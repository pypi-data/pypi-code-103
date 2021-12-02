'''
# AWS::IoTEvents Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_iotevents as aws_iotevents
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
class CfnDetectorModel(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel",
):
    '''A CloudFormation ``AWS::IoTEvents::DetectorModel``.

    :cloudformationResource: AWS::IoTEvents::DetectorModel
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iotevents as iotevents
        
        cfn_detector_model = iotevents.CfnDetectorModel(self, "MyCfnDetectorModel",
            detector_model_definition=iotevents.CfnDetectorModel.DetectorModelDefinitionProperty(
                initial_state_name="initialStateName",
                states=[iotevents.CfnDetectorModel.StateProperty(
                    state_name="stateName",
        
                    # the properties below are optional
                    on_enter=iotevents.CfnDetectorModel.OnEnterProperty(
                        events=[iotevents.CfnDetectorModel.EventProperty(
                            event_name="eventName",
        
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
        
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
        
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
        
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
        
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )],
                            condition="condition"
                        )]
                    ),
                    on_exit=iotevents.CfnDetectorModel.OnExitProperty(
                        events=[iotevents.CfnDetectorModel.EventProperty(
                            event_name="eventName",
        
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
        
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
        
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
        
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
        
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )],
                            condition="condition"
                        )]
                    ),
                    on_input=iotevents.CfnDetectorModel.OnInputProperty(
                        events=[iotevents.CfnDetectorModel.EventProperty(
                            event_name="eventName",
        
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
        
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
        
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
        
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
        
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )],
                            condition="condition"
                        )],
                        transition_events=[iotevents.CfnDetectorModel.TransitionEventProperty(
                            condition="condition",
                            event_name="eventName",
                            next_state="nextState",
        
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
        
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
        
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
        
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
        
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
        
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )]
                        )]
                    )
                )]
            ),
            role_arn="roleArn",
        
            # the properties below are optional
            detector_model_description="detectorModelDescription",
            detector_model_name="detectorModelName",
            evaluation_method="evaluationMethod",
            key="key",
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
        detector_model_definition: typing.Union["CfnDetectorModel.DetectorModelDefinitionProperty", _IResolvable_da3f097b],
        detector_model_description: typing.Optional[builtins.str] = None,
        detector_model_name: typing.Optional[builtins.str] = None,
        evaluation_method: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        role_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IoTEvents::DetectorModel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param detector_model_definition: ``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.
        :param detector_model_description: ``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.
        :param detector_model_name: ``AWS::IoTEvents::DetectorModel.DetectorModelName``.
        :param evaluation_method: ``AWS::IoTEvents::DetectorModel.EvaluationMethod``.
        :param key: ``AWS::IoTEvents::DetectorModel.Key``.
        :param role_arn: ``AWS::IoTEvents::DetectorModel.RoleArn``.
        :param tags: ``AWS::IoTEvents::DetectorModel.Tags``.
        '''
        props = CfnDetectorModelProps(
            detector_model_definition=detector_model_definition,
            detector_model_description=detector_model_description,
            detector_model_name=detector_model_name,
            evaluation_method=evaluation_method,
            key=key,
            role_arn=role_arn,
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
    @jsii.member(jsii_name="detectorModelDefinition")
    def detector_model_definition(
        self,
    ) -> typing.Union["CfnDetectorModel.DetectorModelDefinitionProperty", _IResolvable_da3f097b]:
        '''``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldefinition
        '''
        return typing.cast(typing.Union["CfnDetectorModel.DetectorModelDefinitionProperty", _IResolvable_da3f097b], jsii.get(self, "detectorModelDefinition"))

    @detector_model_definition.setter
    def detector_model_definition(
        self,
        value: typing.Union["CfnDetectorModel.DetectorModelDefinitionProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "detectorModelDefinition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorModelDescription")
    def detector_model_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldescription
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorModelDescription"))

    @detector_model_description.setter
    def detector_model_description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "detectorModelDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectorModelName")
    def detector_model_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.DetectorModelName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodelname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "detectorModelName"))

    @detector_model_name.setter
    def detector_model_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "detectorModelName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evaluationMethod")
    def evaluation_method(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.EvaluationMethod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-evaluationmethod
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evaluationMethod"))

    @evaluation_method.setter
    def evaluation_method(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "evaluationMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.Key``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-key
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "key"))

    @key.setter
    def key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "key", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''``AWS::IoTEvents::DetectorModel.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoTEvents::DetectorModel.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.ActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "clear_timer": "clearTimer",
            "dynamo_db": "dynamoDb",
            "dynamo_d_bv2": "dynamoDBv2",
            "firehose": "firehose",
            "iot_events": "iotEvents",
            "iot_site_wise": "iotSiteWise",
            "iot_topic_publish": "iotTopicPublish",
            "lambda_": "lambda",
            "reset_timer": "resetTimer",
            "set_timer": "setTimer",
            "set_variable": "setVariable",
            "sns": "sns",
            "sqs": "sqs",
        },
    )
    class ActionProperty:
        def __init__(
            self,
            *,
            clear_timer: typing.Optional[typing.Union["CfnDetectorModel.ClearTimerProperty", _IResolvable_da3f097b]] = None,
            dynamo_db: typing.Optional[typing.Union["CfnDetectorModel.DynamoDBProperty", _IResolvable_da3f097b]] = None,
            dynamo_d_bv2: typing.Optional[typing.Union["CfnDetectorModel.DynamoDBv2Property", _IResolvable_da3f097b]] = None,
            firehose: typing.Optional[typing.Union["CfnDetectorModel.FirehoseProperty", _IResolvable_da3f097b]] = None,
            iot_events: typing.Optional[typing.Union["CfnDetectorModel.IotEventsProperty", _IResolvable_da3f097b]] = None,
            iot_site_wise: typing.Optional[typing.Union["CfnDetectorModel.IotSiteWiseProperty", _IResolvable_da3f097b]] = None,
            iot_topic_publish: typing.Optional[typing.Union["CfnDetectorModel.IotTopicPublishProperty", _IResolvable_da3f097b]] = None,
            lambda_: typing.Optional[typing.Union["CfnDetectorModel.LambdaProperty", _IResolvable_da3f097b]] = None,
            reset_timer: typing.Optional[typing.Union["CfnDetectorModel.ResetTimerProperty", _IResolvable_da3f097b]] = None,
            set_timer: typing.Optional[typing.Union["CfnDetectorModel.SetTimerProperty", _IResolvable_da3f097b]] = None,
            set_variable: typing.Optional[typing.Union["CfnDetectorModel.SetVariableProperty", _IResolvable_da3f097b]] = None,
            sns: typing.Optional[typing.Union["CfnDetectorModel.SnsProperty", _IResolvable_da3f097b]] = None,
            sqs: typing.Optional[typing.Union["CfnDetectorModel.SqsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param clear_timer: ``CfnDetectorModel.ActionProperty.ClearTimer``.
            :param dynamo_db: ``CfnDetectorModel.ActionProperty.DynamoDB``.
            :param dynamo_d_bv2: ``CfnDetectorModel.ActionProperty.DynamoDBv2``.
            :param firehose: ``CfnDetectorModel.ActionProperty.Firehose``.
            :param iot_events: ``CfnDetectorModel.ActionProperty.IotEvents``.
            :param iot_site_wise: ``CfnDetectorModel.ActionProperty.IotSiteWise``.
            :param iot_topic_publish: ``CfnDetectorModel.ActionProperty.IotTopicPublish``.
            :param lambda_: ``CfnDetectorModel.ActionProperty.Lambda``.
            :param reset_timer: ``CfnDetectorModel.ActionProperty.ResetTimer``.
            :param set_timer: ``CfnDetectorModel.ActionProperty.SetTimer``.
            :param set_variable: ``CfnDetectorModel.ActionProperty.SetVariable``.
            :param sns: ``CfnDetectorModel.ActionProperty.Sns``.
            :param sqs: ``CfnDetectorModel.ActionProperty.Sqs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                action_property = iotevents.CfnDetectorModel.ActionProperty(
                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                        timer_name="timerName"
                    ),
                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                        hash_key_field="hashKeyField",
                        hash_key_value="hashKeyValue",
                        table_name="tableName",
                
                        # the properties below are optional
                        hash_key_type="hashKeyType",
                        operation="operation",
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        ),
                        payload_field="payloadField",
                        range_key_field="rangeKeyField",
                        range_key_type="rangeKeyType",
                        range_key_value="rangeKeyValue"
                    ),
                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                        table_name="tableName",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                        delivery_stream_name="deliveryStreamName",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        ),
                        separator="separator"
                    ),
                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                        input_name="inputName",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                boolean_value="booleanValue",
                                double_value="doubleValue",
                                integer_value="integerValue",
                                string_value="stringValue"
                            ),
                
                            # the properties below are optional
                            quality="quality",
                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                time_in_seconds="timeInSeconds",
                
                                # the properties below are optional
                                offset_in_nanos="offsetInNanos"
                            )
                        ),
                
                        # the properties below are optional
                        asset_id="assetId",
                        entry_id="entryId",
                        property_alias="propertyAlias",
                        property_id="propertyId"
                    ),
                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                        mqtt_topic="mqttTopic",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                        function_arn="functionArn",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                        timer_name="timerName"
                    ),
                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                        timer_name="timerName",
                
                        # the properties below are optional
                        duration_expression="durationExpression",
                        seconds=123
                    ),
                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                        value="value",
                        variable_name="variableName"
                    ),
                    sns=iotevents.CfnDetectorModel.SnsProperty(
                        target_arn="targetArn",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        )
                    ),
                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                        queue_url="queueUrl",
                
                        # the properties below are optional
                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                            content_expression="contentExpression",
                            type="type"
                        ),
                        use_base64=False
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if clear_timer is not None:
                self._values["clear_timer"] = clear_timer
            if dynamo_db is not None:
                self._values["dynamo_db"] = dynamo_db
            if dynamo_d_bv2 is not None:
                self._values["dynamo_d_bv2"] = dynamo_d_bv2
            if firehose is not None:
                self._values["firehose"] = firehose
            if iot_events is not None:
                self._values["iot_events"] = iot_events
            if iot_site_wise is not None:
                self._values["iot_site_wise"] = iot_site_wise
            if iot_topic_publish is not None:
                self._values["iot_topic_publish"] = iot_topic_publish
            if lambda_ is not None:
                self._values["lambda_"] = lambda_
            if reset_timer is not None:
                self._values["reset_timer"] = reset_timer
            if set_timer is not None:
                self._values["set_timer"] = set_timer
            if set_variable is not None:
                self._values["set_variable"] = set_variable
            if sns is not None:
                self._values["sns"] = sns
            if sqs is not None:
                self._values["sqs"] = sqs

        @builtins.property
        def clear_timer(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.ClearTimerProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.ClearTimer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-cleartimer
            '''
            result = self._values.get("clear_timer")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.ClearTimerProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def dynamo_db(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.DynamoDBProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.DynamoDB``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-dynamodb
            '''
            result = self._values.get("dynamo_db")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.DynamoDBProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def dynamo_d_bv2(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.DynamoDBv2Property", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.DynamoDBv2``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-dynamodbv2
            '''
            result = self._values.get("dynamo_d_bv2")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.DynamoDBv2Property", _IResolvable_da3f097b]], result)

        @builtins.property
        def firehose(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.FirehoseProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.Firehose``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-firehose
            '''
            result = self._values.get("firehose")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.FirehoseProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_events(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.IotEventsProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.IotEvents``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-iotevents
            '''
            result = self._values.get("iot_events")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.IotEventsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_site_wise(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.IotSiteWiseProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.IotSiteWise``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-iotsitewise
            '''
            result = self._values.get("iot_site_wise")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.IotSiteWiseProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_topic_publish(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.IotTopicPublishProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.IotTopicPublish``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-iottopicpublish
            '''
            result = self._values.get("iot_topic_publish")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.IotTopicPublishProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def lambda_(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.LambdaProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.Lambda``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-lambda
            '''
            result = self._values.get("lambda_")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.LambdaProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def reset_timer(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.ResetTimerProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.ResetTimer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-resettimer
            '''
            result = self._values.get("reset_timer")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.ResetTimerProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def set_timer(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.SetTimerProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.SetTimer``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-settimer
            '''
            result = self._values.get("set_timer")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.SetTimerProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def set_variable(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.SetVariableProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.SetVariable``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-setvariable
            '''
            result = self._values.get("set_variable")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.SetVariableProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sns(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.SnsProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.Sns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-sns
            '''
            result = self._values.get("sns")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.SnsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sqs(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.SqsProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.ActionProperty.Sqs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-action.html#cfn-iotevents-detectormodel-action-sqs
            '''
            result = self._values.get("sqs")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.SqsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.AssetPropertyTimestampProperty",
        jsii_struct_bases=[],
        name_mapping={
            "offset_in_nanos": "offsetInNanos",
            "time_in_seconds": "timeInSeconds",
        },
    )
    class AssetPropertyTimestampProperty:
        def __init__(
            self,
            *,
            offset_in_nanos: typing.Optional[builtins.str] = None,
            time_in_seconds: builtins.str,
        ) -> None:
            '''
            :param offset_in_nanos: ``CfnDetectorModel.AssetPropertyTimestampProperty.OffsetInNanos``.
            :param time_in_seconds: ``CfnDetectorModel.AssetPropertyTimestampProperty.TimeInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertytimestamp.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                asset_property_timestamp_property = iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                    time_in_seconds="timeInSeconds",
                
                    # the properties below are optional
                    offset_in_nanos="offsetInNanos"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "time_in_seconds": time_in_seconds,
            }
            if offset_in_nanos is not None:
                self._values["offset_in_nanos"] = offset_in_nanos

        @builtins.property
        def offset_in_nanos(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.AssetPropertyTimestampProperty.OffsetInNanos``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertytimestamp.html#cfn-iotevents-detectormodel-assetpropertytimestamp-offsetinnanos
            '''
            result = self._values.get("offset_in_nanos")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def time_in_seconds(self) -> builtins.str:
            '''``CfnDetectorModel.AssetPropertyTimestampProperty.TimeInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertytimestamp.html#cfn-iotevents-detectormodel-assetpropertytimestamp-timeinseconds
            '''
            result = self._values.get("time_in_seconds")
            assert result is not None, "Required property 'time_in_seconds' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AssetPropertyTimestampProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.AssetPropertyValueProperty",
        jsii_struct_bases=[],
        name_mapping={
            "quality": "quality",
            "timestamp": "timestamp",
            "value": "value",
        },
    )
    class AssetPropertyValueProperty:
        def __init__(
            self,
            *,
            quality: typing.Optional[builtins.str] = None,
            timestamp: typing.Optional[typing.Union["CfnDetectorModel.AssetPropertyTimestampProperty", _IResolvable_da3f097b]] = None,
            value: typing.Union["CfnDetectorModel.AssetPropertyVariantProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param quality: ``CfnDetectorModel.AssetPropertyValueProperty.Quality``.
            :param timestamp: ``CfnDetectorModel.AssetPropertyValueProperty.Timestamp``.
            :param value: ``CfnDetectorModel.AssetPropertyValueProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvalue.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                asset_property_value_property = iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                    value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                        boolean_value="booleanValue",
                        double_value="doubleValue",
                        integer_value="integerValue",
                        string_value="stringValue"
                    ),
                
                    # the properties below are optional
                    quality="quality",
                    timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                        time_in_seconds="timeInSeconds",
                
                        # the properties below are optional
                        offset_in_nanos="offsetInNanos"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "value": value,
            }
            if quality is not None:
                self._values["quality"] = quality
            if timestamp is not None:
                self._values["timestamp"] = timestamp

        @builtins.property
        def quality(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.AssetPropertyValueProperty.Quality``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvalue.html#cfn-iotevents-detectormodel-assetpropertyvalue-quality
            '''
            result = self._values.get("quality")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def timestamp(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.AssetPropertyTimestampProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.AssetPropertyValueProperty.Timestamp``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvalue.html#cfn-iotevents-detectormodel-assetpropertyvalue-timestamp
            '''
            result = self._values.get("timestamp")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.AssetPropertyTimestampProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def value(
            self,
        ) -> typing.Union["CfnDetectorModel.AssetPropertyVariantProperty", _IResolvable_da3f097b]:
            '''``CfnDetectorModel.AssetPropertyValueProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvalue.html#cfn-iotevents-detectormodel-assetpropertyvalue-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(typing.Union["CfnDetectorModel.AssetPropertyVariantProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AssetPropertyValueProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.AssetPropertyVariantProperty",
        jsii_struct_bases=[],
        name_mapping={
            "boolean_value": "booleanValue",
            "double_value": "doubleValue",
            "integer_value": "integerValue",
            "string_value": "stringValue",
        },
    )
    class AssetPropertyVariantProperty:
        def __init__(
            self,
            *,
            boolean_value: typing.Optional[builtins.str] = None,
            double_value: typing.Optional[builtins.str] = None,
            integer_value: typing.Optional[builtins.str] = None,
            string_value: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param boolean_value: ``CfnDetectorModel.AssetPropertyVariantProperty.BooleanValue``.
            :param double_value: ``CfnDetectorModel.AssetPropertyVariantProperty.DoubleValue``.
            :param integer_value: ``CfnDetectorModel.AssetPropertyVariantProperty.IntegerValue``.
            :param string_value: ``CfnDetectorModel.AssetPropertyVariantProperty.StringValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvariant.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                asset_property_variant_property = iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                    boolean_value="booleanValue",
                    double_value="doubleValue",
                    integer_value="integerValue",
                    string_value="stringValue"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if boolean_value is not None:
                self._values["boolean_value"] = boolean_value
            if double_value is not None:
                self._values["double_value"] = double_value
            if integer_value is not None:
                self._values["integer_value"] = integer_value
            if string_value is not None:
                self._values["string_value"] = string_value

        @builtins.property
        def boolean_value(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.AssetPropertyVariantProperty.BooleanValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvariant.html#cfn-iotevents-detectormodel-assetpropertyvariant-booleanvalue
            '''
            result = self._values.get("boolean_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def double_value(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.AssetPropertyVariantProperty.DoubleValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvariant.html#cfn-iotevents-detectormodel-assetpropertyvariant-doublevalue
            '''
            result = self._values.get("double_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def integer_value(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.AssetPropertyVariantProperty.IntegerValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvariant.html#cfn-iotevents-detectormodel-assetpropertyvariant-integervalue
            '''
            result = self._values.get("integer_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def string_value(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.AssetPropertyVariantProperty.StringValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-assetpropertyvariant.html#cfn-iotevents-detectormodel-assetpropertyvariant-stringvalue
            '''
            result = self._values.get("string_value")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AssetPropertyVariantProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.ClearTimerProperty",
        jsii_struct_bases=[],
        name_mapping={"timer_name": "timerName"},
    )
    class ClearTimerProperty:
        def __init__(self, *, timer_name: builtins.str) -> None:
            '''
            :param timer_name: ``CfnDetectorModel.ClearTimerProperty.TimerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-cleartimer.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                clear_timer_property = iotevents.CfnDetectorModel.ClearTimerProperty(
                    timer_name="timerName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "timer_name": timer_name,
            }

        @builtins.property
        def timer_name(self) -> builtins.str:
            '''``CfnDetectorModel.ClearTimerProperty.TimerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-cleartimer.html#cfn-iotevents-detectormodel-cleartimer-timername
            '''
            result = self._values.get("timer_name")
            assert result is not None, "Required property 'timer_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ClearTimerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.DetectorModelDefinitionProperty",
        jsii_struct_bases=[],
        name_mapping={"initial_state_name": "initialStateName", "states": "states"},
    )
    class DetectorModelDefinitionProperty:
        def __init__(
            self,
            *,
            initial_state_name: builtins.str,
            states: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.StateProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param initial_state_name: ``CfnDetectorModel.DetectorModelDefinitionProperty.InitialStateName``.
            :param states: ``CfnDetectorModel.DetectorModelDefinitionProperty.States``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-detectormodeldefinition.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                detector_model_definition_property = iotevents.CfnDetectorModel.DetectorModelDefinitionProperty(
                    initial_state_name="initialStateName",
                    states=[iotevents.CfnDetectorModel.StateProperty(
                        state_name="stateName",
                
                        # the properties below are optional
                        on_enter=iotevents.CfnDetectorModel.OnEnterProperty(
                            events=[iotevents.CfnDetectorModel.EventProperty(
                                event_name="eventName",
                
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
                
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
                
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
                
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
                
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )],
                                condition="condition"
                            )]
                        ),
                        on_exit=iotevents.CfnDetectorModel.OnExitProperty(
                            events=[iotevents.CfnDetectorModel.EventProperty(
                                event_name="eventName",
                
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
                
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
                
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
                
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
                
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )],
                                condition="condition"
                            )]
                        ),
                        on_input=iotevents.CfnDetectorModel.OnInputProperty(
                            events=[iotevents.CfnDetectorModel.EventProperty(
                                event_name="eventName",
                
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
                
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
                
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
                
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
                
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )],
                                condition="condition"
                            )],
                            transition_events=[iotevents.CfnDetectorModel.TransitionEventProperty(
                                condition="condition",
                                event_name="eventName",
                                next_state="nextState",
                
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
                
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
                
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
                
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
                
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
                
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )]
                            )]
                        )
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "initial_state_name": initial_state_name,
                "states": states,
            }

        @builtins.property
        def initial_state_name(self) -> builtins.str:
            '''``CfnDetectorModel.DetectorModelDefinitionProperty.InitialStateName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-detectormodeldefinition.html#cfn-iotevents-detectormodel-detectormodeldefinition-initialstatename
            '''
            result = self._values.get("initial_state_name")
            assert result is not None, "Required property 'initial_state_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def states(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.StateProperty", _IResolvable_da3f097b]]]:
            '''``CfnDetectorModel.DetectorModelDefinitionProperty.States``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-detectormodeldefinition.html#cfn-iotevents-detectormodel-detectormodeldefinition-states
            '''
            result = self._values.get("states")
            assert result is not None, "Required property 'states' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.StateProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DetectorModelDefinitionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.DynamoDBProperty",
        jsii_struct_bases=[],
        name_mapping={
            "hash_key_field": "hashKeyField",
            "hash_key_type": "hashKeyType",
            "hash_key_value": "hashKeyValue",
            "operation": "operation",
            "payload": "payload",
            "payload_field": "payloadField",
            "range_key_field": "rangeKeyField",
            "range_key_type": "rangeKeyType",
            "range_key_value": "rangeKeyValue",
            "table_name": "tableName",
        },
    )
    class DynamoDBProperty:
        def __init__(
            self,
            *,
            hash_key_field: builtins.str,
            hash_key_type: typing.Optional[builtins.str] = None,
            hash_key_value: builtins.str,
            operation: typing.Optional[builtins.str] = None,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
            payload_field: typing.Optional[builtins.str] = None,
            range_key_field: typing.Optional[builtins.str] = None,
            range_key_type: typing.Optional[builtins.str] = None,
            range_key_value: typing.Optional[builtins.str] = None,
            table_name: builtins.str,
        ) -> None:
            '''
            :param hash_key_field: ``CfnDetectorModel.DynamoDBProperty.HashKeyField``.
            :param hash_key_type: ``CfnDetectorModel.DynamoDBProperty.HashKeyType``.
            :param hash_key_value: ``CfnDetectorModel.DynamoDBProperty.HashKeyValue``.
            :param operation: ``CfnDetectorModel.DynamoDBProperty.Operation``.
            :param payload: ``CfnDetectorModel.DynamoDBProperty.Payload``.
            :param payload_field: ``CfnDetectorModel.DynamoDBProperty.PayloadField``.
            :param range_key_field: ``CfnDetectorModel.DynamoDBProperty.RangeKeyField``.
            :param range_key_type: ``CfnDetectorModel.DynamoDBProperty.RangeKeyType``.
            :param range_key_value: ``CfnDetectorModel.DynamoDBProperty.RangeKeyValue``.
            :param table_name: ``CfnDetectorModel.DynamoDBProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                dynamo_dBProperty = iotevents.CfnDetectorModel.DynamoDBProperty(
                    hash_key_field="hashKeyField",
                    hash_key_value="hashKeyValue",
                    table_name="tableName",
                
                    # the properties below are optional
                    hash_key_type="hashKeyType",
                    operation="operation",
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    ),
                    payload_field="payloadField",
                    range_key_field="rangeKeyField",
                    range_key_type="rangeKeyType",
                    range_key_value="rangeKeyValue"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "hash_key_field": hash_key_field,
                "hash_key_value": hash_key_value,
                "table_name": table_name,
            }
            if hash_key_type is not None:
                self._values["hash_key_type"] = hash_key_type
            if operation is not None:
                self._values["operation"] = operation
            if payload is not None:
                self._values["payload"] = payload
            if payload_field is not None:
                self._values["payload_field"] = payload_field
            if range_key_field is not None:
                self._values["range_key_field"] = range_key_field
            if range_key_type is not None:
                self._values["range_key_type"] = range_key_type
            if range_key_value is not None:
                self._values["range_key_value"] = range_key_value

        @builtins.property
        def hash_key_field(self) -> builtins.str:
            '''``CfnDetectorModel.DynamoDBProperty.HashKeyField``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-hashkeyfield
            '''
            result = self._values.get("hash_key_field")
            assert result is not None, "Required property 'hash_key_field' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def hash_key_type(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.DynamoDBProperty.HashKeyType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-hashkeytype
            '''
            result = self._values.get("hash_key_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def hash_key_value(self) -> builtins.str:
            '''``CfnDetectorModel.DynamoDBProperty.HashKeyValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-hashkeyvalue
            '''
            result = self._values.get("hash_key_value")
            assert result is not None, "Required property 'hash_key_value' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def operation(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.DynamoDBProperty.Operation``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-operation
            '''
            result = self._values.get("operation")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.DynamoDBProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def payload_field(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.DynamoDBProperty.PayloadField``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-payloadfield
            '''
            result = self._values.get("payload_field")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def range_key_field(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.DynamoDBProperty.RangeKeyField``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-rangekeyfield
            '''
            result = self._values.get("range_key_field")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def range_key_type(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.DynamoDBProperty.RangeKeyType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-rangekeytype
            '''
            result = self._values.get("range_key_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def range_key_value(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.DynamoDBProperty.RangeKeyValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-rangekeyvalue
            '''
            result = self._values.get("range_key_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def table_name(self) -> builtins.str:
            '''``CfnDetectorModel.DynamoDBProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodb.html#cfn-iotevents-detectormodel-dynamodb-tablename
            '''
            result = self._values.get("table_name")
            assert result is not None, "Required property 'table_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDBProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.DynamoDBv2Property",
        jsii_struct_bases=[],
        name_mapping={"payload": "payload", "table_name": "tableName"},
    )
    class DynamoDBv2Property:
        def __init__(
            self,
            *,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
            table_name: builtins.str,
        ) -> None:
            '''
            :param payload: ``CfnDetectorModel.DynamoDBv2Property.Payload``.
            :param table_name: ``CfnDetectorModel.DynamoDBv2Property.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodbv2.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                dynamo_dBv2_property = iotevents.CfnDetectorModel.DynamoDBv2Property(
                    table_name="tableName",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "table_name": table_name,
            }
            if payload is not None:
                self._values["payload"] = payload

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.DynamoDBv2Property.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodbv2.html#cfn-iotevents-detectormodel-dynamodbv2-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def table_name(self) -> builtins.str:
            '''``CfnDetectorModel.DynamoDBv2Property.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-dynamodbv2.html#cfn-iotevents-detectormodel-dynamodbv2-tablename
            '''
            result = self._values.get("table_name")
            assert result is not None, "Required property 'table_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDBv2Property(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.EventProperty",
        jsii_struct_bases=[],
        name_mapping={
            "actions": "actions",
            "condition": "condition",
            "event_name": "eventName",
        },
    )
    class EventProperty:
        def __init__(
            self,
            *,
            actions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.ActionProperty", _IResolvable_da3f097b]]]] = None,
            condition: typing.Optional[builtins.str] = None,
            event_name: builtins.str,
        ) -> None:
            '''
            :param actions: ``CfnDetectorModel.EventProperty.Actions``.
            :param condition: ``CfnDetectorModel.EventProperty.Condition``.
            :param event_name: ``CfnDetectorModel.EventProperty.EventName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                event_property = iotevents.CfnDetectorModel.EventProperty(
                    event_name="eventName",
                
                    # the properties below are optional
                    actions=[iotevents.CfnDetectorModel.ActionProperty(
                        clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                            timer_name="timerName"
                        ),
                        dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                            hash_key_field="hashKeyField",
                            hash_key_value="hashKeyValue",
                            table_name="tableName",
                
                            # the properties below are optional
                            hash_key_type="hashKeyType",
                            operation="operation",
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            ),
                            payload_field="payloadField",
                            range_key_field="rangeKeyField",
                            range_key_type="rangeKeyType",
                            range_key_value="rangeKeyValue"
                        ),
                        dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                            table_name="tableName",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                            delivery_stream_name="deliveryStreamName",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            ),
                            separator="separator"
                        ),
                        iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                            input_name="inputName",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                            property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                    boolean_value="booleanValue",
                                    double_value="doubleValue",
                                    integer_value="integerValue",
                                    string_value="stringValue"
                                ),
                
                                # the properties below are optional
                                quality="quality",
                                timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                    time_in_seconds="timeInSeconds",
                
                                    # the properties below are optional
                                    offset_in_nanos="offsetInNanos"
                                )
                            ),
                
                            # the properties below are optional
                            asset_id="assetId",
                            entry_id="entryId",
                            property_alias="propertyAlias",
                            property_id="propertyId"
                        ),
                        iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                            mqtt_topic="mqttTopic",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                            function_arn="functionArn",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                            timer_name="timerName"
                        ),
                        set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                            timer_name="timerName",
                
                            # the properties below are optional
                            duration_expression="durationExpression",
                            seconds=123
                        ),
                        set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                            value="value",
                            variable_name="variableName"
                        ),
                        sns=iotevents.CfnDetectorModel.SnsProperty(
                            target_arn="targetArn",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        sqs=iotevents.CfnDetectorModel.SqsProperty(
                            queue_url="queueUrl",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            ),
                            use_base64=False
                        )
                    )],
                    condition="condition"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "event_name": event_name,
            }
            if actions is not None:
                self._values["actions"] = actions
            if condition is not None:
                self._values["condition"] = condition

        @builtins.property
        def actions(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.ActionProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDetectorModel.EventProperty.Actions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html#cfn-iotevents-detectormodel-event-actions
            '''
            result = self._values.get("actions")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.ActionProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def condition(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.EventProperty.Condition``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html#cfn-iotevents-detectormodel-event-condition
            '''
            result = self._values.get("condition")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def event_name(self) -> builtins.str:
            '''``CfnDetectorModel.EventProperty.EventName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-event.html#cfn-iotevents-detectormodel-event-eventname
            '''
            result = self._values.get("event_name")
            assert result is not None, "Required property 'event_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EventProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.FirehoseProperty",
        jsii_struct_bases=[],
        name_mapping={
            "delivery_stream_name": "deliveryStreamName",
            "payload": "payload",
            "separator": "separator",
        },
    )
    class FirehoseProperty:
        def __init__(
            self,
            *,
            delivery_stream_name: builtins.str,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
            separator: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param delivery_stream_name: ``CfnDetectorModel.FirehoseProperty.DeliveryStreamName``.
            :param payload: ``CfnDetectorModel.FirehoseProperty.Payload``.
            :param separator: ``CfnDetectorModel.FirehoseProperty.Separator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                firehose_property = iotevents.CfnDetectorModel.FirehoseProperty(
                    delivery_stream_name="deliveryStreamName",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    ),
                    separator="separator"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "delivery_stream_name": delivery_stream_name,
            }
            if payload is not None:
                self._values["payload"] = payload
            if separator is not None:
                self._values["separator"] = separator

        @builtins.property
        def delivery_stream_name(self) -> builtins.str:
            '''``CfnDetectorModel.FirehoseProperty.DeliveryStreamName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html#cfn-iotevents-detectormodel-firehose-deliverystreamname
            '''
            result = self._values.get("delivery_stream_name")
            assert result is not None, "Required property 'delivery_stream_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.FirehoseProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html#cfn-iotevents-detectormodel-firehose-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def separator(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.FirehoseProperty.Separator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-firehose.html#cfn-iotevents-detectormodel-firehose-separator
            '''
            result = self._values.get("separator")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FirehoseProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.IotEventsProperty",
        jsii_struct_bases=[],
        name_mapping={"input_name": "inputName", "payload": "payload"},
    )
    class IotEventsProperty:
        def __init__(
            self,
            *,
            input_name: builtins.str,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param input_name: ``CfnDetectorModel.IotEventsProperty.InputName``.
            :param payload: ``CfnDetectorModel.IotEventsProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotevents.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                iot_events_property = iotevents.CfnDetectorModel.IotEventsProperty(
                    input_name="inputName",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "input_name": input_name,
            }
            if payload is not None:
                self._values["payload"] = payload

        @builtins.property
        def input_name(self) -> builtins.str:
            '''``CfnDetectorModel.IotEventsProperty.InputName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotevents.html#cfn-iotevents-detectormodel-iotevents-inputname
            '''
            result = self._values.get("input_name")
            assert result is not None, "Required property 'input_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.IotEventsProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotevents.html#cfn-iotevents-detectormodel-iotevents-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IotEventsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.IotSiteWiseProperty",
        jsii_struct_bases=[],
        name_mapping={
            "asset_id": "assetId",
            "entry_id": "entryId",
            "property_alias": "propertyAlias",
            "property_id": "propertyId",
            "property_value": "propertyValue",
        },
    )
    class IotSiteWiseProperty:
        def __init__(
            self,
            *,
            asset_id: typing.Optional[builtins.str] = None,
            entry_id: typing.Optional[builtins.str] = None,
            property_alias: typing.Optional[builtins.str] = None,
            property_id: typing.Optional[builtins.str] = None,
            property_value: typing.Union["CfnDetectorModel.AssetPropertyValueProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param asset_id: ``CfnDetectorModel.IotSiteWiseProperty.AssetId``.
            :param entry_id: ``CfnDetectorModel.IotSiteWiseProperty.EntryId``.
            :param property_alias: ``CfnDetectorModel.IotSiteWiseProperty.PropertyAlias``.
            :param property_id: ``CfnDetectorModel.IotSiteWiseProperty.PropertyId``.
            :param property_value: ``CfnDetectorModel.IotSiteWiseProperty.PropertyValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotsitewise.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                iot_site_wise_property = iotevents.CfnDetectorModel.IotSiteWiseProperty(
                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                            boolean_value="booleanValue",
                            double_value="doubleValue",
                            integer_value="integerValue",
                            string_value="stringValue"
                        ),
                
                        # the properties below are optional
                        quality="quality",
                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                            time_in_seconds="timeInSeconds",
                
                            # the properties below are optional
                            offset_in_nanos="offsetInNanos"
                        )
                    ),
                
                    # the properties below are optional
                    asset_id="assetId",
                    entry_id="entryId",
                    property_alias="propertyAlias",
                    property_id="propertyId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "property_value": property_value,
            }
            if asset_id is not None:
                self._values["asset_id"] = asset_id
            if entry_id is not None:
                self._values["entry_id"] = entry_id
            if property_alias is not None:
                self._values["property_alias"] = property_alias
            if property_id is not None:
                self._values["property_id"] = property_id

        @builtins.property
        def asset_id(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.IotSiteWiseProperty.AssetId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotsitewise.html#cfn-iotevents-detectormodel-iotsitewise-assetid
            '''
            result = self._values.get("asset_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def entry_id(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.IotSiteWiseProperty.EntryId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotsitewise.html#cfn-iotevents-detectormodel-iotsitewise-entryid
            '''
            result = self._values.get("entry_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def property_alias(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.IotSiteWiseProperty.PropertyAlias``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotsitewise.html#cfn-iotevents-detectormodel-iotsitewise-propertyalias
            '''
            result = self._values.get("property_alias")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def property_id(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.IotSiteWiseProperty.PropertyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotsitewise.html#cfn-iotevents-detectormodel-iotsitewise-propertyid
            '''
            result = self._values.get("property_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def property_value(
            self,
        ) -> typing.Union["CfnDetectorModel.AssetPropertyValueProperty", _IResolvable_da3f097b]:
            '''``CfnDetectorModel.IotSiteWiseProperty.PropertyValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iotsitewise.html#cfn-iotevents-detectormodel-iotsitewise-propertyvalue
            '''
            result = self._values.get("property_value")
            assert result is not None, "Required property 'property_value' is missing"
            return typing.cast(typing.Union["CfnDetectorModel.AssetPropertyValueProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IotSiteWiseProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.IotTopicPublishProperty",
        jsii_struct_bases=[],
        name_mapping={"mqtt_topic": "mqttTopic", "payload": "payload"},
    )
    class IotTopicPublishProperty:
        def __init__(
            self,
            *,
            mqtt_topic: builtins.str,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param mqtt_topic: ``CfnDetectorModel.IotTopicPublishProperty.MqttTopic``.
            :param payload: ``CfnDetectorModel.IotTopicPublishProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iottopicpublish.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                iot_topic_publish_property = iotevents.CfnDetectorModel.IotTopicPublishProperty(
                    mqtt_topic="mqttTopic",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "mqtt_topic": mqtt_topic,
            }
            if payload is not None:
                self._values["payload"] = payload

        @builtins.property
        def mqtt_topic(self) -> builtins.str:
            '''``CfnDetectorModel.IotTopicPublishProperty.MqttTopic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iottopicpublish.html#cfn-iotevents-detectormodel-iottopicpublish-mqtttopic
            '''
            result = self._values.get("mqtt_topic")
            assert result is not None, "Required property 'mqtt_topic' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.IotTopicPublishProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-iottopicpublish.html#cfn-iotevents-detectormodel-iottopicpublish-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IotTopicPublishProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.LambdaProperty",
        jsii_struct_bases=[],
        name_mapping={"function_arn": "functionArn", "payload": "payload"},
    )
    class LambdaProperty:
        def __init__(
            self,
            *,
            function_arn: builtins.str,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param function_arn: ``CfnDetectorModel.LambdaProperty.FunctionArn``.
            :param payload: ``CfnDetectorModel.LambdaProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-lambda.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                lambda_property = iotevents.CfnDetectorModel.LambdaProperty(
                    function_arn="functionArn",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "function_arn": function_arn,
            }
            if payload is not None:
                self._values["payload"] = payload

        @builtins.property
        def function_arn(self) -> builtins.str:
            '''``CfnDetectorModel.LambdaProperty.FunctionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-lambda.html#cfn-iotevents-detectormodel-lambda-functionarn
            '''
            result = self._values.get("function_arn")
            assert result is not None, "Required property 'function_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.LambdaProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-lambda.html#cfn-iotevents-detectormodel-lambda-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LambdaProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.OnEnterProperty",
        jsii_struct_bases=[],
        name_mapping={"events": "events"},
    )
    class OnEnterProperty:
        def __init__(
            self,
            *,
            events: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param events: ``CfnDetectorModel.OnEnterProperty.Events``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onenter.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                on_enter_property = iotevents.CfnDetectorModel.OnEnterProperty(
                    events=[iotevents.CfnDetectorModel.EventProperty(
                        event_name="eventName",
                
                        # the properties below are optional
                        actions=[iotevents.CfnDetectorModel.ActionProperty(
                            clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                timer_name="timerName"
                            ),
                            dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                hash_key_field="hashKeyField",
                                hash_key_value="hashKeyValue",
                                table_name="tableName",
                
                                # the properties below are optional
                                hash_key_type="hashKeyType",
                                operation="operation",
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                payload_field="payloadField",
                                range_key_field="rangeKeyField",
                                range_key_type="rangeKeyType",
                                range_key_value="rangeKeyValue"
                            ),
                            dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                table_name="tableName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                delivery_stream_name="deliveryStreamName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                separator="separator"
                            ),
                            iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                input_name="inputName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                    value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
                
                                    # the properties below are optional
                                    quality="quality",
                                    timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
                
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    )
                                ),
                
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            ),
                            iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                mqtt_topic="mqttTopic",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                function_arn="functionArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                timer_name="timerName"
                            ),
                            set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                timer_name="timerName",
                
                                # the properties below are optional
                                duration_expression="durationExpression",
                                seconds=123
                            ),
                            set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                value="value",
                                variable_name="variableName"
                            ),
                            sns=iotevents.CfnDetectorModel.SnsProperty(
                                target_arn="targetArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            sqs=iotevents.CfnDetectorModel.SqsProperty(
                                queue_url="queueUrl",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                use_base64=False
                            )
                        )],
                        condition="condition"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if events is not None:
                self._values["events"] = events

        @builtins.property
        def events(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDetectorModel.OnEnterProperty.Events``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onenter.html#cfn-iotevents-detectormodel-onenter-events
            '''
            result = self._values.get("events")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OnEnterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.OnExitProperty",
        jsii_struct_bases=[],
        name_mapping={"events": "events"},
    )
    class OnExitProperty:
        def __init__(
            self,
            *,
            events: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param events: ``CfnDetectorModel.OnExitProperty.Events``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onexit.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                on_exit_property = iotevents.CfnDetectorModel.OnExitProperty(
                    events=[iotevents.CfnDetectorModel.EventProperty(
                        event_name="eventName",
                
                        # the properties below are optional
                        actions=[iotevents.CfnDetectorModel.ActionProperty(
                            clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                timer_name="timerName"
                            ),
                            dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                hash_key_field="hashKeyField",
                                hash_key_value="hashKeyValue",
                                table_name="tableName",
                
                                # the properties below are optional
                                hash_key_type="hashKeyType",
                                operation="operation",
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                payload_field="payloadField",
                                range_key_field="rangeKeyField",
                                range_key_type="rangeKeyType",
                                range_key_value="rangeKeyValue"
                            ),
                            dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                table_name="tableName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                delivery_stream_name="deliveryStreamName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                separator="separator"
                            ),
                            iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                input_name="inputName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                    value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
                
                                    # the properties below are optional
                                    quality="quality",
                                    timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
                
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    )
                                ),
                
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            ),
                            iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                mqtt_topic="mqttTopic",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                function_arn="functionArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                timer_name="timerName"
                            ),
                            set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                timer_name="timerName",
                
                                # the properties below are optional
                                duration_expression="durationExpression",
                                seconds=123
                            ),
                            set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                value="value",
                                variable_name="variableName"
                            ),
                            sns=iotevents.CfnDetectorModel.SnsProperty(
                                target_arn="targetArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            sqs=iotevents.CfnDetectorModel.SqsProperty(
                                queue_url="queueUrl",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                use_base64=False
                            )
                        )],
                        condition="condition"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if events is not None:
                self._values["events"] = events

        @builtins.property
        def events(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDetectorModel.OnExitProperty.Events``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-onexit.html#cfn-iotevents-detectormodel-onexit-events
            '''
            result = self._values.get("events")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OnExitProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.OnInputProperty",
        jsii_struct_bases=[],
        name_mapping={"events": "events", "transition_events": "transitionEvents"},
    )
    class OnInputProperty:
        def __init__(
            self,
            *,
            events: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]] = None,
            transition_events: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.TransitionEventProperty", _IResolvable_da3f097b]]]] = None,
        ) -> None:
            '''
            :param events: ``CfnDetectorModel.OnInputProperty.Events``.
            :param transition_events: ``CfnDetectorModel.OnInputProperty.TransitionEvents``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-oninput.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                on_input_property = iotevents.CfnDetectorModel.OnInputProperty(
                    events=[iotevents.CfnDetectorModel.EventProperty(
                        event_name="eventName",
                
                        # the properties below are optional
                        actions=[iotevents.CfnDetectorModel.ActionProperty(
                            clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                timer_name="timerName"
                            ),
                            dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                hash_key_field="hashKeyField",
                                hash_key_value="hashKeyValue",
                                table_name="tableName",
                
                                # the properties below are optional
                                hash_key_type="hashKeyType",
                                operation="operation",
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                payload_field="payloadField",
                                range_key_field="rangeKeyField",
                                range_key_type="rangeKeyType",
                                range_key_value="rangeKeyValue"
                            ),
                            dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                table_name="tableName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                delivery_stream_name="deliveryStreamName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                separator="separator"
                            ),
                            iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                input_name="inputName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                    value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
                
                                    # the properties below are optional
                                    quality="quality",
                                    timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
                
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    )
                                ),
                
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            ),
                            iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                mqtt_topic="mqttTopic",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                function_arn="functionArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                timer_name="timerName"
                            ),
                            set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                timer_name="timerName",
                
                                # the properties below are optional
                                duration_expression="durationExpression",
                                seconds=123
                            ),
                            set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                value="value",
                                variable_name="variableName"
                            ),
                            sns=iotevents.CfnDetectorModel.SnsProperty(
                                target_arn="targetArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            sqs=iotevents.CfnDetectorModel.SqsProperty(
                                queue_url="queueUrl",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                use_base64=False
                            )
                        )],
                        condition="condition"
                    )],
                    transition_events=[iotevents.CfnDetectorModel.TransitionEventProperty(
                        condition="condition",
                        event_name="eventName",
                        next_state="nextState",
                
                        # the properties below are optional
                        actions=[iotevents.CfnDetectorModel.ActionProperty(
                            clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                timer_name="timerName"
                            ),
                            dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                hash_key_field="hashKeyField",
                                hash_key_value="hashKeyValue",
                                table_name="tableName",
                
                                # the properties below are optional
                                hash_key_type="hashKeyType",
                                operation="operation",
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                payload_field="payloadField",
                                range_key_field="rangeKeyField",
                                range_key_type="rangeKeyType",
                                range_key_value="rangeKeyValue"
                            ),
                            dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                table_name="tableName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                delivery_stream_name="deliveryStreamName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                separator="separator"
                            ),
                            iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                input_name="inputName",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                    value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
                
                                    # the properties below are optional
                                    quality="quality",
                                    timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
                
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    )
                                ),
                
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            ),
                            iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                mqtt_topic="mqttTopic",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                function_arn="functionArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                timer_name="timerName"
                            ),
                            set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                timer_name="timerName",
                
                                # the properties below are optional
                                duration_expression="durationExpression",
                                seconds=123
                            ),
                            set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                value="value",
                                variable_name="variableName"
                            ),
                            sns=iotevents.CfnDetectorModel.SnsProperty(
                                target_arn="targetArn",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                )
                            ),
                            sqs=iotevents.CfnDetectorModel.SqsProperty(
                                queue_url="queueUrl",
                
                                # the properties below are optional
                                payload=iotevents.CfnDetectorModel.PayloadProperty(
                                    content_expression="contentExpression",
                                    type="type"
                                ),
                                use_base64=False
                            )
                        )]
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if events is not None:
                self._values["events"] = events
            if transition_events is not None:
                self._values["transition_events"] = transition_events

        @builtins.property
        def events(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDetectorModel.OnInputProperty.Events``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-oninput.html#cfn-iotevents-detectormodel-oninput-events
            '''
            result = self._values.get("events")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.EventProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def transition_events(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.TransitionEventProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDetectorModel.OnInputProperty.TransitionEvents``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-oninput.html#cfn-iotevents-detectormodel-oninput-transitionevents
            '''
            result = self._values.get("transition_events")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.TransitionEventProperty", _IResolvable_da3f097b]]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OnInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.PayloadProperty",
        jsii_struct_bases=[],
        name_mapping={"content_expression": "contentExpression", "type": "type"},
    )
    class PayloadProperty:
        def __init__(
            self,
            *,
            content_expression: builtins.str,
            type: builtins.str,
        ) -> None:
            '''
            :param content_expression: ``CfnDetectorModel.PayloadProperty.ContentExpression``.
            :param type: ``CfnDetectorModel.PayloadProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-payload.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                payload_property = iotevents.CfnDetectorModel.PayloadProperty(
                    content_expression="contentExpression",
                    type="type"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "content_expression": content_expression,
                "type": type,
            }

        @builtins.property
        def content_expression(self) -> builtins.str:
            '''``CfnDetectorModel.PayloadProperty.ContentExpression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-payload.html#cfn-iotevents-detectormodel-payload-contentexpression
            '''
            result = self._values.get("content_expression")
            assert result is not None, "Required property 'content_expression' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnDetectorModel.PayloadProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-payload.html#cfn-iotevents-detectormodel-payload-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PayloadProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.ResetTimerProperty",
        jsii_struct_bases=[],
        name_mapping={"timer_name": "timerName"},
    )
    class ResetTimerProperty:
        def __init__(self, *, timer_name: builtins.str) -> None:
            '''
            :param timer_name: ``CfnDetectorModel.ResetTimerProperty.TimerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-resettimer.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                reset_timer_property = iotevents.CfnDetectorModel.ResetTimerProperty(
                    timer_name="timerName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "timer_name": timer_name,
            }

        @builtins.property
        def timer_name(self) -> builtins.str:
            '''``CfnDetectorModel.ResetTimerProperty.TimerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-resettimer.html#cfn-iotevents-detectormodel-resettimer-timername
            '''
            result = self._values.get("timer_name")
            assert result is not None, "Required property 'timer_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResetTimerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.SetTimerProperty",
        jsii_struct_bases=[],
        name_mapping={
            "duration_expression": "durationExpression",
            "seconds": "seconds",
            "timer_name": "timerName",
        },
    )
    class SetTimerProperty:
        def __init__(
            self,
            *,
            duration_expression: typing.Optional[builtins.str] = None,
            seconds: typing.Optional[jsii.Number] = None,
            timer_name: builtins.str,
        ) -> None:
            '''
            :param duration_expression: ``CfnDetectorModel.SetTimerProperty.DurationExpression``.
            :param seconds: ``CfnDetectorModel.SetTimerProperty.Seconds``.
            :param timer_name: ``CfnDetectorModel.SetTimerProperty.TimerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                set_timer_property = iotevents.CfnDetectorModel.SetTimerProperty(
                    timer_name="timerName",
                
                    # the properties below are optional
                    duration_expression="durationExpression",
                    seconds=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "timer_name": timer_name,
            }
            if duration_expression is not None:
                self._values["duration_expression"] = duration_expression
            if seconds is not None:
                self._values["seconds"] = seconds

        @builtins.property
        def duration_expression(self) -> typing.Optional[builtins.str]:
            '''``CfnDetectorModel.SetTimerProperty.DurationExpression``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html#cfn-iotevents-detectormodel-settimer-durationexpression
            '''
            result = self._values.get("duration_expression")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnDetectorModel.SetTimerProperty.Seconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html#cfn-iotevents-detectormodel-settimer-seconds
            '''
            result = self._values.get("seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def timer_name(self) -> builtins.str:
            '''``CfnDetectorModel.SetTimerProperty.TimerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-settimer.html#cfn-iotevents-detectormodel-settimer-timername
            '''
            result = self._values.get("timer_name")
            assert result is not None, "Required property 'timer_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SetTimerProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.SetVariableProperty",
        jsii_struct_bases=[],
        name_mapping={"value": "value", "variable_name": "variableName"},
    )
    class SetVariableProperty:
        def __init__(self, *, value: builtins.str, variable_name: builtins.str) -> None:
            '''
            :param value: ``CfnDetectorModel.SetVariableProperty.Value``.
            :param variable_name: ``CfnDetectorModel.SetVariableProperty.VariableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-setvariable.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                set_variable_property = iotevents.CfnDetectorModel.SetVariableProperty(
                    value="value",
                    variable_name="variableName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "value": value,
                "variable_name": variable_name,
            }

        @builtins.property
        def value(self) -> builtins.str:
            '''``CfnDetectorModel.SetVariableProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-setvariable.html#cfn-iotevents-detectormodel-setvariable-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def variable_name(self) -> builtins.str:
            '''``CfnDetectorModel.SetVariableProperty.VariableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-setvariable.html#cfn-iotevents-detectormodel-setvariable-variablename
            '''
            result = self._values.get("variable_name")
            assert result is not None, "Required property 'variable_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SetVariableProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.SnsProperty",
        jsii_struct_bases=[],
        name_mapping={"payload": "payload", "target_arn": "targetArn"},
    )
    class SnsProperty:
        def __init__(
            self,
            *,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
            target_arn: builtins.str,
        ) -> None:
            '''
            :param payload: ``CfnDetectorModel.SnsProperty.Payload``.
            :param target_arn: ``CfnDetectorModel.SnsProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sns.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                sns_property = iotevents.CfnDetectorModel.SnsProperty(
                    target_arn="targetArn",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "target_arn": target_arn,
            }
            if payload is not None:
                self._values["payload"] = payload

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.SnsProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sns.html#cfn-iotevents-detectormodel-sns-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def target_arn(self) -> builtins.str:
            '''``CfnDetectorModel.SnsProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sns.html#cfn-iotevents-detectormodel-sns-targetarn
            '''
            result = self._values.get("target_arn")
            assert result is not None, "Required property 'target_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SnsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.SqsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "payload": "payload",
            "queue_url": "queueUrl",
            "use_base64": "useBase64",
        },
    )
    class SqsProperty:
        def __init__(
            self,
            *,
            payload: typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]] = None,
            queue_url: builtins.str,
            use_base64: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param payload: ``CfnDetectorModel.SqsProperty.Payload``.
            :param queue_url: ``CfnDetectorModel.SqsProperty.QueueUrl``.
            :param use_base64: ``CfnDetectorModel.SqsProperty.UseBase64``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                sqs_property = iotevents.CfnDetectorModel.SqsProperty(
                    queue_url="queueUrl",
                
                    # the properties below are optional
                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                        content_expression="contentExpression",
                        type="type"
                    ),
                    use_base64=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "queue_url": queue_url,
            }
            if payload is not None:
                self._values["payload"] = payload
            if use_base64 is not None:
                self._values["use_base64"] = use_base64

        @builtins.property
        def payload(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.SqsProperty.Payload``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html#cfn-iotevents-detectormodel-sqs-payload
            '''
            result = self._values.get("payload")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.PayloadProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def queue_url(self) -> builtins.str:
            '''``CfnDetectorModel.SqsProperty.QueueUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html#cfn-iotevents-detectormodel-sqs-queueurl
            '''
            result = self._values.get("queue_url")
            assert result is not None, "Required property 'queue_url' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def use_base64(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.SqsProperty.UseBase64``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-sqs.html#cfn-iotevents-detectormodel-sqs-usebase64
            '''
            result = self._values.get("use_base64")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SqsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.StateProperty",
        jsii_struct_bases=[],
        name_mapping={
            "on_enter": "onEnter",
            "on_exit": "onExit",
            "on_input": "onInput",
            "state_name": "stateName",
        },
    )
    class StateProperty:
        def __init__(
            self,
            *,
            on_enter: typing.Optional[typing.Union["CfnDetectorModel.OnEnterProperty", _IResolvable_da3f097b]] = None,
            on_exit: typing.Optional[typing.Union["CfnDetectorModel.OnExitProperty", _IResolvable_da3f097b]] = None,
            on_input: typing.Optional[typing.Union["CfnDetectorModel.OnInputProperty", _IResolvable_da3f097b]] = None,
            state_name: builtins.str,
        ) -> None:
            '''
            :param on_enter: ``CfnDetectorModel.StateProperty.OnEnter``.
            :param on_exit: ``CfnDetectorModel.StateProperty.OnExit``.
            :param on_input: ``CfnDetectorModel.StateProperty.OnInput``.
            :param state_name: ``CfnDetectorModel.StateProperty.StateName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                state_property = iotevents.CfnDetectorModel.StateProperty(
                    state_name="stateName",
                
                    # the properties below are optional
                    on_enter=iotevents.CfnDetectorModel.OnEnterProperty(
                        events=[iotevents.CfnDetectorModel.EventProperty(
                            event_name="eventName",
                
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
                
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
                
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
                
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
                
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )],
                            condition="condition"
                        )]
                    ),
                    on_exit=iotevents.CfnDetectorModel.OnExitProperty(
                        events=[iotevents.CfnDetectorModel.EventProperty(
                            event_name="eventName",
                
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
                
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
                
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
                
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
                
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )],
                            condition="condition"
                        )]
                    ),
                    on_input=iotevents.CfnDetectorModel.OnInputProperty(
                        events=[iotevents.CfnDetectorModel.EventProperty(
                            event_name="eventName",
                
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
                
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
                
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
                
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
                
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )],
                            condition="condition"
                        )],
                        transition_events=[iotevents.CfnDetectorModel.TransitionEventProperty(
                            condition="condition",
                            event_name="eventName",
                            next_state="nextState",
                
                            # the properties below are optional
                            actions=[iotevents.CfnDetectorModel.ActionProperty(
                                clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                    timer_name="timerName"
                                ),
                                dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                    hash_key_field="hashKeyField",
                                    hash_key_value="hashKeyValue",
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    hash_key_type="hashKeyType",
                                    operation="operation",
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    payload_field="payloadField",
                                    range_key_field="rangeKeyField",
                                    range_key_type="rangeKeyType",
                                    range_key_value="rangeKeyValue"
                                ),
                                dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                    table_name="tableName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                    delivery_stream_name="deliveryStreamName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    separator="separator"
                                ),
                                iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                    input_name="inputName",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                    property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                        value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                            boolean_value="booleanValue",
                                            double_value="doubleValue",
                                            integer_value="integerValue",
                                            string_value="stringValue"
                                        ),
                
                                        # the properties below are optional
                                        quality="quality",
                                        timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                            time_in_seconds="timeInSeconds",
                
                                            # the properties below are optional
                                            offset_in_nanos="offsetInNanos"
                                        )
                                    ),
                
                                    # the properties below are optional
                                    asset_id="assetId",
                                    entry_id="entryId",
                                    property_alias="propertyAlias",
                                    property_id="propertyId"
                                ),
                                iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                    mqtt_topic="mqttTopic",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                    function_arn="functionArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                    timer_name="timerName"
                                ),
                                set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                    timer_name="timerName",
                
                                    # the properties below are optional
                                    duration_expression="durationExpression",
                                    seconds=123
                                ),
                                set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                    value="value",
                                    variable_name="variableName"
                                ),
                                sns=iotevents.CfnDetectorModel.SnsProperty(
                                    target_arn="targetArn",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    )
                                ),
                                sqs=iotevents.CfnDetectorModel.SqsProperty(
                                    queue_url="queueUrl",
                
                                    # the properties below are optional
                                    payload=iotevents.CfnDetectorModel.PayloadProperty(
                                        content_expression="contentExpression",
                                        type="type"
                                    ),
                                    use_base64=False
                                )
                            )]
                        )]
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "state_name": state_name,
            }
            if on_enter is not None:
                self._values["on_enter"] = on_enter
            if on_exit is not None:
                self._values["on_exit"] = on_exit
            if on_input is not None:
                self._values["on_input"] = on_input

        @builtins.property
        def on_enter(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.OnEnterProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.StateProperty.OnEnter``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-onenter
            '''
            result = self._values.get("on_enter")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.OnEnterProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def on_exit(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.OnExitProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.StateProperty.OnExit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-onexit
            '''
            result = self._values.get("on_exit")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.OnExitProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def on_input(
            self,
        ) -> typing.Optional[typing.Union["CfnDetectorModel.OnInputProperty", _IResolvable_da3f097b]]:
            '''``CfnDetectorModel.StateProperty.OnInput``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-oninput
            '''
            result = self._values.get("on_input")
            return typing.cast(typing.Optional[typing.Union["CfnDetectorModel.OnInputProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def state_name(self) -> builtins.str:
            '''``CfnDetectorModel.StateProperty.StateName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-state.html#cfn-iotevents-detectormodel-state-statename
            '''
            result = self._values.get("state_name")
            assert result is not None, "Required property 'state_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StateProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModel.TransitionEventProperty",
        jsii_struct_bases=[],
        name_mapping={
            "actions": "actions",
            "condition": "condition",
            "event_name": "eventName",
            "next_state": "nextState",
        },
    )
    class TransitionEventProperty:
        def __init__(
            self,
            *,
            actions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnDetectorModel.ActionProperty", _IResolvable_da3f097b]]]] = None,
            condition: builtins.str,
            event_name: builtins.str,
            next_state: builtins.str,
        ) -> None:
            '''
            :param actions: ``CfnDetectorModel.TransitionEventProperty.Actions``.
            :param condition: ``CfnDetectorModel.TransitionEventProperty.Condition``.
            :param event_name: ``CfnDetectorModel.TransitionEventProperty.EventName``.
            :param next_state: ``CfnDetectorModel.TransitionEventProperty.NextState``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                transition_event_property = iotevents.CfnDetectorModel.TransitionEventProperty(
                    condition="condition",
                    event_name="eventName",
                    next_state="nextState",
                
                    # the properties below are optional
                    actions=[iotevents.CfnDetectorModel.ActionProperty(
                        clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                            timer_name="timerName"
                        ),
                        dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                            hash_key_field="hashKeyField",
                            hash_key_value="hashKeyValue",
                            table_name="tableName",
                
                            # the properties below are optional
                            hash_key_type="hashKeyType",
                            operation="operation",
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            ),
                            payload_field="payloadField",
                            range_key_field="rangeKeyField",
                            range_key_type="rangeKeyType",
                            range_key_value="rangeKeyValue"
                        ),
                        dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                            table_name="tableName",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                            delivery_stream_name="deliveryStreamName",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            ),
                            separator="separator"
                        ),
                        iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                            input_name="inputName",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                            property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                    boolean_value="booleanValue",
                                    double_value="doubleValue",
                                    integer_value="integerValue",
                                    string_value="stringValue"
                                ),
                
                                # the properties below are optional
                                quality="quality",
                                timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                    time_in_seconds="timeInSeconds",
                
                                    # the properties below are optional
                                    offset_in_nanos="offsetInNanos"
                                )
                            ),
                
                            # the properties below are optional
                            asset_id="assetId",
                            entry_id="entryId",
                            property_alias="propertyAlias",
                            property_id="propertyId"
                        ),
                        iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                            mqtt_topic="mqttTopic",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                            function_arn="functionArn",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                            timer_name="timerName"
                        ),
                        set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                            timer_name="timerName",
                
                            # the properties below are optional
                            duration_expression="durationExpression",
                            seconds=123
                        ),
                        set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                            value="value",
                            variable_name="variableName"
                        ),
                        sns=iotevents.CfnDetectorModel.SnsProperty(
                            target_arn="targetArn",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            )
                        ),
                        sqs=iotevents.CfnDetectorModel.SqsProperty(
                            queue_url="queueUrl",
                
                            # the properties below are optional
                            payload=iotevents.CfnDetectorModel.PayloadProperty(
                                content_expression="contentExpression",
                                type="type"
                            ),
                            use_base64=False
                        )
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "condition": condition,
                "event_name": event_name,
                "next_state": next_state,
            }
            if actions is not None:
                self._values["actions"] = actions

        @builtins.property
        def actions(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.ActionProperty", _IResolvable_da3f097b]]]]:
            '''``CfnDetectorModel.TransitionEventProperty.Actions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-actions
            '''
            result = self._values.get("actions")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnDetectorModel.ActionProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def condition(self) -> builtins.str:
            '''``CfnDetectorModel.TransitionEventProperty.Condition``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-condition
            '''
            result = self._values.get("condition")
            assert result is not None, "Required property 'condition' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def event_name(self) -> builtins.str:
            '''``CfnDetectorModel.TransitionEventProperty.EventName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-eventname
            '''
            result = self._values.get("event_name")
            assert result is not None, "Required property 'event_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def next_state(self) -> builtins.str:
            '''``CfnDetectorModel.TransitionEventProperty.NextState``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-detectormodel-transitionevent.html#cfn-iotevents-detectormodel-transitionevent-nextstate
            '''
            result = self._values.get("next_state")
            assert result is not None, "Required property 'next_state' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TransitionEventProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iotevents.CfnDetectorModelProps",
    jsii_struct_bases=[],
    name_mapping={
        "detector_model_definition": "detectorModelDefinition",
        "detector_model_description": "detectorModelDescription",
        "detector_model_name": "detectorModelName",
        "evaluation_method": "evaluationMethod",
        "key": "key",
        "role_arn": "roleArn",
        "tags": "tags",
    },
)
class CfnDetectorModelProps:
    def __init__(
        self,
        *,
        detector_model_definition: typing.Union[CfnDetectorModel.DetectorModelDefinitionProperty, _IResolvable_da3f097b],
        detector_model_description: typing.Optional[builtins.str] = None,
        detector_model_name: typing.Optional[builtins.str] = None,
        evaluation_method: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        role_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoTEvents::DetectorModel``.

        :param detector_model_definition: ``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.
        :param detector_model_description: ``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.
        :param detector_model_name: ``AWS::IoTEvents::DetectorModel.DetectorModelName``.
        :param evaluation_method: ``AWS::IoTEvents::DetectorModel.EvaluationMethod``.
        :param key: ``AWS::IoTEvents::DetectorModel.Key``.
        :param role_arn: ``AWS::IoTEvents::DetectorModel.RoleArn``.
        :param tags: ``AWS::IoTEvents::DetectorModel.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iotevents as iotevents
            
            cfn_detector_model_props = iotevents.CfnDetectorModelProps(
                detector_model_definition=iotevents.CfnDetectorModel.DetectorModelDefinitionProperty(
                    initial_state_name="initialStateName",
                    states=[iotevents.CfnDetectorModel.StateProperty(
                        state_name="stateName",
            
                        # the properties below are optional
                        on_enter=iotevents.CfnDetectorModel.OnEnterProperty(
                            events=[iotevents.CfnDetectorModel.EventProperty(
                                event_name="eventName",
            
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
            
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
            
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
            
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
            
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )],
                                condition="condition"
                            )]
                        ),
                        on_exit=iotevents.CfnDetectorModel.OnExitProperty(
                            events=[iotevents.CfnDetectorModel.EventProperty(
                                event_name="eventName",
            
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
            
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
            
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
            
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
            
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )],
                                condition="condition"
                            )]
                        ),
                        on_input=iotevents.CfnDetectorModel.OnInputProperty(
                            events=[iotevents.CfnDetectorModel.EventProperty(
                                event_name="eventName",
            
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
            
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
            
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
            
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
            
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )],
                                condition="condition"
                            )],
                            transition_events=[iotevents.CfnDetectorModel.TransitionEventProperty(
                                condition="condition",
                                event_name="eventName",
                                next_state="nextState",
            
                                # the properties below are optional
                                actions=[iotevents.CfnDetectorModel.ActionProperty(
                                    clear_timer=iotevents.CfnDetectorModel.ClearTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    dynamo_db=iotevents.CfnDetectorModel.DynamoDBProperty(
                                        hash_key_field="hashKeyField",
                                        hash_key_value="hashKeyValue",
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        hash_key_type="hashKeyType",
                                        operation="operation",
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        payload_field="payloadField",
                                        range_key_field="rangeKeyField",
                                        range_key_type="rangeKeyType",
                                        range_key_value="rangeKeyValue"
                                    ),
                                    dynamo_dBv2=iotevents.CfnDetectorModel.DynamoDBv2Property(
                                        table_name="tableName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    firehose=iotevents.CfnDetectorModel.FirehoseProperty(
                                        delivery_stream_name="deliveryStreamName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        separator="separator"
                                    ),
                                    iot_events=iotevents.CfnDetectorModel.IotEventsProperty(
                                        input_name="inputName",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    iot_site_wise=iotevents.CfnDetectorModel.IotSiteWiseProperty(
                                        property_value=iotevents.CfnDetectorModel.AssetPropertyValueProperty(
                                            value=iotevents.CfnDetectorModel.AssetPropertyVariantProperty(
                                                boolean_value="booleanValue",
                                                double_value="doubleValue",
                                                integer_value="integerValue",
                                                string_value="stringValue"
                                            ),
            
                                            # the properties below are optional
                                            quality="quality",
                                            timestamp=iotevents.CfnDetectorModel.AssetPropertyTimestampProperty(
                                                time_in_seconds="timeInSeconds",
            
                                                # the properties below are optional
                                                offset_in_nanos="offsetInNanos"
                                            )
                                        ),
            
                                        # the properties below are optional
                                        asset_id="assetId",
                                        entry_id="entryId",
                                        property_alias="propertyAlias",
                                        property_id="propertyId"
                                    ),
                                    iot_topic_publish=iotevents.CfnDetectorModel.IotTopicPublishProperty(
                                        mqtt_topic="mqttTopic",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    lambda_=iotevents.CfnDetectorModel.LambdaProperty(
                                        function_arn="functionArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    reset_timer=iotevents.CfnDetectorModel.ResetTimerProperty(
                                        timer_name="timerName"
                                    ),
                                    set_timer=iotevents.CfnDetectorModel.SetTimerProperty(
                                        timer_name="timerName",
            
                                        # the properties below are optional
                                        duration_expression="durationExpression",
                                        seconds=123
                                    ),
                                    set_variable=iotevents.CfnDetectorModel.SetVariableProperty(
                                        value="value",
                                        variable_name="variableName"
                                    ),
                                    sns=iotevents.CfnDetectorModel.SnsProperty(
                                        target_arn="targetArn",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        )
                                    ),
                                    sqs=iotevents.CfnDetectorModel.SqsProperty(
                                        queue_url="queueUrl",
            
                                        # the properties below are optional
                                        payload=iotevents.CfnDetectorModel.PayloadProperty(
                                            content_expression="contentExpression",
                                            type="type"
                                        ),
                                        use_base64=False
                                    )
                                )]
                            )]
                        )
                    )]
                ),
                role_arn="roleArn",
            
                # the properties below are optional
                detector_model_description="detectorModelDescription",
                detector_model_name="detectorModelName",
                evaluation_method="evaluationMethod",
                key="key",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "detector_model_definition": detector_model_definition,
            "role_arn": role_arn,
        }
        if detector_model_description is not None:
            self._values["detector_model_description"] = detector_model_description
        if detector_model_name is not None:
            self._values["detector_model_name"] = detector_model_name
        if evaluation_method is not None:
            self._values["evaluation_method"] = evaluation_method
        if key is not None:
            self._values["key"] = key
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def detector_model_definition(
        self,
    ) -> typing.Union[CfnDetectorModel.DetectorModelDefinitionProperty, _IResolvable_da3f097b]:
        '''``AWS::IoTEvents::DetectorModel.DetectorModelDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldefinition
        '''
        result = self._values.get("detector_model_definition")
        assert result is not None, "Required property 'detector_model_definition' is missing"
        return typing.cast(typing.Union[CfnDetectorModel.DetectorModelDefinitionProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def detector_model_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.DetectorModelDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodeldescription
        '''
        result = self._values.get("detector_model_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detector_model_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.DetectorModelName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-detectormodelname
        '''
        result = self._values.get("detector_model_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def evaluation_method(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.EvaluationMethod``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-evaluationmethod
        '''
        result = self._values.get("evaluation_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::DetectorModel.Key``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-key
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''``AWS::IoTEvents::DetectorModel.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoTEvents::DetectorModel.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-detectormodel.html#cfn-iotevents-detectormodel-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDetectorModelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnInput(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iotevents.CfnInput",
):
    '''A CloudFormation ``AWS::IoTEvents::Input``.

    :cloudformationResource: AWS::IoTEvents::Input
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iotevents as iotevents
        
        cfn_input = iotevents.CfnInput(self, "MyCfnInput",
            input_definition=iotevents.CfnInput.InputDefinitionProperty(
                attributes=[iotevents.CfnInput.AttributeProperty(
                    json_path="jsonPath"
                )]
            ),
        
            # the properties below are optional
            input_description="inputDescription",
            input_name="inputName",
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
        input_definition: typing.Union["CfnInput.InputDefinitionProperty", _IResolvable_da3f097b],
        input_description: typing.Optional[builtins.str] = None,
        input_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IoTEvents::Input``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param input_definition: ``AWS::IoTEvents::Input.InputDefinition``.
        :param input_description: ``AWS::IoTEvents::Input.InputDescription``.
        :param input_name: ``AWS::IoTEvents::Input.InputName``.
        :param tags: ``AWS::IoTEvents::Input.Tags``.
        '''
        props = CfnInputProps(
            input_definition=input_definition,
            input_description=input_description,
            input_name=input_name,
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
    @jsii.member(jsii_name="inputDefinition")
    def input_definition(
        self,
    ) -> typing.Union["CfnInput.InputDefinitionProperty", _IResolvable_da3f097b]:
        '''``AWS::IoTEvents::Input.InputDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdefinition
        '''
        return typing.cast(typing.Union["CfnInput.InputDefinitionProperty", _IResolvable_da3f097b], jsii.get(self, "inputDefinition"))

    @input_definition.setter
    def input_definition(
        self,
        value: typing.Union["CfnInput.InputDefinitionProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "inputDefinition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputDescription")
    def input_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::Input.InputDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdescription
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputDescription"))

    @input_description.setter
    def input_description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "inputDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::Input.InputName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputName"))

    @input_name.setter
    def input_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "inputName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoTEvents::Input.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnInput.AttributeProperty",
        jsii_struct_bases=[],
        name_mapping={"json_path": "jsonPath"},
    )
    class AttributeProperty:
        def __init__(self, *, json_path: builtins.str) -> None:
            '''
            :param json_path: ``CfnInput.AttributeProperty.JsonPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-attribute.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                attribute_property = iotevents.CfnInput.AttributeProperty(
                    json_path="jsonPath"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "json_path": json_path,
            }

        @builtins.property
        def json_path(self) -> builtins.str:
            '''``CfnInput.AttributeProperty.JsonPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-attribute.html#cfn-iotevents-input-attribute-jsonpath
            '''
            result = self._values.get("json_path")
            assert result is not None, "Required property 'json_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AttributeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iotevents.CfnInput.InputDefinitionProperty",
        jsii_struct_bases=[],
        name_mapping={"attributes": "attributes"},
    )
    class InputDefinitionProperty:
        def __init__(
            self,
            *,
            attributes: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnInput.AttributeProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param attributes: ``CfnInput.InputDefinitionProperty.Attributes``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-inputdefinition.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iotevents as iotevents
                
                input_definition_property = iotevents.CfnInput.InputDefinitionProperty(
                    attributes=[iotevents.CfnInput.AttributeProperty(
                        json_path="jsonPath"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "attributes": attributes,
            }

        @builtins.property
        def attributes(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnInput.AttributeProperty", _IResolvable_da3f097b]]]:
            '''``CfnInput.InputDefinitionProperty.Attributes``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iotevents-input-inputdefinition.html#cfn-iotevents-input-inputdefinition-attributes
            '''
            result = self._values.get("attributes")
            assert result is not None, "Required property 'attributes' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnInput.AttributeProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InputDefinitionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iotevents.CfnInputProps",
    jsii_struct_bases=[],
    name_mapping={
        "input_definition": "inputDefinition",
        "input_description": "inputDescription",
        "input_name": "inputName",
        "tags": "tags",
    },
)
class CfnInputProps:
    def __init__(
        self,
        *,
        input_definition: typing.Union[CfnInput.InputDefinitionProperty, _IResolvable_da3f097b],
        input_description: typing.Optional[builtins.str] = None,
        input_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoTEvents::Input``.

        :param input_definition: ``AWS::IoTEvents::Input.InputDefinition``.
        :param input_description: ``AWS::IoTEvents::Input.InputDescription``.
        :param input_name: ``AWS::IoTEvents::Input.InputName``.
        :param tags: ``AWS::IoTEvents::Input.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iotevents as iotevents
            
            cfn_input_props = iotevents.CfnInputProps(
                input_definition=iotevents.CfnInput.InputDefinitionProperty(
                    attributes=[iotevents.CfnInput.AttributeProperty(
                        json_path="jsonPath"
                    )]
                ),
            
                # the properties below are optional
                input_description="inputDescription",
                input_name="inputName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "input_definition": input_definition,
        }
        if input_description is not None:
            self._values["input_description"] = input_description
        if input_name is not None:
            self._values["input_name"] = input_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def input_definition(
        self,
    ) -> typing.Union[CfnInput.InputDefinitionProperty, _IResolvable_da3f097b]:
        '''``AWS::IoTEvents::Input.InputDefinition``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdefinition
        '''
        result = self._values.get("input_definition")
        assert result is not None, "Required property 'input_definition' is missing"
        return typing.cast(typing.Union[CfnInput.InputDefinitionProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def input_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::Input.InputDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputdescription
        '''
        result = self._values.get("input_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoTEvents::Input.InputName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-inputname
        '''
        result = self._values.get("input_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoTEvents::Input.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotevents-input.html#cfn-iotevents-input-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnInputProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnDetectorModel",
    "CfnDetectorModelProps",
    "CfnInput",
    "CfnInputProps",
]

publication.publish()
