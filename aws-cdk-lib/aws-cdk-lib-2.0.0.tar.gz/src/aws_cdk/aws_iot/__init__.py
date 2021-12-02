'''
# AWS::IoT Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import aws_cdk.aws_iot as aws_iot
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
class CfnAccountAuditConfiguration(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnAccountAuditConfiguration",
):
    '''A CloudFormation ``AWS::IoT::AccountAuditConfiguration``.

    :cloudformationResource: AWS::IoT::AccountAuditConfiguration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_account_audit_configuration = iot.CfnAccountAuditConfiguration(self, "MyCfnAccountAuditConfiguration",
            account_id="accountId",
            audit_check_configurations=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty(
                authenticated_cognito_role_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                ca_certificate_expiring_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                ca_certificate_key_quality_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                conflicting_client_ids_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                device_certificate_expiring_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                device_certificate_key_quality_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                device_certificate_shared_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                iot_policy_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                iot_role_alias_allows_access_to_unused_services_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                iot_role_alias_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                logging_disabled_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                revoked_ca_certificate_still_active_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                revoked_device_certificate_still_active_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                ),
                unauthenticated_cognito_role_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                )
            ),
            role_arn="roleArn",
        
            # the properties below are optional
            audit_notification_target_configurations=iot.CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty(
                sns=iot.CfnAccountAuditConfiguration.AuditNotificationTargetProperty(
                    enabled=False,
                    role_arn="roleArn",
                    target_arn="targetArn"
                )
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        audit_check_configurations: typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty", _IResolvable_da3f097b],
        audit_notification_target_configurations: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty", _IResolvable_da3f097b]] = None,
        role_arn: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::AccountAuditConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param account_id: ``AWS::IoT::AccountAuditConfiguration.AccountId``.
        :param audit_check_configurations: ``AWS::IoT::AccountAuditConfiguration.AuditCheckConfigurations``.
        :param audit_notification_target_configurations: ``AWS::IoT::AccountAuditConfiguration.AuditNotificationTargetConfigurations``.
        :param role_arn: ``AWS::IoT::AccountAuditConfiguration.RoleArn``.
        '''
        props = CfnAccountAuditConfigurationProps(
            account_id=account_id,
            audit_check_configurations=audit_check_configurations,
            audit_notification_target_configurations=audit_notification_target_configurations,
            role_arn=role_arn,
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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''``AWS::IoT::AccountAuditConfiguration.AccountId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-accountid
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditCheckConfigurations")
    def audit_check_configurations(
        self,
    ) -> typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty", _IResolvable_da3f097b]:
        '''``AWS::IoT::AccountAuditConfiguration.AuditCheckConfigurations``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations
        '''
        return typing.cast(typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty", _IResolvable_da3f097b], jsii.get(self, "auditCheckConfigurations"))

    @audit_check_configurations.setter
    def audit_check_configurations(
        self,
        value: typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "auditCheckConfigurations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auditNotificationTargetConfigurations")
    def audit_notification_target_configurations(
        self,
    ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::AccountAuditConfiguration.AuditNotificationTargetConfigurations``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-auditnotificationtargetconfigurations
        '''
        return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty", _IResolvable_da3f097b]], jsii.get(self, "auditNotificationTargetConfigurations"))

    @audit_notification_target_configurations.setter
    def audit_notification_target_configurations(
        self,
        value: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "auditNotificationTargetConfigurations", value)

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
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''``AWS::IoT::AccountAuditConfiguration.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"enabled": "enabled"},
    )
    class AuditCheckConfigurationProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param enabled: ``CfnAccountAuditConfiguration.AuditCheckConfigurationProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfiguration.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                audit_check_configuration_property = iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                    enabled=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfiguration.html#cfn-iot-accountauditconfiguration-auditcheckconfiguration-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuditCheckConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "authenticated_cognito_role_overly_permissive_check": "authenticatedCognitoRoleOverlyPermissiveCheck",
            "ca_certificate_expiring_check": "caCertificateExpiringCheck",
            "ca_certificate_key_quality_check": "caCertificateKeyQualityCheck",
            "conflicting_client_ids_check": "conflictingClientIdsCheck",
            "device_certificate_expiring_check": "deviceCertificateExpiringCheck",
            "device_certificate_key_quality_check": "deviceCertificateKeyQualityCheck",
            "device_certificate_shared_check": "deviceCertificateSharedCheck",
            "iot_policy_overly_permissive_check": "iotPolicyOverlyPermissiveCheck",
            "iot_role_alias_allows_access_to_unused_services_check": "iotRoleAliasAllowsAccessToUnusedServicesCheck",
            "iot_role_alias_overly_permissive_check": "iotRoleAliasOverlyPermissiveCheck",
            "logging_disabled_check": "loggingDisabledCheck",
            "revoked_ca_certificate_still_active_check": "revokedCaCertificateStillActiveCheck",
            "revoked_device_certificate_still_active_check": "revokedDeviceCertificateStillActiveCheck",
            "unauthenticated_cognito_role_overly_permissive_check": "unauthenticatedCognitoRoleOverlyPermissiveCheck",
        },
    )
    class AuditCheckConfigurationsProperty:
        def __init__(
            self,
            *,
            authenticated_cognito_role_overly_permissive_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            ca_certificate_expiring_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            ca_certificate_key_quality_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            conflicting_client_ids_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            device_certificate_expiring_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            device_certificate_key_quality_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            device_certificate_shared_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            iot_policy_overly_permissive_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            iot_role_alias_allows_access_to_unused_services_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            iot_role_alias_overly_permissive_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            logging_disabled_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            revoked_ca_certificate_still_active_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            revoked_device_certificate_still_active_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
            unauthenticated_cognito_role_overly_permissive_check: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param authenticated_cognito_role_overly_permissive_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.AuthenticatedCognitoRoleOverlyPermissiveCheck``.
            :param ca_certificate_expiring_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.CaCertificateExpiringCheck``.
            :param ca_certificate_key_quality_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.CaCertificateKeyQualityCheck``.
            :param conflicting_client_ids_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.ConflictingClientIdsCheck``.
            :param device_certificate_expiring_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.DeviceCertificateExpiringCheck``.
            :param device_certificate_key_quality_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.DeviceCertificateKeyQualityCheck``.
            :param device_certificate_shared_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.DeviceCertificateSharedCheck``.
            :param iot_policy_overly_permissive_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.IotPolicyOverlyPermissiveCheck``.
            :param iot_role_alias_allows_access_to_unused_services_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.IotRoleAliasAllowsAccessToUnusedServicesCheck``.
            :param iot_role_alias_overly_permissive_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.IotRoleAliasOverlyPermissiveCheck``.
            :param logging_disabled_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.LoggingDisabledCheck``.
            :param revoked_ca_certificate_still_active_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.RevokedCaCertificateStillActiveCheck``.
            :param revoked_device_certificate_still_active_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.RevokedDeviceCertificateStillActiveCheck``.
            :param unauthenticated_cognito_role_overly_permissive_check: ``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.UnauthenticatedCognitoRoleOverlyPermissiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                audit_check_configurations_property = iot.CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty(
                    authenticated_cognito_role_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    ca_certificate_expiring_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    ca_certificate_key_quality_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    conflicting_client_ids_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    device_certificate_expiring_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    device_certificate_key_quality_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    device_certificate_shared_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    iot_policy_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    iot_role_alias_allows_access_to_unused_services_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    iot_role_alias_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    logging_disabled_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    revoked_ca_certificate_still_active_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    revoked_device_certificate_still_active_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    unauthenticated_cognito_role_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if authenticated_cognito_role_overly_permissive_check is not None:
                self._values["authenticated_cognito_role_overly_permissive_check"] = authenticated_cognito_role_overly_permissive_check
            if ca_certificate_expiring_check is not None:
                self._values["ca_certificate_expiring_check"] = ca_certificate_expiring_check
            if ca_certificate_key_quality_check is not None:
                self._values["ca_certificate_key_quality_check"] = ca_certificate_key_quality_check
            if conflicting_client_ids_check is not None:
                self._values["conflicting_client_ids_check"] = conflicting_client_ids_check
            if device_certificate_expiring_check is not None:
                self._values["device_certificate_expiring_check"] = device_certificate_expiring_check
            if device_certificate_key_quality_check is not None:
                self._values["device_certificate_key_quality_check"] = device_certificate_key_quality_check
            if device_certificate_shared_check is not None:
                self._values["device_certificate_shared_check"] = device_certificate_shared_check
            if iot_policy_overly_permissive_check is not None:
                self._values["iot_policy_overly_permissive_check"] = iot_policy_overly_permissive_check
            if iot_role_alias_allows_access_to_unused_services_check is not None:
                self._values["iot_role_alias_allows_access_to_unused_services_check"] = iot_role_alias_allows_access_to_unused_services_check
            if iot_role_alias_overly_permissive_check is not None:
                self._values["iot_role_alias_overly_permissive_check"] = iot_role_alias_overly_permissive_check
            if logging_disabled_check is not None:
                self._values["logging_disabled_check"] = logging_disabled_check
            if revoked_ca_certificate_still_active_check is not None:
                self._values["revoked_ca_certificate_still_active_check"] = revoked_ca_certificate_still_active_check
            if revoked_device_certificate_still_active_check is not None:
                self._values["revoked_device_certificate_still_active_check"] = revoked_device_certificate_still_active_check
            if unauthenticated_cognito_role_overly_permissive_check is not None:
                self._values["unauthenticated_cognito_role_overly_permissive_check"] = unauthenticated_cognito_role_overly_permissive_check

        @builtins.property
        def authenticated_cognito_role_overly_permissive_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.AuthenticatedCognitoRoleOverlyPermissiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-authenticatedcognitoroleoverlypermissivecheck
            '''
            result = self._values.get("authenticated_cognito_role_overly_permissive_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def ca_certificate_expiring_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.CaCertificateExpiringCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-cacertificateexpiringcheck
            '''
            result = self._values.get("ca_certificate_expiring_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def ca_certificate_key_quality_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.CaCertificateKeyQualityCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-cacertificatekeyqualitycheck
            '''
            result = self._values.get("ca_certificate_key_quality_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def conflicting_client_ids_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.ConflictingClientIdsCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-conflictingclientidscheck
            '''
            result = self._values.get("conflicting_client_ids_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def device_certificate_expiring_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.DeviceCertificateExpiringCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-devicecertificateexpiringcheck
            '''
            result = self._values.get("device_certificate_expiring_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def device_certificate_key_quality_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.DeviceCertificateKeyQualityCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-devicecertificatekeyqualitycheck
            '''
            result = self._values.get("device_certificate_key_quality_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def device_certificate_shared_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.DeviceCertificateSharedCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-devicecertificatesharedcheck
            '''
            result = self._values.get("device_certificate_shared_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_policy_overly_permissive_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.IotPolicyOverlyPermissiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-iotpolicyoverlypermissivecheck
            '''
            result = self._values.get("iot_policy_overly_permissive_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_role_alias_allows_access_to_unused_services_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.IotRoleAliasAllowsAccessToUnusedServicesCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-iotrolealiasallowsaccesstounusedservicescheck
            '''
            result = self._values.get("iot_role_alias_allows_access_to_unused_services_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_role_alias_overly_permissive_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.IotRoleAliasOverlyPermissiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-iotrolealiasoverlypermissivecheck
            '''
            result = self._values.get("iot_role_alias_overly_permissive_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def logging_disabled_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.LoggingDisabledCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-loggingdisabledcheck
            '''
            result = self._values.get("logging_disabled_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def revoked_ca_certificate_still_active_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.RevokedCaCertificateStillActiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-revokedcacertificatestillactivecheck
            '''
            result = self._values.get("revoked_ca_certificate_still_active_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def revoked_device_certificate_still_active_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.RevokedDeviceCertificateStillActiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-revokeddevicecertificatestillactivecheck
            '''
            result = self._values.get("revoked_device_certificate_still_active_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def unauthenticated_cognito_role_overly_permissive_check(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty.UnauthenticatedCognitoRoleOverlyPermissiveCheck``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditcheckconfigurations.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations-unauthenticatedcognitoroleoverlypermissivecheck
            '''
            result = self._values.get("unauthenticated_cognito_role_overly_permissive_check")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditCheckConfigurationProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuditCheckConfigurationsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty",
        jsii_struct_bases=[],
        name_mapping={"sns": "sns"},
    )
    class AuditNotificationTargetConfigurationsProperty:
        def __init__(
            self,
            *,
            sns: typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param sns: ``CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty.Sns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditnotificationtargetconfigurations.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                audit_notification_target_configurations_property = iot.CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty(
                    sns=iot.CfnAccountAuditConfiguration.AuditNotificationTargetProperty(
                        enabled=False,
                        role_arn="roleArn",
                        target_arn="targetArn"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if sns is not None:
                self._values["sns"] = sns

        @builtins.property
        def sns(
            self,
        ) -> typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetProperty", _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty.Sns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditnotificationtargetconfigurations.html#cfn-iot-accountauditconfiguration-auditnotificationtargetconfigurations-sns
            '''
            result = self._values.get("sns")
            return typing.cast(typing.Optional[typing.Union["CfnAccountAuditConfiguration.AuditNotificationTargetProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuditNotificationTargetConfigurationsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnAccountAuditConfiguration.AuditNotificationTargetProperty",
        jsii_struct_bases=[],
        name_mapping={
            "enabled": "enabled",
            "role_arn": "roleArn",
            "target_arn": "targetArn",
        },
    )
    class AuditNotificationTargetProperty:
        def __init__(
            self,
            *,
            enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            role_arn: typing.Optional[builtins.str] = None,
            target_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param enabled: ``CfnAccountAuditConfiguration.AuditNotificationTargetProperty.Enabled``.
            :param role_arn: ``CfnAccountAuditConfiguration.AuditNotificationTargetProperty.RoleArn``.
            :param target_arn: ``CfnAccountAuditConfiguration.AuditNotificationTargetProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditnotificationtarget.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                audit_notification_target_property = iot.CfnAccountAuditConfiguration.AuditNotificationTargetProperty(
                    enabled=False,
                    role_arn="roleArn",
                    target_arn="targetArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if enabled is not None:
                self._values["enabled"] = enabled
            if role_arn is not None:
                self._values["role_arn"] = role_arn
            if target_arn is not None:
                self._values["target_arn"] = target_arn

        @builtins.property
        def enabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnAccountAuditConfiguration.AuditNotificationTargetProperty.Enabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditnotificationtarget.html#cfn-iot-accountauditconfiguration-auditnotificationtarget-enabled
            '''
            result = self._values.get("enabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnAccountAuditConfiguration.AuditNotificationTargetProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditnotificationtarget.html#cfn-iot-accountauditconfiguration-auditnotificationtarget-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def target_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnAccountAuditConfiguration.AuditNotificationTargetProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-accountauditconfiguration-auditnotificationtarget.html#cfn-iot-accountauditconfiguration-auditnotificationtarget-targetarn
            '''
            result = self._values.get("target_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuditNotificationTargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnAccountAuditConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "audit_check_configurations": "auditCheckConfigurations",
        "audit_notification_target_configurations": "auditNotificationTargetConfigurations",
        "role_arn": "roleArn",
    },
)
class CfnAccountAuditConfigurationProps:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        audit_check_configurations: typing.Union[CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty, _IResolvable_da3f097b],
        audit_notification_target_configurations: typing.Optional[typing.Union[CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty, _IResolvable_da3f097b]] = None,
        role_arn: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::AccountAuditConfiguration``.

        :param account_id: ``AWS::IoT::AccountAuditConfiguration.AccountId``.
        :param audit_check_configurations: ``AWS::IoT::AccountAuditConfiguration.AuditCheckConfigurations``.
        :param audit_notification_target_configurations: ``AWS::IoT::AccountAuditConfiguration.AuditNotificationTargetConfigurations``.
        :param role_arn: ``AWS::IoT::AccountAuditConfiguration.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_account_audit_configuration_props = iot.CfnAccountAuditConfigurationProps(
                account_id="accountId",
                audit_check_configurations=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty(
                    authenticated_cognito_role_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    ca_certificate_expiring_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    ca_certificate_key_quality_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    conflicting_client_ids_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    device_certificate_expiring_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    device_certificate_key_quality_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    device_certificate_shared_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    iot_policy_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    iot_role_alias_allows_access_to_unused_services_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    iot_role_alias_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    logging_disabled_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    revoked_ca_certificate_still_active_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    revoked_device_certificate_still_active_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    ),
                    unauthenticated_cognito_role_overly_permissive_check=iot.CfnAccountAuditConfiguration.AuditCheckConfigurationProperty(
                        enabled=False
                    )
                ),
                role_arn="roleArn",
            
                # the properties below are optional
                audit_notification_target_configurations=iot.CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty(
                    sns=iot.CfnAccountAuditConfiguration.AuditNotificationTargetProperty(
                        enabled=False,
                        role_arn="roleArn",
                        target_arn="targetArn"
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "audit_check_configurations": audit_check_configurations,
            "role_arn": role_arn,
        }
        if audit_notification_target_configurations is not None:
            self._values["audit_notification_target_configurations"] = audit_notification_target_configurations

    @builtins.property
    def account_id(self) -> builtins.str:
        '''``AWS::IoT::AccountAuditConfiguration.AccountId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-accountid
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audit_check_configurations(
        self,
    ) -> typing.Union[CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty, _IResolvable_da3f097b]:
        '''``AWS::IoT::AccountAuditConfiguration.AuditCheckConfigurations``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-auditcheckconfigurations
        '''
        result = self._values.get("audit_check_configurations")
        assert result is not None, "Required property 'audit_check_configurations' is missing"
        return typing.cast(typing.Union[CfnAccountAuditConfiguration.AuditCheckConfigurationsProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def audit_notification_target_configurations(
        self,
    ) -> typing.Optional[typing.Union[CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::AccountAuditConfiguration.AuditNotificationTargetConfigurations``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-auditnotificationtargetconfigurations
        '''
        result = self._values.get("audit_notification_target_configurations")
        return typing.cast(typing.Optional[typing.Union[CfnAccountAuditConfiguration.AuditNotificationTargetConfigurationsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''``AWS::IoT::AccountAuditConfiguration.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-accountauditconfiguration.html#cfn-iot-accountauditconfiguration-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAccountAuditConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnAuthorizer(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnAuthorizer",
):
    '''A CloudFormation ``AWS::IoT::Authorizer``.

    :cloudformationResource: AWS::IoT::Authorizer
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_authorizer = iot.CfnAuthorizer(self, "MyCfnAuthorizer",
            authorizer_function_arn="authorizerFunctionArn",
        
            # the properties below are optional
            authorizer_name="authorizerName",
            signing_disabled=False,
            status="status",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            token_key_name="tokenKeyName",
            token_signing_public_keys={
                "token_signing_public_keys_key": "tokenSigningPublicKeys"
            }
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authorizer_function_arn: builtins.str,
        authorizer_name: typing.Optional[builtins.str] = None,
        signing_disabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        token_key_name: typing.Optional[builtins.str] = None,
        token_signing_public_keys: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::Authorizer``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authorizer_function_arn: ``AWS::IoT::Authorizer.AuthorizerFunctionArn``.
        :param authorizer_name: ``AWS::IoT::Authorizer.AuthorizerName``.
        :param signing_disabled: ``AWS::IoT::Authorizer.SigningDisabled``.
        :param status: ``AWS::IoT::Authorizer.Status``.
        :param tags: ``AWS::IoT::Authorizer.Tags``.
        :param token_key_name: ``AWS::IoT::Authorizer.TokenKeyName``.
        :param token_signing_public_keys: ``AWS::IoT::Authorizer.TokenSigningPublicKeys``.
        '''
        props = CfnAuthorizerProps(
            authorizer_function_arn=authorizer_function_arn,
            authorizer_name=authorizer_name,
            signing_disabled=signing_disabled,
            status=status,
            tags=tags,
            token_key_name=token_key_name,
            token_signing_public_keys=token_signing_public_keys,
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
    @jsii.member(jsii_name="authorizerFunctionArn")
    def authorizer_function_arn(self) -> builtins.str:
        '''``AWS::IoT::Authorizer.AuthorizerFunctionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-authorizerfunctionarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "authorizerFunctionArn"))

    @authorizer_function_arn.setter
    def authorizer_function_arn(self, value: builtins.str) -> None:
        jsii.set(self, "authorizerFunctionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerName")
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Authorizer.AuthorizerName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-authorizername
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizerName"))

    @authorizer_name.setter
    def authorizer_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "authorizerName", value)

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
    @jsii.member(jsii_name="signingDisabled")
    def signing_disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::IoT::Authorizer.SigningDisabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-signingdisabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "signingDisabled"))

    @signing_disabled.setter
    def signing_disabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "signingDisabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Authorizer.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-status
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @status.setter
    def status(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::Authorizer.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenKeyName")
    def token_key_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Authorizer.TokenKeyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-tokenkeyname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenKeyName"))

    @token_key_name.setter
    def token_key_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "tokenKeyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenSigningPublicKeys")
    def token_signing_public_keys(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]]:
        '''``AWS::IoT::Authorizer.TokenSigningPublicKeys``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-tokensigningpublickeys
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tokenSigningPublicKeys"))

    @token_signing_public_keys.setter
    def token_signing_public_keys(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]],
    ) -> None:
        jsii.set(self, "tokenSigningPublicKeys", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnAuthorizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_function_arn": "authorizerFunctionArn",
        "authorizer_name": "authorizerName",
        "signing_disabled": "signingDisabled",
        "status": "status",
        "tags": "tags",
        "token_key_name": "tokenKeyName",
        "token_signing_public_keys": "tokenSigningPublicKeys",
    },
)
class CfnAuthorizerProps:
    def __init__(
        self,
        *,
        authorizer_function_arn: builtins.str,
        authorizer_name: typing.Optional[builtins.str] = None,
        signing_disabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        status: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        token_key_name: typing.Optional[builtins.str] = None,
        token_signing_public_keys: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::Authorizer``.

        :param authorizer_function_arn: ``AWS::IoT::Authorizer.AuthorizerFunctionArn``.
        :param authorizer_name: ``AWS::IoT::Authorizer.AuthorizerName``.
        :param signing_disabled: ``AWS::IoT::Authorizer.SigningDisabled``.
        :param status: ``AWS::IoT::Authorizer.Status``.
        :param tags: ``AWS::IoT::Authorizer.Tags``.
        :param token_key_name: ``AWS::IoT::Authorizer.TokenKeyName``.
        :param token_signing_public_keys: ``AWS::IoT::Authorizer.TokenSigningPublicKeys``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_authorizer_props = iot.CfnAuthorizerProps(
                authorizer_function_arn="authorizerFunctionArn",
            
                # the properties below are optional
                authorizer_name="authorizerName",
                signing_disabled=False,
                status="status",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                token_key_name="tokenKeyName",
                token_signing_public_keys={
                    "token_signing_public_keys_key": "tokenSigningPublicKeys"
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorizer_function_arn": authorizer_function_arn,
        }
        if authorizer_name is not None:
            self._values["authorizer_name"] = authorizer_name
        if signing_disabled is not None:
            self._values["signing_disabled"] = signing_disabled
        if status is not None:
            self._values["status"] = status
        if tags is not None:
            self._values["tags"] = tags
        if token_key_name is not None:
            self._values["token_key_name"] = token_key_name
        if token_signing_public_keys is not None:
            self._values["token_signing_public_keys"] = token_signing_public_keys

    @builtins.property
    def authorizer_function_arn(self) -> builtins.str:
        '''``AWS::IoT::Authorizer.AuthorizerFunctionArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-authorizerfunctionarn
        '''
        result = self._values.get("authorizer_function_arn")
        assert result is not None, "Required property 'authorizer_function_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Authorizer.AuthorizerName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-authorizername
        '''
        result = self._values.get("authorizer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signing_disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::IoT::Authorizer.SigningDisabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-signingdisabled
        '''
        result = self._values.get("signing_disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Authorizer.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-status
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::Authorizer.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def token_key_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Authorizer.TokenKeyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-tokenkeyname
        '''
        result = self._values.get("token_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_signing_public_keys(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]]:
        '''``AWS::IoT::Authorizer.TokenSigningPublicKeys``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-authorizer.html#cfn-iot-authorizer-tokensigningpublickeys
        '''
        result = self._values.get("token_signing_public_keys")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAuthorizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCertificate(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnCertificate",
):
    '''A CloudFormation ``AWS::IoT::Certificate``.

    :cloudformationResource: AWS::IoT::Certificate
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_certificate = iot.CfnCertificate(self, "MyCfnCertificate",
            status="status",
        
            # the properties below are optional
            ca_certificate_pem="caCertificatePem",
            certificate_mode="certificateMode",
            certificate_pem="certificatePem",
            certificate_signing_request="certificateSigningRequest"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ca_certificate_pem: typing.Optional[builtins.str] = None,
        certificate_mode: typing.Optional[builtins.str] = None,
        certificate_pem: typing.Optional[builtins.str] = None,
        certificate_signing_request: typing.Optional[builtins.str] = None,
        status: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::Certificate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param ca_certificate_pem: ``AWS::IoT::Certificate.CACertificatePem``.
        :param certificate_mode: ``AWS::IoT::Certificate.CertificateMode``.
        :param certificate_pem: ``AWS::IoT::Certificate.CertificatePem``.
        :param certificate_signing_request: ``AWS::IoT::Certificate.CertificateSigningRequest``.
        :param status: ``AWS::IoT::Certificate.Status``.
        '''
        props = CfnCertificateProps(
            ca_certificate_pem=ca_certificate_pem,
            certificate_mode=certificate_mode,
            certificate_pem=certificate_pem,
            certificate_signing_request=certificate_signing_request,
            status=status,
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
    @jsii.member(jsii_name="caCertificatePem")
    def ca_certificate_pem(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CACertificatePem``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-cacertificatepem
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertificatePem"))

    @ca_certificate_pem.setter
    def ca_certificate_pem(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "caCertificatePem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateMode")
    def certificate_mode(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CertificateMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatemode
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateMode"))

    @certificate_mode.setter
    def certificate_mode(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificateMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CertificatePem``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatepem
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificatePem"))

    @certificate_pem.setter
    def certificate_pem(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificatePem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateSigningRequest")
    def certificate_signing_request(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CertificateSigningRequest``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateSigningRequest"))

    @certificate_signing_request.setter
    def certificate_signing_request(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certificateSigningRequest", value)

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
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        '''``AWS::IoT::Certificate.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
        '''
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnCertificateProps",
    jsii_struct_bases=[],
    name_mapping={
        "ca_certificate_pem": "caCertificatePem",
        "certificate_mode": "certificateMode",
        "certificate_pem": "certificatePem",
        "certificate_signing_request": "certificateSigningRequest",
        "status": "status",
    },
)
class CfnCertificateProps:
    def __init__(
        self,
        *,
        ca_certificate_pem: typing.Optional[builtins.str] = None,
        certificate_mode: typing.Optional[builtins.str] = None,
        certificate_pem: typing.Optional[builtins.str] = None,
        certificate_signing_request: typing.Optional[builtins.str] = None,
        status: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::Certificate``.

        :param ca_certificate_pem: ``AWS::IoT::Certificate.CACertificatePem``.
        :param certificate_mode: ``AWS::IoT::Certificate.CertificateMode``.
        :param certificate_pem: ``AWS::IoT::Certificate.CertificatePem``.
        :param certificate_signing_request: ``AWS::IoT::Certificate.CertificateSigningRequest``.
        :param status: ``AWS::IoT::Certificate.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_certificate_props = iot.CfnCertificateProps(
                status="status",
            
                # the properties below are optional
                ca_certificate_pem="caCertificatePem",
                certificate_mode="certificateMode",
                certificate_pem="certificatePem",
                certificate_signing_request="certificateSigningRequest"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status": status,
        }
        if ca_certificate_pem is not None:
            self._values["ca_certificate_pem"] = ca_certificate_pem
        if certificate_mode is not None:
            self._values["certificate_mode"] = certificate_mode
        if certificate_pem is not None:
            self._values["certificate_pem"] = certificate_pem
        if certificate_signing_request is not None:
            self._values["certificate_signing_request"] = certificate_signing_request

    @builtins.property
    def ca_certificate_pem(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CACertificatePem``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-cacertificatepem
        '''
        result = self._values.get("ca_certificate_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_mode(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CertificateMode``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatemode
        '''
        result = self._values.get("certificate_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_pem(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CertificatePem``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatepem
        '''
        result = self._values.get("certificate_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_signing_request(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Certificate.CertificateSigningRequest``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-certificatesigningrequest
        '''
        result = self._values.get("certificate_signing_request")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> builtins.str:
        '''``AWS::IoT::Certificate.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-certificate.html#cfn-iot-certificate-status
        '''
        result = self._values.get("status")
        assert result is not None, "Required property 'status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCertificateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnCustomMetric(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnCustomMetric",
):
    '''A CloudFormation ``AWS::IoT::CustomMetric``.

    :cloudformationResource: AWS::IoT::CustomMetric
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_custom_metric = iot.CfnCustomMetric(self, "MyCfnCustomMetric",
            metric_type="metricType",
        
            # the properties below are optional
            display_name="displayName",
            metric_name="metricName",
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
        display_name: typing.Optional[builtins.str] = None,
        metric_name: typing.Optional[builtins.str] = None,
        metric_type: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::CustomMetric``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param display_name: ``AWS::IoT::CustomMetric.DisplayName``.
        :param metric_name: ``AWS::IoT::CustomMetric.MetricName``.
        :param metric_type: ``AWS::IoT::CustomMetric.MetricType``.
        :param tags: ``AWS::IoT::CustomMetric.Tags``.
        '''
        props = CfnCustomMetricProps(
            display_name=display_name,
            metric_name=metric_name,
            metric_type=metric_type,
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
    @jsii.member(jsii_name="attrMetricArn")
    def attr_metric_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: MetricArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMetricArn"))

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
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::CustomMetric.DisplayName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-displayname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "displayName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::CustomMetric.MetricName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-metricname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "metricName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricType")
    def metric_type(self) -> builtins.str:
        '''``AWS::IoT::CustomMetric.MetricType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-metrictype
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricType"))

    @metric_type.setter
    def metric_type(self, value: builtins.str) -> None:
        jsii.set(self, "metricType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::CustomMetric.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnCustomMetricProps",
    jsii_struct_bases=[],
    name_mapping={
        "display_name": "displayName",
        "metric_name": "metricName",
        "metric_type": "metricType",
        "tags": "tags",
    },
)
class CfnCustomMetricProps:
    def __init__(
        self,
        *,
        display_name: typing.Optional[builtins.str] = None,
        metric_name: typing.Optional[builtins.str] = None,
        metric_type: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::CustomMetric``.

        :param display_name: ``AWS::IoT::CustomMetric.DisplayName``.
        :param metric_name: ``AWS::IoT::CustomMetric.MetricName``.
        :param metric_type: ``AWS::IoT::CustomMetric.MetricType``.
        :param tags: ``AWS::IoT::CustomMetric.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_custom_metric_props = iot.CfnCustomMetricProps(
                metric_type="metricType",
            
                # the properties below are optional
                display_name="displayName",
                metric_name="metricName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "metric_type": metric_type,
        }
        if display_name is not None:
            self._values["display_name"] = display_name
        if metric_name is not None:
            self._values["metric_name"] = metric_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::CustomMetric.DisplayName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-displayname
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::CustomMetric.MetricName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-metricname
        '''
        result = self._values.get("metric_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_type(self) -> builtins.str:
        '''``AWS::IoT::CustomMetric.MetricType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-metrictype
        '''
        result = self._values.get("metric_type")
        assert result is not None, "Required property 'metric_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::CustomMetric.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-custommetric.html#cfn-iot-custommetric-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCustomMetricProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDimension(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnDimension",
):
    '''A CloudFormation ``AWS::IoT::Dimension``.

    :cloudformationResource: AWS::IoT::Dimension
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_dimension = iot.CfnDimension(self, "MyCfnDimension",
            string_values=["stringValues"],
            type="type",
        
            # the properties below are optional
            name="name",
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
        name: typing.Optional[builtins.str] = None,
        string_values: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        type: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::Dimension``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param name: ``AWS::IoT::Dimension.Name``.
        :param string_values: ``AWS::IoT::Dimension.StringValues``.
        :param tags: ``AWS::IoT::Dimension.Tags``.
        :param type: ``AWS::IoT::Dimension.Type``.
        '''
        props = CfnDimensionProps(
            name=name, string_values=string_values, tags=tags, type=type
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
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Dimension.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringValues")
    def string_values(self) -> typing.List[builtins.str]:
        '''``AWS::IoT::Dimension.StringValues``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-stringvalues
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "stringValues"))

    @string_values.setter
    def string_values(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "stringValues", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::Dimension.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        '''``AWS::IoT::Dimension.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-type
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnDimensionProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "string_values": "stringValues",
        "tags": "tags",
        "type": "type",
    },
)
class CfnDimensionProps:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        string_values: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        type: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::Dimension``.

        :param name: ``AWS::IoT::Dimension.Name``.
        :param string_values: ``AWS::IoT::Dimension.StringValues``.
        :param tags: ``AWS::IoT::Dimension.Tags``.
        :param type: ``AWS::IoT::Dimension.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_dimension_props = iot.CfnDimensionProps(
                string_values=["stringValues"],
                type="type",
            
                # the properties below are optional
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "string_values": string_values,
            "type": type,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Dimension.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def string_values(self) -> typing.List[builtins.str]:
        '''``AWS::IoT::Dimension.StringValues``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-stringvalues
        '''
        result = self._values.get("string_values")
        assert result is not None, "Required property 'string_values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::Dimension.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''``AWS::IoT::Dimension.Type``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-dimension.html#cfn-iot-dimension-type
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDimensionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnDomainConfiguration(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnDomainConfiguration",
):
    '''A CloudFormation ``AWS::IoT::DomainConfiguration``.

    :cloudformationResource: AWS::IoT::DomainConfiguration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_domain_configuration = iot.CfnDomainConfiguration(self, "MyCfnDomainConfiguration",
            authorizer_config=iot.CfnDomainConfiguration.AuthorizerConfigProperty(
                allow_authorizer_override=False,
                default_authorizer_name="defaultAuthorizerName"
            ),
            domain_configuration_name="domainConfigurationName",
            domain_configuration_status="domainConfigurationStatus",
            domain_name="domainName",
            server_certificate_arns=["serverCertificateArns"],
            service_type="serviceType",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            validation_certificate_arn="validationCertificateArn"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authorizer_config: typing.Optional[typing.Union["CfnDomainConfiguration.AuthorizerConfigProperty", _IResolvable_da3f097b]] = None,
        domain_configuration_name: typing.Optional[builtins.str] = None,
        domain_configuration_status: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        server_certificate_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        validation_certificate_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::DomainConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authorizer_config: ``AWS::IoT::DomainConfiguration.AuthorizerConfig``.
        :param domain_configuration_name: ``AWS::IoT::DomainConfiguration.DomainConfigurationName``.
        :param domain_configuration_status: ``AWS::IoT::DomainConfiguration.DomainConfigurationStatus``.
        :param domain_name: ``AWS::IoT::DomainConfiguration.DomainName``.
        :param server_certificate_arns: ``AWS::IoT::DomainConfiguration.ServerCertificateArns``.
        :param service_type: ``AWS::IoT::DomainConfiguration.ServiceType``.
        :param tags: ``AWS::IoT::DomainConfiguration.Tags``.
        :param validation_certificate_arn: ``AWS::IoT::DomainConfiguration.ValidationCertificateArn``.
        '''
        props = CfnDomainConfigurationProps(
            authorizer_config=authorizer_config,
            domain_configuration_name=domain_configuration_name,
            domain_configuration_status=domain_configuration_status,
            domain_name=domain_name,
            server_certificate_arns=server_certificate_arns,
            service_type=service_type,
            tags=tags,
            validation_certificate_arn=validation_certificate_arn,
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
    @jsii.member(jsii_name="attrDomainType")
    def attr_domain_type(self) -> builtins.str:
        '''
        :cloudformationAttribute: DomainType
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrDomainType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrServerCertificates")
    def attr_server_certificates(self) -> _IResolvable_da3f097b:
        '''
        :cloudformationAttribute: ServerCertificates
        '''
        return typing.cast(_IResolvable_da3f097b, jsii.get(self, "attrServerCertificates"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizerConfig")
    def authorizer_config(
        self,
    ) -> typing.Optional[typing.Union["CfnDomainConfiguration.AuthorizerConfigProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::DomainConfiguration.AuthorizerConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-authorizerconfig
        '''
        return typing.cast(typing.Optional[typing.Union["CfnDomainConfiguration.AuthorizerConfigProperty", _IResolvable_da3f097b]], jsii.get(self, "authorizerConfig"))

    @authorizer_config.setter
    def authorizer_config(
        self,
        value: typing.Optional[typing.Union["CfnDomainConfiguration.AuthorizerConfigProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "authorizerConfig", value)

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
    @jsii.member(jsii_name="domainConfigurationName")
    def domain_configuration_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.DomainConfigurationName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-domainconfigurationname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainConfigurationName"))

    @domain_configuration_name.setter
    def domain_configuration_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "domainConfigurationName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainConfigurationStatus")
    def domain_configuration_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.DomainConfigurationStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-domainconfigurationstatus
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainConfigurationStatus"))

    @domain_configuration_status.setter
    def domain_configuration_status(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "domainConfigurationStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-domainname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverCertificateArns")
    def server_certificate_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::IoT::DomainConfiguration.ServerCertificateArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-servercertificatearns
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serverCertificateArns"))

    @server_certificate_arns.setter
    def server_certificate_arns(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "serverCertificateArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceType")
    def service_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.ServiceType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-servicetype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceType"))

    @service_type.setter
    def service_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "serviceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::DomainConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validationCertificateArn")
    def validation_certificate_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.ValidationCertificateArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-validationcertificatearn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "validationCertificateArn"))

    @validation_certificate_arn.setter
    def validation_certificate_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "validationCertificateArn", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnDomainConfiguration.AuthorizerConfigProperty",
        jsii_struct_bases=[],
        name_mapping={
            "allow_authorizer_override": "allowAuthorizerOverride",
            "default_authorizer_name": "defaultAuthorizerName",
        },
    )
    class AuthorizerConfigProperty:
        def __init__(
            self,
            *,
            allow_authorizer_override: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            default_authorizer_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param allow_authorizer_override: ``CfnDomainConfiguration.AuthorizerConfigProperty.AllowAuthorizerOverride``.
            :param default_authorizer_name: ``CfnDomainConfiguration.AuthorizerConfigProperty.DefaultAuthorizerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-authorizerconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                authorizer_config_property = iot.CfnDomainConfiguration.AuthorizerConfigProperty(
                    allow_authorizer_override=False,
                    default_authorizer_name="defaultAuthorizerName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if allow_authorizer_override is not None:
                self._values["allow_authorizer_override"] = allow_authorizer_override
            if default_authorizer_name is not None:
                self._values["default_authorizer_name"] = default_authorizer_name

        @builtins.property
        def allow_authorizer_override(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnDomainConfiguration.AuthorizerConfigProperty.AllowAuthorizerOverride``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-authorizerconfig.html#cfn-iot-domainconfiguration-authorizerconfig-allowauthorizeroverride
            '''
            result = self._values.get("allow_authorizer_override")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def default_authorizer_name(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainConfiguration.AuthorizerConfigProperty.DefaultAuthorizerName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-authorizerconfig.html#cfn-iot-domainconfiguration-authorizerconfig-defaultauthorizername
            '''
            result = self._values.get("default_authorizer_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AuthorizerConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnDomainConfiguration.ServerCertificateSummaryProperty",
        jsii_struct_bases=[],
        name_mapping={
            "server_certificate_arn": "serverCertificateArn",
            "server_certificate_status": "serverCertificateStatus",
            "server_certificate_status_detail": "serverCertificateStatusDetail",
        },
    )
    class ServerCertificateSummaryProperty:
        def __init__(
            self,
            *,
            server_certificate_arn: typing.Optional[builtins.str] = None,
            server_certificate_status: typing.Optional[builtins.str] = None,
            server_certificate_status_detail: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param server_certificate_arn: ``CfnDomainConfiguration.ServerCertificateSummaryProperty.ServerCertificateArn``.
            :param server_certificate_status: ``CfnDomainConfiguration.ServerCertificateSummaryProperty.ServerCertificateStatus``.
            :param server_certificate_status_detail: ``CfnDomainConfiguration.ServerCertificateSummaryProperty.ServerCertificateStatusDetail``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-servercertificatesummary.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                server_certificate_summary_property = iot.CfnDomainConfiguration.ServerCertificateSummaryProperty(
                    server_certificate_arn="serverCertificateArn",
                    server_certificate_status="serverCertificateStatus",
                    server_certificate_status_detail="serverCertificateStatusDetail"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if server_certificate_arn is not None:
                self._values["server_certificate_arn"] = server_certificate_arn
            if server_certificate_status is not None:
                self._values["server_certificate_status"] = server_certificate_status
            if server_certificate_status_detail is not None:
                self._values["server_certificate_status_detail"] = server_certificate_status_detail

        @builtins.property
        def server_certificate_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainConfiguration.ServerCertificateSummaryProperty.ServerCertificateArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-servercertificatesummary.html#cfn-iot-domainconfiguration-servercertificatesummary-servercertificatearn
            '''
            result = self._values.get("server_certificate_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def server_certificate_status(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainConfiguration.ServerCertificateSummaryProperty.ServerCertificateStatus``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-servercertificatesummary.html#cfn-iot-domainconfiguration-servercertificatesummary-servercertificatestatus
            '''
            result = self._values.get("server_certificate_status")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def server_certificate_status_detail(self) -> typing.Optional[builtins.str]:
            '''``CfnDomainConfiguration.ServerCertificateSummaryProperty.ServerCertificateStatusDetail``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-domainconfiguration-servercertificatesummary.html#cfn-iot-domainconfiguration-servercertificatesummary-servercertificatestatusdetail
            '''
            result = self._values.get("server_certificate_status_detail")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ServerCertificateSummaryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnDomainConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorizer_config": "authorizerConfig",
        "domain_configuration_name": "domainConfigurationName",
        "domain_configuration_status": "domainConfigurationStatus",
        "domain_name": "domainName",
        "server_certificate_arns": "serverCertificateArns",
        "service_type": "serviceType",
        "tags": "tags",
        "validation_certificate_arn": "validationCertificateArn",
    },
)
class CfnDomainConfigurationProps:
    def __init__(
        self,
        *,
        authorizer_config: typing.Optional[typing.Union[CfnDomainConfiguration.AuthorizerConfigProperty, _IResolvable_da3f097b]] = None,
        domain_configuration_name: typing.Optional[builtins.str] = None,
        domain_configuration_status: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        server_certificate_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_type: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        validation_certificate_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::DomainConfiguration``.

        :param authorizer_config: ``AWS::IoT::DomainConfiguration.AuthorizerConfig``.
        :param domain_configuration_name: ``AWS::IoT::DomainConfiguration.DomainConfigurationName``.
        :param domain_configuration_status: ``AWS::IoT::DomainConfiguration.DomainConfigurationStatus``.
        :param domain_name: ``AWS::IoT::DomainConfiguration.DomainName``.
        :param server_certificate_arns: ``AWS::IoT::DomainConfiguration.ServerCertificateArns``.
        :param service_type: ``AWS::IoT::DomainConfiguration.ServiceType``.
        :param tags: ``AWS::IoT::DomainConfiguration.Tags``.
        :param validation_certificate_arn: ``AWS::IoT::DomainConfiguration.ValidationCertificateArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_domain_configuration_props = iot.CfnDomainConfigurationProps(
                authorizer_config=iot.CfnDomainConfiguration.AuthorizerConfigProperty(
                    allow_authorizer_override=False,
                    default_authorizer_name="defaultAuthorizerName"
                ),
                domain_configuration_name="domainConfigurationName",
                domain_configuration_status="domainConfigurationStatus",
                domain_name="domainName",
                server_certificate_arns=["serverCertificateArns"],
                service_type="serviceType",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                validation_certificate_arn="validationCertificateArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorizer_config is not None:
            self._values["authorizer_config"] = authorizer_config
        if domain_configuration_name is not None:
            self._values["domain_configuration_name"] = domain_configuration_name
        if domain_configuration_status is not None:
            self._values["domain_configuration_status"] = domain_configuration_status
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if server_certificate_arns is not None:
            self._values["server_certificate_arns"] = server_certificate_arns
        if service_type is not None:
            self._values["service_type"] = service_type
        if tags is not None:
            self._values["tags"] = tags
        if validation_certificate_arn is not None:
            self._values["validation_certificate_arn"] = validation_certificate_arn

    @builtins.property
    def authorizer_config(
        self,
    ) -> typing.Optional[typing.Union[CfnDomainConfiguration.AuthorizerConfigProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::DomainConfiguration.AuthorizerConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-authorizerconfig
        '''
        result = self._values.get("authorizer_config")
        return typing.cast(typing.Optional[typing.Union[CfnDomainConfiguration.AuthorizerConfigProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def domain_configuration_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.DomainConfigurationName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-domainconfigurationname
        '''
        result = self._values.get("domain_configuration_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_configuration_status(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.DomainConfigurationStatus``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-domainconfigurationstatus
        '''
        result = self._values.get("domain_configuration_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.DomainName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-domainname
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_certificate_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::IoT::DomainConfiguration.ServerCertificateArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-servercertificatearns
        '''
        result = self._values.get("server_certificate_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_type(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.ServiceType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-servicetype
        '''
        result = self._values.get("service_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::DomainConfiguration.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def validation_certificate_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::DomainConfiguration.ValidationCertificateArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-domainconfiguration.html#cfn-iot-domainconfiguration-validationcertificatearn
        '''
        result = self._values.get("validation_certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDomainConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnFleetMetric(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnFleetMetric",
):
    '''A CloudFormation ``AWS::IoT::FleetMetric``.

    :cloudformationResource: AWS::IoT::FleetMetric
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_fleet_metric = iot.CfnFleetMetric(self, "MyCfnFleetMetric",
            metric_name="metricName",
        
            # the properties below are optional
            aggregation_field="aggregationField",
            aggregation_type=iot.CfnFleetMetric.AggregationTypeProperty(
                name="name",
                values=["values"]
            ),
            description="description",
            index_name="indexName",
            period=123,
            query_string="queryString",
            query_version="queryVersion",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            unit="unit"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        aggregation_field: typing.Optional[builtins.str] = None,
        aggregation_type: typing.Optional[typing.Union["CfnFleetMetric.AggregationTypeProperty", _IResolvable_da3f097b]] = None,
        description: typing.Optional[builtins.str] = None,
        index_name: typing.Optional[builtins.str] = None,
        metric_name: builtins.str,
        period: typing.Optional[jsii.Number] = None,
        query_string: typing.Optional[builtins.str] = None,
        query_version: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::FleetMetric``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param aggregation_field: ``AWS::IoT::FleetMetric.AggregationField``.
        :param aggregation_type: ``AWS::IoT::FleetMetric.AggregationType``.
        :param description: ``AWS::IoT::FleetMetric.Description``.
        :param index_name: ``AWS::IoT::FleetMetric.IndexName``.
        :param metric_name: ``AWS::IoT::FleetMetric.MetricName``.
        :param period: ``AWS::IoT::FleetMetric.Period``.
        :param query_string: ``AWS::IoT::FleetMetric.QueryString``.
        :param query_version: ``AWS::IoT::FleetMetric.QueryVersion``.
        :param tags: ``AWS::IoT::FleetMetric.Tags``.
        :param unit: ``AWS::IoT::FleetMetric.Unit``.
        '''
        props = CfnFleetMetricProps(
            aggregation_field=aggregation_field,
            aggregation_type=aggregation_type,
            description=description,
            index_name=index_name,
            metric_name=metric_name,
            period=period,
            query_string=query_string,
            query_version=query_version,
            tags=tags,
            unit=unit,
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
    @jsii.member(jsii_name="aggregationField")
    def aggregation_field(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.AggregationField``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-aggregationfield
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aggregationField"))

    @aggregation_field.setter
    def aggregation_field(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "aggregationField", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aggregationType")
    def aggregation_type(
        self,
    ) -> typing.Optional[typing.Union["CfnFleetMetric.AggregationTypeProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::FleetMetric.AggregationType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-aggregationtype
        '''
        return typing.cast(typing.Optional[typing.Union["CfnFleetMetric.AggregationTypeProperty", _IResolvable_da3f097b]], jsii.get(self, "aggregationType"))

    @aggregation_type.setter
    def aggregation_type(
        self,
        value: typing.Optional[typing.Union["CfnFleetMetric.AggregationTypeProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "aggregationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrCreationDate")
    def attr_creation_date(self) -> _IResolvable_da3f097b:
        '''
        :cloudformationAttribute: CreationDate
        '''
        return typing.cast(_IResolvable_da3f097b, jsii.get(self, "attrCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrLastModifiedDate")
    def attr_last_modified_date(self) -> _IResolvable_da3f097b:
        '''
        :cloudformationAttribute: LastModifiedDate
        '''
        return typing.cast(_IResolvable_da3f097b, jsii.get(self, "attrLastModifiedDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrMetricArn")
    def attr_metric_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: MetricArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMetricArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrVersion")
    def attr_version(self) -> _IResolvable_da3f097b:
        '''
        :cloudformationAttribute: Version
        '''
        return typing.cast(_IResolvable_da3f097b, jsii.get(self, "attrVersion"))

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
        '''``AWS::IoT::FleetMetric.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="indexName")
    def index_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.IndexName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-indexname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexName"))

    @index_name.setter
    def index_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "indexName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        '''``AWS::IoT::FleetMetric.MetricName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-metricname
        '''
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        jsii.set(self, "metricName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="period")
    def period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::IoT::FleetMetric.Period``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-period
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "period"))

    @period.setter
    def period(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "period", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.QueryString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-querystring
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryString"))

    @query_string.setter
    def query_string(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "queryString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryVersion")
    def query_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.QueryVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-queryversion
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryVersion"))

    @query_version.setter
    def query_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "queryVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::FleetMetric.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unit")
    def unit(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.Unit``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-unit
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "unit", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnFleetMetric.AggregationTypeProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "values": "values"},
    )
    class AggregationTypeProperty:
        def __init__(
            self,
            *,
            name: builtins.str,
            values: typing.Sequence[builtins.str],
        ) -> None:
            '''
            :param name: ``CfnFleetMetric.AggregationTypeProperty.Name``.
            :param values: ``CfnFleetMetric.AggregationTypeProperty.Values``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-fleetmetric-aggregationtype.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                aggregation_type_property = iot.CfnFleetMetric.AggregationTypeProperty(
                    name="name",
                    values=["values"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
                "values": values,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnFleetMetric.AggregationTypeProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-fleetmetric-aggregationtype.html#cfn-iot-fleetmetric-aggregationtype-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def values(self) -> typing.List[builtins.str]:
            '''``CfnFleetMetric.AggregationTypeProperty.Values``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-fleetmetric-aggregationtype.html#cfn-iot-fleetmetric-aggregationtype-values
            '''
            result = self._values.get("values")
            assert result is not None, "Required property 'values' is missing"
            return typing.cast(typing.List[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AggregationTypeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnFleetMetricProps",
    jsii_struct_bases=[],
    name_mapping={
        "aggregation_field": "aggregationField",
        "aggregation_type": "aggregationType",
        "description": "description",
        "index_name": "indexName",
        "metric_name": "metricName",
        "period": "period",
        "query_string": "queryString",
        "query_version": "queryVersion",
        "tags": "tags",
        "unit": "unit",
    },
)
class CfnFleetMetricProps:
    def __init__(
        self,
        *,
        aggregation_field: typing.Optional[builtins.str] = None,
        aggregation_type: typing.Optional[typing.Union[CfnFleetMetric.AggregationTypeProperty, _IResolvable_da3f097b]] = None,
        description: typing.Optional[builtins.str] = None,
        index_name: typing.Optional[builtins.str] = None,
        metric_name: builtins.str,
        period: typing.Optional[jsii.Number] = None,
        query_string: typing.Optional[builtins.str] = None,
        query_version: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        unit: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::FleetMetric``.

        :param aggregation_field: ``AWS::IoT::FleetMetric.AggregationField``.
        :param aggregation_type: ``AWS::IoT::FleetMetric.AggregationType``.
        :param description: ``AWS::IoT::FleetMetric.Description``.
        :param index_name: ``AWS::IoT::FleetMetric.IndexName``.
        :param metric_name: ``AWS::IoT::FleetMetric.MetricName``.
        :param period: ``AWS::IoT::FleetMetric.Period``.
        :param query_string: ``AWS::IoT::FleetMetric.QueryString``.
        :param query_version: ``AWS::IoT::FleetMetric.QueryVersion``.
        :param tags: ``AWS::IoT::FleetMetric.Tags``.
        :param unit: ``AWS::IoT::FleetMetric.Unit``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_fleet_metric_props = iot.CfnFleetMetricProps(
                metric_name="metricName",
            
                # the properties below are optional
                aggregation_field="aggregationField",
                aggregation_type=iot.CfnFleetMetric.AggregationTypeProperty(
                    name="name",
                    values=["values"]
                ),
                description="description",
                index_name="indexName",
                period=123,
                query_string="queryString",
                query_version="queryVersion",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                unit="unit"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "metric_name": metric_name,
        }
        if aggregation_field is not None:
            self._values["aggregation_field"] = aggregation_field
        if aggregation_type is not None:
            self._values["aggregation_type"] = aggregation_type
        if description is not None:
            self._values["description"] = description
        if index_name is not None:
            self._values["index_name"] = index_name
        if period is not None:
            self._values["period"] = period
        if query_string is not None:
            self._values["query_string"] = query_string
        if query_version is not None:
            self._values["query_version"] = query_version
        if tags is not None:
            self._values["tags"] = tags
        if unit is not None:
            self._values["unit"] = unit

    @builtins.property
    def aggregation_field(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.AggregationField``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-aggregationfield
        '''
        result = self._values.get("aggregation_field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aggregation_type(
        self,
    ) -> typing.Optional[typing.Union[CfnFleetMetric.AggregationTypeProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::FleetMetric.AggregationType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-aggregationtype
        '''
        result = self._values.get("aggregation_type")
        return typing.cast(typing.Optional[typing.Union[CfnFleetMetric.AggregationTypeProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.IndexName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-indexname
        '''
        result = self._values.get("index_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''``AWS::IoT::FleetMetric.MetricName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-metricname
        '''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''``AWS::IoT::FleetMetric.Period``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-period
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def query_string(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.QueryString``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-querystring
        '''
        result = self._values.get("query_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def query_version(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.QueryVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-queryversion
        '''
        result = self._values.get("query_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::FleetMetric.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def unit(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::FleetMetric.Unit``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-fleetmetric.html#cfn-iot-fleetmetric-unit
        '''
        result = self._values.get("unit")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnFleetMetricProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnJobTemplate(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnJobTemplate",
):
    '''A CloudFormation ``AWS::IoT::JobTemplate``.

    :cloudformationResource: AWS::IoT::JobTemplate
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        # abort_config is of type object
        # job_executions_rollout_config is of type object
        # presigned_url_config is of type object
        # timeout_config is of type object
        
        cfn_job_template = iot.CfnJobTemplate(self, "MyCfnJobTemplate",
            description="description",
            job_template_id="jobTemplateId",
        
            # the properties below are optional
            abort_config=abort_config,
            document="document",
            document_source="documentSource",
            job_arn="jobArn",
            job_executions_rollout_config=job_executions_rollout_config,
            presigned_url_config=presigned_url_config,
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            timeout_config=timeout_config
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        abort_config: typing.Any = None,
        description: builtins.str,
        document: typing.Optional[builtins.str] = None,
        document_source: typing.Optional[builtins.str] = None,
        job_arn: typing.Optional[builtins.str] = None,
        job_executions_rollout_config: typing.Any = None,
        job_template_id: builtins.str,
        presigned_url_config: typing.Any = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        timeout_config: typing.Any = None,
    ) -> None:
        '''Create a new ``AWS::IoT::JobTemplate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param abort_config: ``AWS::IoT::JobTemplate.AbortConfig``.
        :param description: ``AWS::IoT::JobTemplate.Description``.
        :param document: ``AWS::IoT::JobTemplate.Document``.
        :param document_source: ``AWS::IoT::JobTemplate.DocumentSource``.
        :param job_arn: ``AWS::IoT::JobTemplate.JobArn``.
        :param job_executions_rollout_config: ``AWS::IoT::JobTemplate.JobExecutionsRolloutConfig``.
        :param job_template_id: ``AWS::IoT::JobTemplate.JobTemplateId``.
        :param presigned_url_config: ``AWS::IoT::JobTemplate.PresignedUrlConfig``.
        :param tags: ``AWS::IoT::JobTemplate.Tags``.
        :param timeout_config: ``AWS::IoT::JobTemplate.TimeoutConfig``.
        '''
        props = CfnJobTemplateProps(
            abort_config=abort_config,
            description=description,
            document=document,
            document_source=document_source,
            job_arn=job_arn,
            job_executions_rollout_config=job_executions_rollout_config,
            job_template_id=job_template_id,
            presigned_url_config=presigned_url_config,
            tags=tags,
            timeout_config=timeout_config,
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
    @jsii.member(jsii_name="abortConfig")
    def abort_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.AbortConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-abortconfig
        '''
        return typing.cast(typing.Any, jsii.get(self, "abortConfig"))

    @abort_config.setter
    def abort_config(self, value: typing.Any) -> None:
        jsii.set(self, "abortConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: Arn
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
    def description(self) -> builtins.str:
        '''``AWS::IoT::JobTemplate.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-description
        '''
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="document")
    def document(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::JobTemplate.Document``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-document
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "document"))

    @document.setter
    def document(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "document", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentSource")
    def document_source(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::JobTemplate.DocumentSource``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-documentsource
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "documentSource"))

    @document_source.setter
    def document_source(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "documentSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobArn")
    def job_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::JobTemplate.JobArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-jobarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobArn"))

    @job_arn.setter
    def job_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "jobArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobExecutionsRolloutConfig")
    def job_executions_rollout_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.JobExecutionsRolloutConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-jobexecutionsrolloutconfig
        '''
        return typing.cast(typing.Any, jsii.get(self, "jobExecutionsRolloutConfig"))

    @job_executions_rollout_config.setter
    def job_executions_rollout_config(self, value: typing.Any) -> None:
        jsii.set(self, "jobExecutionsRolloutConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobTemplateId")
    def job_template_id(self) -> builtins.str:
        '''``AWS::IoT::JobTemplate.JobTemplateId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-jobtemplateid
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobTemplateId"))

    @job_template_id.setter
    def job_template_id(self, value: builtins.str) -> None:
        jsii.set(self, "jobTemplateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="presignedUrlConfig")
    def presigned_url_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.PresignedUrlConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-presignedurlconfig
        '''
        return typing.cast(typing.Any, jsii.get(self, "presignedUrlConfig"))

    @presigned_url_config.setter
    def presigned_url_config(self, value: typing.Any) -> None:
        jsii.set(self, "presignedUrlConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::JobTemplate.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutConfig")
    def timeout_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.TimeoutConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-timeoutconfig
        '''
        return typing.cast(typing.Any, jsii.get(self, "timeoutConfig"))

    @timeout_config.setter
    def timeout_config(self, value: typing.Any) -> None:
        jsii.set(self, "timeoutConfig", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnJobTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "abort_config": "abortConfig",
        "description": "description",
        "document": "document",
        "document_source": "documentSource",
        "job_arn": "jobArn",
        "job_executions_rollout_config": "jobExecutionsRolloutConfig",
        "job_template_id": "jobTemplateId",
        "presigned_url_config": "presignedUrlConfig",
        "tags": "tags",
        "timeout_config": "timeoutConfig",
    },
)
class CfnJobTemplateProps:
    def __init__(
        self,
        *,
        abort_config: typing.Any = None,
        description: builtins.str,
        document: typing.Optional[builtins.str] = None,
        document_source: typing.Optional[builtins.str] = None,
        job_arn: typing.Optional[builtins.str] = None,
        job_executions_rollout_config: typing.Any = None,
        job_template_id: builtins.str,
        presigned_url_config: typing.Any = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        timeout_config: typing.Any = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::JobTemplate``.

        :param abort_config: ``AWS::IoT::JobTemplate.AbortConfig``.
        :param description: ``AWS::IoT::JobTemplate.Description``.
        :param document: ``AWS::IoT::JobTemplate.Document``.
        :param document_source: ``AWS::IoT::JobTemplate.DocumentSource``.
        :param job_arn: ``AWS::IoT::JobTemplate.JobArn``.
        :param job_executions_rollout_config: ``AWS::IoT::JobTemplate.JobExecutionsRolloutConfig``.
        :param job_template_id: ``AWS::IoT::JobTemplate.JobTemplateId``.
        :param presigned_url_config: ``AWS::IoT::JobTemplate.PresignedUrlConfig``.
        :param tags: ``AWS::IoT::JobTemplate.Tags``.
        :param timeout_config: ``AWS::IoT::JobTemplate.TimeoutConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            # abort_config is of type object
            # job_executions_rollout_config is of type object
            # presigned_url_config is of type object
            # timeout_config is of type object
            
            cfn_job_template_props = iot.CfnJobTemplateProps(
                description="description",
                job_template_id="jobTemplateId",
            
                # the properties below are optional
                abort_config=abort_config,
                document="document",
                document_source="documentSource",
                job_arn="jobArn",
                job_executions_rollout_config=job_executions_rollout_config,
                presigned_url_config=presigned_url_config,
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                timeout_config=timeout_config
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "job_template_id": job_template_id,
        }
        if abort_config is not None:
            self._values["abort_config"] = abort_config
        if document is not None:
            self._values["document"] = document
        if document_source is not None:
            self._values["document_source"] = document_source
        if job_arn is not None:
            self._values["job_arn"] = job_arn
        if job_executions_rollout_config is not None:
            self._values["job_executions_rollout_config"] = job_executions_rollout_config
        if presigned_url_config is not None:
            self._values["presigned_url_config"] = presigned_url_config
        if tags is not None:
            self._values["tags"] = tags
        if timeout_config is not None:
            self._values["timeout_config"] = timeout_config

    @builtins.property
    def abort_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.AbortConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-abortconfig
        '''
        result = self._values.get("abort_config")
        return typing.cast(typing.Any, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''``AWS::IoT::JobTemplate.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-description
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def document(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::JobTemplate.Document``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-document
        '''
        result = self._values.get("document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_source(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::JobTemplate.DocumentSource``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-documentsource
        '''
        result = self._values.get("document_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_arn(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::JobTemplate.JobArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-jobarn
        '''
        result = self._values.get("job_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_executions_rollout_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.JobExecutionsRolloutConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-jobexecutionsrolloutconfig
        '''
        result = self._values.get("job_executions_rollout_config")
        return typing.cast(typing.Any, result)

    @builtins.property
    def job_template_id(self) -> builtins.str:
        '''``AWS::IoT::JobTemplate.JobTemplateId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-jobtemplateid
        '''
        result = self._values.get("job_template_id")
        assert result is not None, "Required property 'job_template_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def presigned_url_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.PresignedUrlConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-presignedurlconfig
        '''
        result = self._values.get("presigned_url_config")
        return typing.cast(typing.Any, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::JobTemplate.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def timeout_config(self) -> typing.Any:
        '''``AWS::IoT::JobTemplate.TimeoutConfig``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-jobtemplate.html#cfn-iot-jobtemplate-timeoutconfig
        '''
        result = self._values.get("timeout_config")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnJobTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnLogging(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnLogging",
):
    '''A CloudFormation ``AWS::IoT::Logging``.

    :cloudformationResource: AWS::IoT::Logging
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_logging = iot.CfnLogging(self, "MyCfnLogging",
            account_id="accountId",
            default_log_level="defaultLogLevel",
            role_arn="roleArn"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        default_log_level: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::Logging``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param account_id: ``AWS::IoT::Logging.AccountId``.
        :param default_log_level: ``AWS::IoT::Logging.DefaultLogLevel``.
        :param role_arn: ``AWS::IoT::Logging.RoleArn``.
        '''
        props = CfnLoggingProps(
            account_id=account_id,
            default_log_level=default_log_level,
            role_arn=role_arn,
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
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''``AWS::IoT::Logging.AccountId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html#cfn-iot-logging-accountid
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

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
    @jsii.member(jsii_name="defaultLogLevel")
    def default_log_level(self) -> builtins.str:
        '''``AWS::IoT::Logging.DefaultLogLevel``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html#cfn-iot-logging-defaultloglevel
        '''
        return typing.cast(builtins.str, jsii.get(self, "defaultLogLevel"))

    @default_log_level.setter
    def default_log_level(self, value: builtins.str) -> None:
        jsii.set(self, "defaultLogLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''``AWS::IoT::Logging.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html#cfn-iot-logging-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnLoggingProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_id": "accountId",
        "default_log_level": "defaultLogLevel",
        "role_arn": "roleArn",
    },
)
class CfnLoggingProps:
    def __init__(
        self,
        *,
        account_id: builtins.str,
        default_log_level: builtins.str,
        role_arn: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::Logging``.

        :param account_id: ``AWS::IoT::Logging.AccountId``.
        :param default_log_level: ``AWS::IoT::Logging.DefaultLogLevel``.
        :param role_arn: ``AWS::IoT::Logging.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_logging_props = iot.CfnLoggingProps(
                account_id="accountId",
                default_log_level="defaultLogLevel",
                role_arn="roleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "default_log_level": default_log_level,
            "role_arn": role_arn,
        }

    @builtins.property
    def account_id(self) -> builtins.str:
        '''``AWS::IoT::Logging.AccountId``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html#cfn-iot-logging-accountid
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_log_level(self) -> builtins.str:
        '''``AWS::IoT::Logging.DefaultLogLevel``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html#cfn-iot-logging-defaultloglevel
        '''
        result = self._values.get("default_log_level")
        assert result is not None, "Required property 'default_log_level' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''``AWS::IoT::Logging.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-logging.html#cfn-iot-logging-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnLoggingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnMitigationAction(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction",
):
    '''A CloudFormation ``AWS::IoT::MitigationAction``.

    :cloudformationResource: AWS::IoT::MitigationAction
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_mitigation_action = iot.CfnMitigationAction(self, "MyCfnMitigationAction",
            action_params=iot.CfnMitigationAction.ActionParamsProperty(
                add_things_to_thing_group_params=iot.CfnMitigationAction.AddThingsToThingGroupParamsProperty(
                    thing_group_names=["thingGroupNames"],
        
                    # the properties below are optional
                    override_dynamic_groups=False
                ),
                enable_io_tLogging_params=iot.CfnMitigationAction.EnableIoTLoggingParamsProperty(
                    log_level="logLevel",
                    role_arn_for_logging="roleArnForLogging"
                ),
                publish_finding_to_sns_params=iot.CfnMitigationAction.PublishFindingToSnsParamsProperty(
                    topic_arn="topicArn"
                ),
                replace_default_policy_version_params=iot.CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty(
                    template_name="templateName"
                ),
                update_ca_certificate_params=iot.CfnMitigationAction.UpdateCACertificateParamsProperty(
                    action="action"
                ),
                update_device_certificate_params=iot.CfnMitigationAction.UpdateDeviceCertificateParamsProperty(
                    action="action"
                )
            ),
            role_arn="roleArn",
        
            # the properties below are optional
            action_name="actionName",
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
        action_name: typing.Optional[builtins.str] = None,
        action_params: typing.Union["CfnMitigationAction.ActionParamsProperty", _IResolvable_da3f097b],
        role_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::MitigationAction``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param action_name: ``AWS::IoT::MitigationAction.ActionName``.
        :param action_params: ``AWS::IoT::MitigationAction.ActionParams``.
        :param role_arn: ``AWS::IoT::MitigationAction.RoleArn``.
        :param tags: ``AWS::IoT::MitigationAction.Tags``.
        '''
        props = CfnMitigationActionProps(
            action_name=action_name,
            action_params=action_params,
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionName")
    def action_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::MitigationAction.ActionName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-actionname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionName"))

    @action_name.setter
    def action_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "actionName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionParams")
    def action_params(
        self,
    ) -> typing.Union["CfnMitigationAction.ActionParamsProperty", _IResolvable_da3f097b]:
        '''``AWS::IoT::MitigationAction.ActionParams``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-actionparams
        '''
        return typing.cast(typing.Union["CfnMitigationAction.ActionParamsProperty", _IResolvable_da3f097b], jsii.get(self, "actionParams"))

    @action_params.setter
    def action_params(
        self,
        value: typing.Union["CfnMitigationAction.ActionParamsProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "actionParams", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrMitigationActionArn")
    def attr_mitigation_action_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: MitigationActionArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMitigationActionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrMitigationActionId")
    def attr_mitigation_action_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: MitigationActionId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrMitigationActionId"))

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
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''``AWS::IoT::MitigationAction.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::MitigationAction.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.ActionParamsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "add_things_to_thing_group_params": "addThingsToThingGroupParams",
            "enable_io_t_logging_params": "enableIoTLoggingParams",
            "publish_finding_to_sns_params": "publishFindingToSnsParams",
            "replace_default_policy_version_params": "replaceDefaultPolicyVersionParams",
            "update_ca_certificate_params": "updateCaCertificateParams",
            "update_device_certificate_params": "updateDeviceCertificateParams",
        },
    )
    class ActionParamsProperty:
        def __init__(
            self,
            *,
            add_things_to_thing_group_params: typing.Optional[typing.Union["CfnMitigationAction.AddThingsToThingGroupParamsProperty", _IResolvable_da3f097b]] = None,
            enable_io_t_logging_params: typing.Optional[typing.Union["CfnMitigationAction.EnableIoTLoggingParamsProperty", _IResolvable_da3f097b]] = None,
            publish_finding_to_sns_params: typing.Optional[typing.Union["CfnMitigationAction.PublishFindingToSnsParamsProperty", _IResolvable_da3f097b]] = None,
            replace_default_policy_version_params: typing.Optional[typing.Union["CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty", _IResolvable_da3f097b]] = None,
            update_ca_certificate_params: typing.Optional[typing.Union["CfnMitigationAction.UpdateCACertificateParamsProperty", _IResolvable_da3f097b]] = None,
            update_device_certificate_params: typing.Optional[typing.Union["CfnMitigationAction.UpdateDeviceCertificateParamsProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param add_things_to_thing_group_params: ``CfnMitigationAction.ActionParamsProperty.AddThingsToThingGroupParams``.
            :param enable_io_t_logging_params: ``CfnMitigationAction.ActionParamsProperty.EnableIoTLoggingParams``.
            :param publish_finding_to_sns_params: ``CfnMitigationAction.ActionParamsProperty.PublishFindingToSnsParams``.
            :param replace_default_policy_version_params: ``CfnMitigationAction.ActionParamsProperty.ReplaceDefaultPolicyVersionParams``.
            :param update_ca_certificate_params: ``CfnMitigationAction.ActionParamsProperty.UpdateCACertificateParams``.
            :param update_device_certificate_params: ``CfnMitigationAction.ActionParamsProperty.UpdateDeviceCertificateParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                action_params_property = iot.CfnMitigationAction.ActionParamsProperty(
                    add_things_to_thing_group_params=iot.CfnMitigationAction.AddThingsToThingGroupParamsProperty(
                        thing_group_names=["thingGroupNames"],
                
                        # the properties below are optional
                        override_dynamic_groups=False
                    ),
                    enable_io_tLogging_params=iot.CfnMitigationAction.EnableIoTLoggingParamsProperty(
                        log_level="logLevel",
                        role_arn_for_logging="roleArnForLogging"
                    ),
                    publish_finding_to_sns_params=iot.CfnMitigationAction.PublishFindingToSnsParamsProperty(
                        topic_arn="topicArn"
                    ),
                    replace_default_policy_version_params=iot.CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty(
                        template_name="templateName"
                    ),
                    update_ca_certificate_params=iot.CfnMitigationAction.UpdateCACertificateParamsProperty(
                        action="action"
                    ),
                    update_device_certificate_params=iot.CfnMitigationAction.UpdateDeviceCertificateParamsProperty(
                        action="action"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if add_things_to_thing_group_params is not None:
                self._values["add_things_to_thing_group_params"] = add_things_to_thing_group_params
            if enable_io_t_logging_params is not None:
                self._values["enable_io_t_logging_params"] = enable_io_t_logging_params
            if publish_finding_to_sns_params is not None:
                self._values["publish_finding_to_sns_params"] = publish_finding_to_sns_params
            if replace_default_policy_version_params is not None:
                self._values["replace_default_policy_version_params"] = replace_default_policy_version_params
            if update_ca_certificate_params is not None:
                self._values["update_ca_certificate_params"] = update_ca_certificate_params
            if update_device_certificate_params is not None:
                self._values["update_device_certificate_params"] = update_device_certificate_params

        @builtins.property
        def add_things_to_thing_group_params(
            self,
        ) -> typing.Optional[typing.Union["CfnMitigationAction.AddThingsToThingGroupParamsProperty", _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.ActionParamsProperty.AddThingsToThingGroupParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html#cfn-iot-mitigationaction-actionparams-addthingstothinggroupparams
            '''
            result = self._values.get("add_things_to_thing_group_params")
            return typing.cast(typing.Optional[typing.Union["CfnMitigationAction.AddThingsToThingGroupParamsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def enable_io_t_logging_params(
            self,
        ) -> typing.Optional[typing.Union["CfnMitigationAction.EnableIoTLoggingParamsProperty", _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.ActionParamsProperty.EnableIoTLoggingParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html#cfn-iot-mitigationaction-actionparams-enableiotloggingparams
            '''
            result = self._values.get("enable_io_t_logging_params")
            return typing.cast(typing.Optional[typing.Union["CfnMitigationAction.EnableIoTLoggingParamsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def publish_finding_to_sns_params(
            self,
        ) -> typing.Optional[typing.Union["CfnMitigationAction.PublishFindingToSnsParamsProperty", _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.ActionParamsProperty.PublishFindingToSnsParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html#cfn-iot-mitigationaction-actionparams-publishfindingtosnsparams
            '''
            result = self._values.get("publish_finding_to_sns_params")
            return typing.cast(typing.Optional[typing.Union["CfnMitigationAction.PublishFindingToSnsParamsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def replace_default_policy_version_params(
            self,
        ) -> typing.Optional[typing.Union["CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty", _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.ActionParamsProperty.ReplaceDefaultPolicyVersionParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html#cfn-iot-mitigationaction-actionparams-replacedefaultpolicyversionparams
            '''
            result = self._values.get("replace_default_policy_version_params")
            return typing.cast(typing.Optional[typing.Union["CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def update_ca_certificate_params(
            self,
        ) -> typing.Optional[typing.Union["CfnMitigationAction.UpdateCACertificateParamsProperty", _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.ActionParamsProperty.UpdateCACertificateParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html#cfn-iot-mitigationaction-actionparams-updatecacertificateparams
            '''
            result = self._values.get("update_ca_certificate_params")
            return typing.cast(typing.Optional[typing.Union["CfnMitigationAction.UpdateCACertificateParamsProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def update_device_certificate_params(
            self,
        ) -> typing.Optional[typing.Union["CfnMitigationAction.UpdateDeviceCertificateParamsProperty", _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.ActionParamsProperty.UpdateDeviceCertificateParams``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-actionparams.html#cfn-iot-mitigationaction-actionparams-updatedevicecertificateparams
            '''
            result = self._values.get("update_device_certificate_params")
            return typing.cast(typing.Optional[typing.Union["CfnMitigationAction.UpdateDeviceCertificateParamsProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.AddThingsToThingGroupParamsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "override_dynamic_groups": "overrideDynamicGroups",
            "thing_group_names": "thingGroupNames",
        },
    )
    class AddThingsToThingGroupParamsProperty:
        def __init__(
            self,
            *,
            override_dynamic_groups: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            thing_group_names: typing.Sequence[builtins.str],
        ) -> None:
            '''
            :param override_dynamic_groups: ``CfnMitigationAction.AddThingsToThingGroupParamsProperty.OverrideDynamicGroups``.
            :param thing_group_names: ``CfnMitigationAction.AddThingsToThingGroupParamsProperty.ThingGroupNames``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-addthingstothinggroupparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                add_things_to_thing_group_params_property = iot.CfnMitigationAction.AddThingsToThingGroupParamsProperty(
                    thing_group_names=["thingGroupNames"],
                
                    # the properties below are optional
                    override_dynamic_groups=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "thing_group_names": thing_group_names,
            }
            if override_dynamic_groups is not None:
                self._values["override_dynamic_groups"] = override_dynamic_groups

        @builtins.property
        def override_dynamic_groups(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnMitigationAction.AddThingsToThingGroupParamsProperty.OverrideDynamicGroups``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-addthingstothinggroupparams.html#cfn-iot-mitigationaction-addthingstothinggroupparams-overridedynamicgroups
            '''
            result = self._values.get("override_dynamic_groups")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def thing_group_names(self) -> typing.List[builtins.str]:
            '''``CfnMitigationAction.AddThingsToThingGroupParamsProperty.ThingGroupNames``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-addthingstothinggroupparams.html#cfn-iot-mitigationaction-addthingstothinggroupparams-thinggroupnames
            '''
            result = self._values.get("thing_group_names")
            assert result is not None, "Required property 'thing_group_names' is missing"
            return typing.cast(typing.List[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AddThingsToThingGroupParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.EnableIoTLoggingParamsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "log_level": "logLevel",
            "role_arn_for_logging": "roleArnForLogging",
        },
    )
    class EnableIoTLoggingParamsProperty:
        def __init__(
            self,
            *,
            log_level: builtins.str,
            role_arn_for_logging: builtins.str,
        ) -> None:
            '''
            :param log_level: ``CfnMitigationAction.EnableIoTLoggingParamsProperty.LogLevel``.
            :param role_arn_for_logging: ``CfnMitigationAction.EnableIoTLoggingParamsProperty.RoleArnForLogging``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-enableiotloggingparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                enable_io_tLogging_params_property = iot.CfnMitigationAction.EnableIoTLoggingParamsProperty(
                    log_level="logLevel",
                    role_arn_for_logging="roleArnForLogging"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "log_level": log_level,
                "role_arn_for_logging": role_arn_for_logging,
            }

        @builtins.property
        def log_level(self) -> builtins.str:
            '''``CfnMitigationAction.EnableIoTLoggingParamsProperty.LogLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-enableiotloggingparams.html#cfn-iot-mitigationaction-enableiotloggingparams-loglevel
            '''
            result = self._values.get("log_level")
            assert result is not None, "Required property 'log_level' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn_for_logging(self) -> builtins.str:
            '''``CfnMitigationAction.EnableIoTLoggingParamsProperty.RoleArnForLogging``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-enableiotloggingparams.html#cfn-iot-mitigationaction-enableiotloggingparams-rolearnforlogging
            '''
            result = self._values.get("role_arn_for_logging")
            assert result is not None, "Required property 'role_arn_for_logging' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EnableIoTLoggingParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.PublishFindingToSnsParamsProperty",
        jsii_struct_bases=[],
        name_mapping={"topic_arn": "topicArn"},
    )
    class PublishFindingToSnsParamsProperty:
        def __init__(self, *, topic_arn: builtins.str) -> None:
            '''
            :param topic_arn: ``CfnMitigationAction.PublishFindingToSnsParamsProperty.TopicArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-publishfindingtosnsparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                publish_finding_to_sns_params_property = iot.CfnMitigationAction.PublishFindingToSnsParamsProperty(
                    topic_arn="topicArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "topic_arn": topic_arn,
            }

        @builtins.property
        def topic_arn(self) -> builtins.str:
            '''``CfnMitigationAction.PublishFindingToSnsParamsProperty.TopicArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-publishfindingtosnsparams.html#cfn-iot-mitigationaction-publishfindingtosnsparams-topicarn
            '''
            result = self._values.get("topic_arn")
            assert result is not None, "Required property 'topic_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PublishFindingToSnsParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty",
        jsii_struct_bases=[],
        name_mapping={"template_name": "templateName"},
    )
    class ReplaceDefaultPolicyVersionParamsProperty:
        def __init__(self, *, template_name: builtins.str) -> None:
            '''
            :param template_name: ``CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty.TemplateName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-replacedefaultpolicyversionparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                replace_default_policy_version_params_property = iot.CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty(
                    template_name="templateName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "template_name": template_name,
            }

        @builtins.property
        def template_name(self) -> builtins.str:
            '''``CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty.TemplateName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-replacedefaultpolicyversionparams.html#cfn-iot-mitigationaction-replacedefaultpolicyversionparams-templatename
            '''
            result = self._values.get("template_name")
            assert result is not None, "Required property 'template_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ReplaceDefaultPolicyVersionParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.UpdateCACertificateParamsProperty",
        jsii_struct_bases=[],
        name_mapping={"action": "action"},
    )
    class UpdateCACertificateParamsProperty:
        def __init__(self, *, action: builtins.str) -> None:
            '''
            :param action: ``CfnMitigationAction.UpdateCACertificateParamsProperty.Action``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-updatecacertificateparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                update_cACertificate_params_property = iot.CfnMitigationAction.UpdateCACertificateParamsProperty(
                    action="action"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "action": action,
            }

        @builtins.property
        def action(self) -> builtins.str:
            '''``CfnMitigationAction.UpdateCACertificateParamsProperty.Action``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-updatecacertificateparams.html#cfn-iot-mitigationaction-updatecacertificateparams-action
            '''
            result = self._values.get("action")
            assert result is not None, "Required property 'action' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "UpdateCACertificateParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnMitigationAction.UpdateDeviceCertificateParamsProperty",
        jsii_struct_bases=[],
        name_mapping={"action": "action"},
    )
    class UpdateDeviceCertificateParamsProperty:
        def __init__(self, *, action: builtins.str) -> None:
            '''
            :param action: ``CfnMitigationAction.UpdateDeviceCertificateParamsProperty.Action``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-updatedevicecertificateparams.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                update_device_certificate_params_property = iot.CfnMitigationAction.UpdateDeviceCertificateParamsProperty(
                    action="action"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "action": action,
            }

        @builtins.property
        def action(self) -> builtins.str:
            '''``CfnMitigationAction.UpdateDeviceCertificateParamsProperty.Action``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-mitigationaction-updatedevicecertificateparams.html#cfn-iot-mitigationaction-updatedevicecertificateparams-action
            '''
            result = self._values.get("action")
            assert result is not None, "Required property 'action' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "UpdateDeviceCertificateParamsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnMitigationActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "action_name": "actionName",
        "action_params": "actionParams",
        "role_arn": "roleArn",
        "tags": "tags",
    },
)
class CfnMitigationActionProps:
    def __init__(
        self,
        *,
        action_name: typing.Optional[builtins.str] = None,
        action_params: typing.Union[CfnMitigationAction.ActionParamsProperty, _IResolvable_da3f097b],
        role_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::MitigationAction``.

        :param action_name: ``AWS::IoT::MitigationAction.ActionName``.
        :param action_params: ``AWS::IoT::MitigationAction.ActionParams``.
        :param role_arn: ``AWS::IoT::MitigationAction.RoleArn``.
        :param tags: ``AWS::IoT::MitigationAction.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_mitigation_action_props = iot.CfnMitigationActionProps(
                action_params=iot.CfnMitigationAction.ActionParamsProperty(
                    add_things_to_thing_group_params=iot.CfnMitigationAction.AddThingsToThingGroupParamsProperty(
                        thing_group_names=["thingGroupNames"],
            
                        # the properties below are optional
                        override_dynamic_groups=False
                    ),
                    enable_io_tLogging_params=iot.CfnMitigationAction.EnableIoTLoggingParamsProperty(
                        log_level="logLevel",
                        role_arn_for_logging="roleArnForLogging"
                    ),
                    publish_finding_to_sns_params=iot.CfnMitigationAction.PublishFindingToSnsParamsProperty(
                        topic_arn="topicArn"
                    ),
                    replace_default_policy_version_params=iot.CfnMitigationAction.ReplaceDefaultPolicyVersionParamsProperty(
                        template_name="templateName"
                    ),
                    update_ca_certificate_params=iot.CfnMitigationAction.UpdateCACertificateParamsProperty(
                        action="action"
                    ),
                    update_device_certificate_params=iot.CfnMitigationAction.UpdateDeviceCertificateParamsProperty(
                        action="action"
                    )
                ),
                role_arn="roleArn",
            
                # the properties below are optional
                action_name="actionName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_params": action_params,
            "role_arn": role_arn,
        }
        if action_name is not None:
            self._values["action_name"] = action_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def action_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::MitigationAction.ActionName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-actionname
        '''
        result = self._values.get("action_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def action_params(
        self,
    ) -> typing.Union[CfnMitigationAction.ActionParamsProperty, _IResolvable_da3f097b]:
        '''``AWS::IoT::MitigationAction.ActionParams``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-actionparams
        '''
        result = self._values.get("action_params")
        assert result is not None, "Required property 'action_params' is missing"
        return typing.cast(typing.Union[CfnMitigationAction.ActionParamsProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''``AWS::IoT::MitigationAction.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::MitigationAction.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-mitigationaction.html#cfn-iot-mitigationaction-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnMitigationActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnPolicy(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnPolicy",
):
    '''A CloudFormation ``AWS::IoT::Policy``.

    :cloudformationResource: AWS::IoT::Policy
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        # policy_document is of type object
        
        cfn_policy = iot.CfnPolicy(self, "MyCfnPolicy",
            policy_document=policy_document,
        
            # the properties below are optional
            policy_name="policyName"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_document: typing.Any,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::Policy``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param policy_document: ``AWS::IoT::Policy.PolicyDocument``.
        :param policy_name: ``AWS::IoT::Policy.PolicyName``.
        '''
        props = CfnPolicyProps(
            policy_document=policy_document, policy_name=policy_name
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
    @jsii.member(jsii_name="policyDocument")
    def policy_document(self) -> typing.Any:
        '''``AWS::IoT::Policy.PolicyDocument``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
        '''
        return typing.cast(typing.Any, jsii.get(self, "policyDocument"))

    @policy_document.setter
    def policy_document(self, value: typing.Any) -> None:
        jsii.set(self, "policyDocument", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Policy.PolicyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "policyName", value)


@jsii.implements(_IInspectable_c2943556)
class CfnPolicyPrincipalAttachment(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnPolicyPrincipalAttachment",
):
    '''A CloudFormation ``AWS::IoT::PolicyPrincipalAttachment``.

    :cloudformationResource: AWS::IoT::PolicyPrincipalAttachment
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_policy_principal_attachment = iot.CfnPolicyPrincipalAttachment(self, "MyCfnPolicyPrincipalAttachment",
            policy_name="policyName",
            principal="principal"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_name: builtins.str,
        principal: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::PolicyPrincipalAttachment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param policy_name: ``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.
        :param principal: ``AWS::IoT::PolicyPrincipalAttachment.Principal``.
        '''
        props = CfnPolicyPrincipalAttachmentProps(
            policy_name=policy_name, principal=principal
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
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        '''``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        jsii.set(self, "policyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        '''``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
        '''
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        jsii.set(self, "principal", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnPolicyPrincipalAttachmentProps",
    jsii_struct_bases=[],
    name_mapping={"policy_name": "policyName", "principal": "principal"},
)
class CfnPolicyPrincipalAttachmentProps:
    def __init__(self, *, policy_name: builtins.str, principal: builtins.str) -> None:
        '''Properties for defining a ``AWS::IoT::PolicyPrincipalAttachment``.

        :param policy_name: ``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.
        :param principal: ``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_policy_principal_attachment_props = iot.CfnPolicyPrincipalAttachmentProps(
                policy_name="policyName",
                principal="principal"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy_name": policy_name,
            "principal": principal,
        }

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''``AWS::IoT::PolicyPrincipalAttachment.PolicyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-policyname
        '''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def principal(self) -> builtins.str:
        '''``AWS::IoT::PolicyPrincipalAttachment.Principal``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policyprincipalattachment.html#cfn-iot-policyprincipalattachment-principal
        '''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPolicyPrincipalAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnPolicyProps",
    jsii_struct_bases=[],
    name_mapping={"policy_document": "policyDocument", "policy_name": "policyName"},
)
class CfnPolicyProps:
    def __init__(
        self,
        *,
        policy_document: typing.Any,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::Policy``.

        :param policy_document: ``AWS::IoT::Policy.PolicyDocument``.
        :param policy_name: ``AWS::IoT::Policy.PolicyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            # policy_document is of type object
            
            cfn_policy_props = iot.CfnPolicyProps(
                policy_document=policy_document,
            
                # the properties below are optional
                policy_name="policyName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy_document": policy_document,
        }
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def policy_document(self) -> typing.Any:
        '''``AWS::IoT::Policy.PolicyDocument``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policydocument
        '''
        result = self._values.get("policy_document")
        assert result is not None, "Required property 'policy_document' is missing"
        return typing.cast(typing.Any, result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Policy.PolicyName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-policy.html#cfn-iot-policy-policyname
        '''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnProvisioningTemplate(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnProvisioningTemplate",
):
    '''A CloudFormation ``AWS::IoT::ProvisioningTemplate``.

    :cloudformationResource: AWS::IoT::ProvisioningTemplate
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_provisioning_template = iot.CfnProvisioningTemplate(self, "MyCfnProvisioningTemplate",
            provisioning_role_arn="provisioningRoleArn",
            template_body="templateBody",
        
            # the properties below are optional
            description="description",
            enabled=False,
            pre_provisioning_hook=iot.CfnProvisioningTemplate.ProvisioningHookProperty(
                payload_version="payloadVersion",
                target_arn="targetArn"
            ),
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            template_name="templateName"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        pre_provisioning_hook: typing.Optional[typing.Union["CfnProvisioningTemplate.ProvisioningHookProperty", _IResolvable_da3f097b]] = None,
        provisioning_role_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        template_body: builtins.str,
        template_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::ProvisioningTemplate``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param description: ``AWS::IoT::ProvisioningTemplate.Description``.
        :param enabled: ``AWS::IoT::ProvisioningTemplate.Enabled``.
        :param pre_provisioning_hook: ``AWS::IoT::ProvisioningTemplate.PreProvisioningHook``.
        :param provisioning_role_arn: ``AWS::IoT::ProvisioningTemplate.ProvisioningRoleArn``.
        :param tags: ``AWS::IoT::ProvisioningTemplate.Tags``.
        :param template_body: ``AWS::IoT::ProvisioningTemplate.TemplateBody``.
        :param template_name: ``AWS::IoT::ProvisioningTemplate.TemplateName``.
        '''
        props = CfnProvisioningTemplateProps(
            description=description,
            enabled=enabled,
            pre_provisioning_hook=pre_provisioning_hook,
            provisioning_role_arn=provisioning_role_arn,
            tags=tags,
            template_body=template_body,
            template_name=template_name,
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
    @jsii.member(jsii_name="attrTemplateArn")
    def attr_template_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: TemplateArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrTemplateArn"))

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
        '''``AWS::IoT::ProvisioningTemplate.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::IoT::ProvisioningTemplate.Enabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-enabled
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preProvisioningHook")
    def pre_provisioning_hook(
        self,
    ) -> typing.Optional[typing.Union["CfnProvisioningTemplate.ProvisioningHookProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::ProvisioningTemplate.PreProvisioningHook``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-preprovisioninghook
        '''
        return typing.cast(typing.Optional[typing.Union["CfnProvisioningTemplate.ProvisioningHookProperty", _IResolvable_da3f097b]], jsii.get(self, "preProvisioningHook"))

    @pre_provisioning_hook.setter
    def pre_provisioning_hook(
        self,
        value: typing.Optional[typing.Union["CfnProvisioningTemplate.ProvisioningHookProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "preProvisioningHook", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provisioningRoleArn")
    def provisioning_role_arn(self) -> builtins.str:
        '''``AWS::IoT::ProvisioningTemplate.ProvisioningRoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-provisioningrolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "provisioningRoleArn"))

    @provisioning_role_arn.setter
    def provisioning_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "provisioningRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::ProvisioningTemplate.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> builtins.str:
        '''``AWS::IoT::ProvisioningTemplate.TemplateBody``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-templatebody
        '''
        return typing.cast(builtins.str, jsii.get(self, "templateBody"))

    @template_body.setter
    def template_body(self, value: builtins.str) -> None:
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateName")
    def template_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ProvisioningTemplate.TemplateName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-templatename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateName"))

    @template_name.setter
    def template_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "templateName", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnProvisioningTemplate.ProvisioningHookProperty",
        jsii_struct_bases=[],
        name_mapping={"payload_version": "payloadVersion", "target_arn": "targetArn"},
    )
    class ProvisioningHookProperty:
        def __init__(
            self,
            *,
            payload_version: typing.Optional[builtins.str] = None,
            target_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param payload_version: ``CfnProvisioningTemplate.ProvisioningHookProperty.PayloadVersion``.
            :param target_arn: ``CfnProvisioningTemplate.ProvisioningHookProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-provisioningtemplate-provisioninghook.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                provisioning_hook_property = iot.CfnProvisioningTemplate.ProvisioningHookProperty(
                    payload_version="payloadVersion",
                    target_arn="targetArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if payload_version is not None:
                self._values["payload_version"] = payload_version
            if target_arn is not None:
                self._values["target_arn"] = target_arn

        @builtins.property
        def payload_version(self) -> typing.Optional[builtins.str]:
            '''``CfnProvisioningTemplate.ProvisioningHookProperty.PayloadVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-provisioningtemplate-provisioninghook.html#cfn-iot-provisioningtemplate-provisioninghook-payloadversion
            '''
            result = self._values.get("payload_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def target_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnProvisioningTemplate.ProvisioningHookProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-provisioningtemplate-provisioninghook.html#cfn-iot-provisioningtemplate-provisioninghook-targetarn
            '''
            result = self._values.get("target_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ProvisioningHookProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnProvisioningTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "enabled": "enabled",
        "pre_provisioning_hook": "preProvisioningHook",
        "provisioning_role_arn": "provisioningRoleArn",
        "tags": "tags",
        "template_body": "templateBody",
        "template_name": "templateName",
    },
)
class CfnProvisioningTemplateProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        pre_provisioning_hook: typing.Optional[typing.Union[CfnProvisioningTemplate.ProvisioningHookProperty, _IResolvable_da3f097b]] = None,
        provisioning_role_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        template_body: builtins.str,
        template_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::ProvisioningTemplate``.

        :param description: ``AWS::IoT::ProvisioningTemplate.Description``.
        :param enabled: ``AWS::IoT::ProvisioningTemplate.Enabled``.
        :param pre_provisioning_hook: ``AWS::IoT::ProvisioningTemplate.PreProvisioningHook``.
        :param provisioning_role_arn: ``AWS::IoT::ProvisioningTemplate.ProvisioningRoleArn``.
        :param tags: ``AWS::IoT::ProvisioningTemplate.Tags``.
        :param template_body: ``AWS::IoT::ProvisioningTemplate.TemplateBody``.
        :param template_name: ``AWS::IoT::ProvisioningTemplate.TemplateName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_provisioning_template_props = iot.CfnProvisioningTemplateProps(
                provisioning_role_arn="provisioningRoleArn",
                template_body="templateBody",
            
                # the properties below are optional
                description="description",
                enabled=False,
                pre_provisioning_hook=iot.CfnProvisioningTemplate.ProvisioningHookProperty(
                    payload_version="payloadVersion",
                    target_arn="targetArn"
                ),
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                template_name="templateName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "provisioning_role_arn": provisioning_role_arn,
            "template_body": template_body,
        }
        if description is not None:
            self._values["description"] = description
        if enabled is not None:
            self._values["enabled"] = enabled
        if pre_provisioning_hook is not None:
            self._values["pre_provisioning_hook"] = pre_provisioning_hook
        if tags is not None:
            self._values["tags"] = tags
        if template_name is not None:
            self._values["template_name"] = template_name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ProvisioningTemplate.Description``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::IoT::ProvisioningTemplate.Enabled``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-enabled
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def pre_provisioning_hook(
        self,
    ) -> typing.Optional[typing.Union[CfnProvisioningTemplate.ProvisioningHookProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::ProvisioningTemplate.PreProvisioningHook``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-preprovisioninghook
        '''
        result = self._values.get("pre_provisioning_hook")
        return typing.cast(typing.Optional[typing.Union[CfnProvisioningTemplate.ProvisioningHookProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def provisioning_role_arn(self) -> builtins.str:
        '''``AWS::IoT::ProvisioningTemplate.ProvisioningRoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-provisioningrolearn
        '''
        result = self._values.get("provisioning_role_arn")
        assert result is not None, "Required property 'provisioning_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::ProvisioningTemplate.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def template_body(self) -> builtins.str:
        '''``AWS::IoT::ProvisioningTemplate.TemplateBody``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-templatebody
        '''
        result = self._values.get("template_body")
        assert result is not None, "Required property 'template_body' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ProvisioningTemplate.TemplateName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-provisioningtemplate.html#cfn-iot-provisioningtemplate-templatename
        '''
        result = self._values.get("template_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnProvisioningTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnResourceSpecificLogging(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnResourceSpecificLogging",
):
    '''A CloudFormation ``AWS::IoT::ResourceSpecificLogging``.

    :cloudformationResource: AWS::IoT::ResourceSpecificLogging
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_resource_specific_logging = iot.CfnResourceSpecificLogging(self, "MyCfnResourceSpecificLogging",
            log_level="logLevel",
            target_name="targetName",
            target_type="targetType"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        log_level: builtins.str,
        target_name: builtins.str,
        target_type: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::ResourceSpecificLogging``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param log_level: ``AWS::IoT::ResourceSpecificLogging.LogLevel``.
        :param target_name: ``AWS::IoT::ResourceSpecificLogging.TargetName``.
        :param target_type: ``AWS::IoT::ResourceSpecificLogging.TargetType``.
        '''
        props = CfnResourceSpecificLoggingProps(
            log_level=log_level, target_name=target_name, target_type=target_type
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
    @jsii.member(jsii_name="attrTargetId")
    def attr_target_id(self) -> builtins.str:
        '''
        :cloudformationAttribute: TargetId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrTargetId"))

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
    @jsii.member(jsii_name="logLevel")
    def log_level(self) -> builtins.str:
        '''``AWS::IoT::ResourceSpecificLogging.LogLevel``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html#cfn-iot-resourcespecificlogging-loglevel
        '''
        return typing.cast(builtins.str, jsii.get(self, "logLevel"))

    @log_level.setter
    def log_level(self, value: builtins.str) -> None:
        jsii.set(self, "logLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        '''``AWS::IoT::ResourceSpecificLogging.TargetName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html#cfn-iot-resourcespecificlogging-targetname
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        jsii.set(self, "targetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetType")
    def target_type(self) -> builtins.str:
        '''``AWS::IoT::ResourceSpecificLogging.TargetType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html#cfn-iot-resourcespecificlogging-targettype
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetType"))

    @target_type.setter
    def target_type(self, value: builtins.str) -> None:
        jsii.set(self, "targetType", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnResourceSpecificLoggingProps",
    jsii_struct_bases=[],
    name_mapping={
        "log_level": "logLevel",
        "target_name": "targetName",
        "target_type": "targetType",
    },
)
class CfnResourceSpecificLoggingProps:
    def __init__(
        self,
        *,
        log_level: builtins.str,
        target_name: builtins.str,
        target_type: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::ResourceSpecificLogging``.

        :param log_level: ``AWS::IoT::ResourceSpecificLogging.LogLevel``.
        :param target_name: ``AWS::IoT::ResourceSpecificLogging.TargetName``.
        :param target_type: ``AWS::IoT::ResourceSpecificLogging.TargetType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_resource_specific_logging_props = iot.CfnResourceSpecificLoggingProps(
                log_level="logLevel",
                target_name="targetName",
                target_type="targetType"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "log_level": log_level,
            "target_name": target_name,
            "target_type": target_type,
        }

    @builtins.property
    def log_level(self) -> builtins.str:
        '''``AWS::IoT::ResourceSpecificLogging.LogLevel``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html#cfn-iot-resourcespecificlogging-loglevel
        '''
        result = self._values.get("log_level")
        assert result is not None, "Required property 'log_level' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''``AWS::IoT::ResourceSpecificLogging.TargetName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html#cfn-iot-resourcespecificlogging-targetname
        '''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_type(self) -> builtins.str:
        '''``AWS::IoT::ResourceSpecificLogging.TargetType``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-resourcespecificlogging.html#cfn-iot-resourcespecificlogging-targettype
        '''
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnResourceSpecificLoggingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnScheduledAudit(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnScheduledAudit",
):
    '''A CloudFormation ``AWS::IoT::ScheduledAudit``.

    :cloudformationResource: AWS::IoT::ScheduledAudit
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_scheduled_audit = iot.CfnScheduledAudit(self, "MyCfnScheduledAudit",
            frequency="frequency",
            target_check_names=["targetCheckNames"],
        
            # the properties below are optional
            day_of_month="dayOfMonth",
            day_of_week="dayOfWeek",
            scheduled_audit_name="scheduledAuditName",
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
        day_of_month: typing.Optional[builtins.str] = None,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: builtins.str,
        scheduled_audit_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        target_check_names: typing.Sequence[builtins.str],
    ) -> None:
        '''Create a new ``AWS::IoT::ScheduledAudit``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param day_of_month: ``AWS::IoT::ScheduledAudit.DayOfMonth``.
        :param day_of_week: ``AWS::IoT::ScheduledAudit.DayOfWeek``.
        :param frequency: ``AWS::IoT::ScheduledAudit.Frequency``.
        :param scheduled_audit_name: ``AWS::IoT::ScheduledAudit.ScheduledAuditName``.
        :param tags: ``AWS::IoT::ScheduledAudit.Tags``.
        :param target_check_names: ``AWS::IoT::ScheduledAudit.TargetCheckNames``.
        '''
        props = CfnScheduledAuditProps(
            day_of_month=day_of_month,
            day_of_week=day_of_week,
            frequency=frequency,
            scheduled_audit_name=scheduled_audit_name,
            tags=tags,
            target_check_names=target_check_names,
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
    @jsii.member(jsii_name="attrScheduledAuditArn")
    def attr_scheduled_audit_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: ScheduledAuditArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrScheduledAuditArn"))

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
    @jsii.member(jsii_name="dayOfMonth")
    def day_of_month(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.DayOfMonth``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-dayofmonth
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfMonth"))

    @day_of_month.setter
    def day_of_month(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dayOfMonth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.DayOfWeek``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-dayofweek
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dayOfWeek", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> builtins.str:
        '''``AWS::IoT::ScheduledAudit.Frequency``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-frequency
        '''
        return typing.cast(builtins.str, jsii.get(self, "frequency"))

    @frequency.setter
    def frequency(self, value: builtins.str) -> None:
        jsii.set(self, "frequency", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scheduledAuditName")
    def scheduled_audit_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.ScheduledAuditName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-scheduledauditname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scheduledAuditName"))

    @scheduled_audit_name.setter
    def scheduled_audit_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "scheduledAuditName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::ScheduledAudit.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetCheckNames")
    def target_check_names(self) -> typing.List[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.TargetCheckNames``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-targetchecknames
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetCheckNames"))

    @target_check_names.setter
    def target_check_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targetCheckNames", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnScheduledAuditProps",
    jsii_struct_bases=[],
    name_mapping={
        "day_of_month": "dayOfMonth",
        "day_of_week": "dayOfWeek",
        "frequency": "frequency",
        "scheduled_audit_name": "scheduledAuditName",
        "tags": "tags",
        "target_check_names": "targetCheckNames",
    },
)
class CfnScheduledAuditProps:
    def __init__(
        self,
        *,
        day_of_month: typing.Optional[builtins.str] = None,
        day_of_week: typing.Optional[builtins.str] = None,
        frequency: builtins.str,
        scheduled_audit_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        target_check_names: typing.Sequence[builtins.str],
    ) -> None:
        '''Properties for defining a ``AWS::IoT::ScheduledAudit``.

        :param day_of_month: ``AWS::IoT::ScheduledAudit.DayOfMonth``.
        :param day_of_week: ``AWS::IoT::ScheduledAudit.DayOfWeek``.
        :param frequency: ``AWS::IoT::ScheduledAudit.Frequency``.
        :param scheduled_audit_name: ``AWS::IoT::ScheduledAudit.ScheduledAuditName``.
        :param tags: ``AWS::IoT::ScheduledAudit.Tags``.
        :param target_check_names: ``AWS::IoT::ScheduledAudit.TargetCheckNames``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_scheduled_audit_props = iot.CfnScheduledAuditProps(
                frequency="frequency",
                target_check_names=["targetCheckNames"],
            
                # the properties below are optional
                day_of_month="dayOfMonth",
                day_of_week="dayOfWeek",
                scheduled_audit_name="scheduledAuditName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "frequency": frequency,
            "target_check_names": target_check_names,
        }
        if day_of_month is not None:
            self._values["day_of_month"] = day_of_month
        if day_of_week is not None:
            self._values["day_of_week"] = day_of_week
        if scheduled_audit_name is not None:
            self._values["scheduled_audit_name"] = scheduled_audit_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def day_of_month(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.DayOfMonth``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-dayofmonth
        '''
        result = self._values.get("day_of_month")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def day_of_week(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.DayOfWeek``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-dayofweek
        '''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency(self) -> builtins.str:
        '''``AWS::IoT::ScheduledAudit.Frequency``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-frequency
        '''
        result = self._values.get("frequency")
        assert result is not None, "Required property 'frequency' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheduled_audit_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.ScheduledAuditName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-scheduledauditname
        '''
        result = self._values.get("scheduled_audit_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::ScheduledAudit.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def target_check_names(self) -> typing.List[builtins.str]:
        '''``AWS::IoT::ScheduledAudit.TargetCheckNames``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-scheduledaudit.html#cfn-iot-scheduledaudit-targetchecknames
        '''
        result = self._values.get("target_check_names")
        assert result is not None, "Required property 'target_check_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnScheduledAuditProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnSecurityProfile(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile",
):
    '''A CloudFormation ``AWS::IoT::SecurityProfile``.

    :cloudformationResource: AWS::IoT::SecurityProfile
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_security_profile = iot.CfnSecurityProfile(self, "MyCfnSecurityProfile",
            additional_metrics_to_retain_v2=[iot.CfnSecurityProfile.MetricToRetainProperty(
                metric="metric",
        
                # the properties below are optional
                metric_dimension=iot.CfnSecurityProfile.MetricDimensionProperty(
                    dimension_name="dimensionName",
        
                    # the properties below are optional
                    operator="operator"
                )
            )],
            alert_targets={
                "alert_targets_key": iot.CfnSecurityProfile.AlertTargetProperty(
                    alert_target_arn="alertTargetArn",
                    role_arn="roleArn"
                )
            },
            behaviors=[iot.CfnSecurityProfile.BehaviorProperty(
                name="name",
        
                # the properties below are optional
                criteria=iot.CfnSecurityProfile.BehaviorCriteriaProperty(
                    comparison_operator="comparisonOperator",
                    consecutive_datapoints_to_alarm=123,
                    consecutive_datapoints_to_clear=123,
                    duration_seconds=123,
                    ml_detection_config=iot.CfnSecurityProfile.MachineLearningDetectionConfigProperty(
                        confidence_level="confidenceLevel"
                    ),
                    statistical_threshold=iot.CfnSecurityProfile.StatisticalThresholdProperty(
                        statistic="statistic"
                    ),
                    value=iot.CfnSecurityProfile.MetricValueProperty(
                        cidrs=["cidrs"],
                        count="count",
                        number=123,
                        numbers=[123],
                        ports=[123],
                        strings=["strings"]
                    )
                ),
                metric="metric",
                metric_dimension=iot.CfnSecurityProfile.MetricDimensionProperty(
                    dimension_name="dimensionName",
        
                    # the properties below are optional
                    operator="operator"
                ),
                suppress_alerts=False
            )],
            security_profile_description="securityProfileDescription",
            security_profile_name="securityProfileName",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            target_arns=["targetArns"]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        additional_metrics_to_retain_v2: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnSecurityProfile.MetricToRetainProperty", _IResolvable_da3f097b]]]] = None,
        alert_targets: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union["CfnSecurityProfile.AlertTargetProperty", _IResolvable_da3f097b]]]] = None,
        behaviors: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnSecurityProfile.BehaviorProperty", _IResolvable_da3f097b]]]] = None,
        security_profile_description: typing.Optional[builtins.str] = None,
        security_profile_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        target_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::SecurityProfile``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param additional_metrics_to_retain_v2: ``AWS::IoT::SecurityProfile.AdditionalMetricsToRetainV2``.
        :param alert_targets: ``AWS::IoT::SecurityProfile.AlertTargets``.
        :param behaviors: ``AWS::IoT::SecurityProfile.Behaviors``.
        :param security_profile_description: ``AWS::IoT::SecurityProfile.SecurityProfileDescription``.
        :param security_profile_name: ``AWS::IoT::SecurityProfile.SecurityProfileName``.
        :param tags: ``AWS::IoT::SecurityProfile.Tags``.
        :param target_arns: ``AWS::IoT::SecurityProfile.TargetArns``.
        '''
        props = CfnSecurityProfileProps(
            additional_metrics_to_retain_v2=additional_metrics_to_retain_v2,
            alert_targets=alert_targets,
            behaviors=behaviors,
            security_profile_description=security_profile_description,
            security_profile_name=security_profile_name,
            tags=tags,
            target_arns=target_arns,
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
    @jsii.member(jsii_name="additionalMetricsToRetainV2")
    def additional_metrics_to_retain_v2(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityProfile.MetricToRetainProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::IoT::SecurityProfile.AdditionalMetricsToRetainV2``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-additionalmetricstoretainv2
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityProfile.MetricToRetainProperty", _IResolvable_da3f097b]]]], jsii.get(self, "additionalMetricsToRetainV2"))

    @additional_metrics_to_retain_v2.setter
    def additional_metrics_to_retain_v2(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityProfile.MetricToRetainProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "additionalMetricsToRetainV2", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alertTargets")
    def alert_targets(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union["CfnSecurityProfile.AlertTargetProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::IoT::SecurityProfile.AlertTargets``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-alerttargets
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union["CfnSecurityProfile.AlertTargetProperty", _IResolvable_da3f097b]]]], jsii.get(self, "alertTargets"))

    @alert_targets.setter
    def alert_targets(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union["CfnSecurityProfile.AlertTargetProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "alertTargets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrSecurityProfileArn")
    def attr_security_profile_arn(self) -> builtins.str:
        '''
        :cloudformationAttribute: SecurityProfileArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrSecurityProfileArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="behaviors")
    def behaviors(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityProfile.BehaviorProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::IoT::SecurityProfile.Behaviors``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-behaviors
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityProfile.BehaviorProperty", _IResolvable_da3f097b]]]], jsii.get(self, "behaviors"))

    @behaviors.setter
    def behaviors(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnSecurityProfile.BehaviorProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "behaviors", value)

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
    @jsii.member(jsii_name="securityProfileDescription")
    def security_profile_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::SecurityProfile.SecurityProfileDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-securityprofiledescription
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityProfileDescription"))

    @security_profile_description.setter
    def security_profile_description(
        self,
        value: typing.Optional[builtins.str],
    ) -> None:
        jsii.set(self, "securityProfileDescription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityProfileName")
    def security_profile_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::SecurityProfile.SecurityProfileName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-securityprofilename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "securityProfileName"))

    @security_profile_name.setter
    def security_profile_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "securityProfileName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::SecurityProfile.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetArns")
    def target_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::IoT::SecurityProfile.TargetArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-targetarns
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetArns"))

    @target_arns.setter
    def target_arns(self, value: typing.Optional[typing.List[builtins.str]]) -> None:
        jsii.set(self, "targetArns", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.AlertTargetProperty",
        jsii_struct_bases=[],
        name_mapping={"alert_target_arn": "alertTargetArn", "role_arn": "roleArn"},
    )
    class AlertTargetProperty:
        def __init__(
            self,
            *,
            alert_target_arn: builtins.str,
            role_arn: builtins.str,
        ) -> None:
            '''
            :param alert_target_arn: ``CfnSecurityProfile.AlertTargetProperty.AlertTargetArn``.
            :param role_arn: ``CfnSecurityProfile.AlertTargetProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-alerttarget.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                alert_target_property = iot.CfnSecurityProfile.AlertTargetProperty(
                    alert_target_arn="alertTargetArn",
                    role_arn="roleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "alert_target_arn": alert_target_arn,
                "role_arn": role_arn,
            }

        @builtins.property
        def alert_target_arn(self) -> builtins.str:
            '''``CfnSecurityProfile.AlertTargetProperty.AlertTargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-alerttarget.html#cfn-iot-securityprofile-alerttarget-alerttargetarn
            '''
            result = self._values.get("alert_target_arn")
            assert result is not None, "Required property 'alert_target_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnSecurityProfile.AlertTargetProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-alerttarget.html#cfn-iot-securityprofile-alerttarget-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AlertTargetProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.BehaviorCriteriaProperty",
        jsii_struct_bases=[],
        name_mapping={
            "comparison_operator": "comparisonOperator",
            "consecutive_datapoints_to_alarm": "consecutiveDatapointsToAlarm",
            "consecutive_datapoints_to_clear": "consecutiveDatapointsToClear",
            "duration_seconds": "durationSeconds",
            "ml_detection_config": "mlDetectionConfig",
            "statistical_threshold": "statisticalThreshold",
            "value": "value",
        },
    )
    class BehaviorCriteriaProperty:
        def __init__(
            self,
            *,
            comparison_operator: typing.Optional[builtins.str] = None,
            consecutive_datapoints_to_alarm: typing.Optional[jsii.Number] = None,
            consecutive_datapoints_to_clear: typing.Optional[jsii.Number] = None,
            duration_seconds: typing.Optional[jsii.Number] = None,
            ml_detection_config: typing.Optional[typing.Union["CfnSecurityProfile.MachineLearningDetectionConfigProperty", _IResolvable_da3f097b]] = None,
            statistical_threshold: typing.Optional[typing.Union["CfnSecurityProfile.StatisticalThresholdProperty", _IResolvable_da3f097b]] = None,
            value: typing.Optional[typing.Union["CfnSecurityProfile.MetricValueProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param comparison_operator: ``CfnSecurityProfile.BehaviorCriteriaProperty.ComparisonOperator``.
            :param consecutive_datapoints_to_alarm: ``CfnSecurityProfile.BehaviorCriteriaProperty.ConsecutiveDatapointsToAlarm``.
            :param consecutive_datapoints_to_clear: ``CfnSecurityProfile.BehaviorCriteriaProperty.ConsecutiveDatapointsToClear``.
            :param duration_seconds: ``CfnSecurityProfile.BehaviorCriteriaProperty.DurationSeconds``.
            :param ml_detection_config: ``CfnSecurityProfile.BehaviorCriteriaProperty.MlDetectionConfig``.
            :param statistical_threshold: ``CfnSecurityProfile.BehaviorCriteriaProperty.StatisticalThreshold``.
            :param value: ``CfnSecurityProfile.BehaviorCriteriaProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                behavior_criteria_property = iot.CfnSecurityProfile.BehaviorCriteriaProperty(
                    comparison_operator="comparisonOperator",
                    consecutive_datapoints_to_alarm=123,
                    consecutive_datapoints_to_clear=123,
                    duration_seconds=123,
                    ml_detection_config=iot.CfnSecurityProfile.MachineLearningDetectionConfigProperty(
                        confidence_level="confidenceLevel"
                    ),
                    statistical_threshold=iot.CfnSecurityProfile.StatisticalThresholdProperty(
                        statistic="statistic"
                    ),
                    value=iot.CfnSecurityProfile.MetricValueProperty(
                        cidrs=["cidrs"],
                        count="count",
                        number=123,
                        numbers=[123],
                        ports=[123],
                        strings=["strings"]
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if comparison_operator is not None:
                self._values["comparison_operator"] = comparison_operator
            if consecutive_datapoints_to_alarm is not None:
                self._values["consecutive_datapoints_to_alarm"] = consecutive_datapoints_to_alarm
            if consecutive_datapoints_to_clear is not None:
                self._values["consecutive_datapoints_to_clear"] = consecutive_datapoints_to_clear
            if duration_seconds is not None:
                self._values["duration_seconds"] = duration_seconds
            if ml_detection_config is not None:
                self._values["ml_detection_config"] = ml_detection_config
            if statistical_threshold is not None:
                self._values["statistical_threshold"] = statistical_threshold
            if value is not None:
                self._values["value"] = value

        @builtins.property
        def comparison_operator(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.ComparisonOperator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-comparisonoperator
            '''
            result = self._values.get("comparison_operator")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def consecutive_datapoints_to_alarm(self) -> typing.Optional[jsii.Number]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.ConsecutiveDatapointsToAlarm``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-consecutivedatapointstoalarm
            '''
            result = self._values.get("consecutive_datapoints_to_alarm")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def consecutive_datapoints_to_clear(self) -> typing.Optional[jsii.Number]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.ConsecutiveDatapointsToClear``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-consecutivedatapointstoclear
            '''
            result = self._values.get("consecutive_datapoints_to_clear")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def duration_seconds(self) -> typing.Optional[jsii.Number]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.DurationSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-durationseconds
            '''
            result = self._values.get("duration_seconds")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def ml_detection_config(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityProfile.MachineLearningDetectionConfigProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.MlDetectionConfig``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-mldetectionconfig
            '''
            result = self._values.get("ml_detection_config")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityProfile.MachineLearningDetectionConfigProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def statistical_threshold(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityProfile.StatisticalThresholdProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.StatisticalThreshold``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-statisticalthreshold
            '''
            result = self._values.get("statistical_threshold")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityProfile.StatisticalThresholdProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def value(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityProfile.MetricValueProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.BehaviorCriteriaProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behaviorcriteria.html#cfn-iot-securityprofile-behaviorcriteria-value
            '''
            result = self._values.get("value")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityProfile.MetricValueProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BehaviorCriteriaProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.BehaviorProperty",
        jsii_struct_bases=[],
        name_mapping={
            "criteria": "criteria",
            "metric": "metric",
            "metric_dimension": "metricDimension",
            "name": "name",
            "suppress_alerts": "suppressAlerts",
        },
    )
    class BehaviorProperty:
        def __init__(
            self,
            *,
            criteria: typing.Optional[typing.Union["CfnSecurityProfile.BehaviorCriteriaProperty", _IResolvable_da3f097b]] = None,
            metric: typing.Optional[builtins.str] = None,
            metric_dimension: typing.Optional[typing.Union["CfnSecurityProfile.MetricDimensionProperty", _IResolvable_da3f097b]] = None,
            name: builtins.str,
            suppress_alerts: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param criteria: ``CfnSecurityProfile.BehaviorProperty.Criteria``.
            :param metric: ``CfnSecurityProfile.BehaviorProperty.Metric``.
            :param metric_dimension: ``CfnSecurityProfile.BehaviorProperty.MetricDimension``.
            :param name: ``CfnSecurityProfile.BehaviorProperty.Name``.
            :param suppress_alerts: ``CfnSecurityProfile.BehaviorProperty.SuppressAlerts``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behavior.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                behavior_property = iot.CfnSecurityProfile.BehaviorProperty(
                    name="name",
                
                    # the properties below are optional
                    criteria=iot.CfnSecurityProfile.BehaviorCriteriaProperty(
                        comparison_operator="comparisonOperator",
                        consecutive_datapoints_to_alarm=123,
                        consecutive_datapoints_to_clear=123,
                        duration_seconds=123,
                        ml_detection_config=iot.CfnSecurityProfile.MachineLearningDetectionConfigProperty(
                            confidence_level="confidenceLevel"
                        ),
                        statistical_threshold=iot.CfnSecurityProfile.StatisticalThresholdProperty(
                            statistic="statistic"
                        ),
                        value=iot.CfnSecurityProfile.MetricValueProperty(
                            cidrs=["cidrs"],
                            count="count",
                            number=123,
                            numbers=[123],
                            ports=[123],
                            strings=["strings"]
                        )
                    ),
                    metric="metric",
                    metric_dimension=iot.CfnSecurityProfile.MetricDimensionProperty(
                        dimension_name="dimensionName",
                
                        # the properties below are optional
                        operator="operator"
                    ),
                    suppress_alerts=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
            }
            if criteria is not None:
                self._values["criteria"] = criteria
            if metric is not None:
                self._values["metric"] = metric
            if metric_dimension is not None:
                self._values["metric_dimension"] = metric_dimension
            if suppress_alerts is not None:
                self._values["suppress_alerts"] = suppress_alerts

        @builtins.property
        def criteria(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityProfile.BehaviorCriteriaProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.BehaviorProperty.Criteria``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behavior.html#cfn-iot-securityprofile-behavior-criteria
            '''
            result = self._values.get("criteria")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityProfile.BehaviorCriteriaProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def metric(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityProfile.BehaviorProperty.Metric``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behavior.html#cfn-iot-securityprofile-behavior-metric
            '''
            result = self._values.get("metric")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def metric_dimension(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityProfile.MetricDimensionProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.BehaviorProperty.MetricDimension``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behavior.html#cfn-iot-securityprofile-behavior-metricdimension
            '''
            result = self._values.get("metric_dimension")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityProfile.MetricDimensionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnSecurityProfile.BehaviorProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behavior.html#cfn-iot-securityprofile-behavior-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def suppress_alerts(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.BehaviorProperty.SuppressAlerts``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-behavior.html#cfn-iot-securityprofile-behavior-suppressalerts
            '''
            result = self._values.get("suppress_alerts")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BehaviorProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.MachineLearningDetectionConfigProperty",
        jsii_struct_bases=[],
        name_mapping={"confidence_level": "confidenceLevel"},
    )
    class MachineLearningDetectionConfigProperty:
        def __init__(
            self,
            *,
            confidence_level: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param confidence_level: ``CfnSecurityProfile.MachineLearningDetectionConfigProperty.ConfidenceLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-machinelearningdetectionconfig.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                machine_learning_detection_config_property = iot.CfnSecurityProfile.MachineLearningDetectionConfigProperty(
                    confidence_level="confidenceLevel"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if confidence_level is not None:
                self._values["confidence_level"] = confidence_level

        @builtins.property
        def confidence_level(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityProfile.MachineLearningDetectionConfigProperty.ConfidenceLevel``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-machinelearningdetectionconfig.html#cfn-iot-securityprofile-machinelearningdetectionconfig-confidencelevel
            '''
            result = self._values.get("confidence_level")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MachineLearningDetectionConfigProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.MetricDimensionProperty",
        jsii_struct_bases=[],
        name_mapping={"dimension_name": "dimensionName", "operator": "operator"},
    )
    class MetricDimensionProperty:
        def __init__(
            self,
            *,
            dimension_name: builtins.str,
            operator: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param dimension_name: ``CfnSecurityProfile.MetricDimensionProperty.DimensionName``.
            :param operator: ``CfnSecurityProfile.MetricDimensionProperty.Operator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricdimension.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                metric_dimension_property = iot.CfnSecurityProfile.MetricDimensionProperty(
                    dimension_name="dimensionName",
                
                    # the properties below are optional
                    operator="operator"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "dimension_name": dimension_name,
            }
            if operator is not None:
                self._values["operator"] = operator

        @builtins.property
        def dimension_name(self) -> builtins.str:
            '''``CfnSecurityProfile.MetricDimensionProperty.DimensionName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricdimension.html#cfn-iot-securityprofile-metricdimension-dimensionname
            '''
            result = self._values.get("dimension_name")
            assert result is not None, "Required property 'dimension_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def operator(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityProfile.MetricDimensionProperty.Operator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricdimension.html#cfn-iot-securityprofile-metricdimension-operator
            '''
            result = self._values.get("operator")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MetricDimensionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.MetricToRetainProperty",
        jsii_struct_bases=[],
        name_mapping={"metric": "metric", "metric_dimension": "metricDimension"},
    )
    class MetricToRetainProperty:
        def __init__(
            self,
            *,
            metric: builtins.str,
            metric_dimension: typing.Optional[typing.Union["CfnSecurityProfile.MetricDimensionProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param metric: ``CfnSecurityProfile.MetricToRetainProperty.Metric``.
            :param metric_dimension: ``CfnSecurityProfile.MetricToRetainProperty.MetricDimension``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metrictoretain.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                metric_to_retain_property = iot.CfnSecurityProfile.MetricToRetainProperty(
                    metric="metric",
                
                    # the properties below are optional
                    metric_dimension=iot.CfnSecurityProfile.MetricDimensionProperty(
                        dimension_name="dimensionName",
                
                        # the properties below are optional
                        operator="operator"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "metric": metric,
            }
            if metric_dimension is not None:
                self._values["metric_dimension"] = metric_dimension

        @builtins.property
        def metric(self) -> builtins.str:
            '''``CfnSecurityProfile.MetricToRetainProperty.Metric``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metrictoretain.html#cfn-iot-securityprofile-metrictoretain-metric
            '''
            result = self._values.get("metric")
            assert result is not None, "Required property 'metric' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def metric_dimension(
            self,
        ) -> typing.Optional[typing.Union["CfnSecurityProfile.MetricDimensionProperty", _IResolvable_da3f097b]]:
            '''``CfnSecurityProfile.MetricToRetainProperty.MetricDimension``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metrictoretain.html#cfn-iot-securityprofile-metrictoretain-metricdimension
            '''
            result = self._values.get("metric_dimension")
            return typing.cast(typing.Optional[typing.Union["CfnSecurityProfile.MetricDimensionProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MetricToRetainProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.MetricValueProperty",
        jsii_struct_bases=[],
        name_mapping={
            "cidrs": "cidrs",
            "count": "count",
            "number": "number",
            "numbers": "numbers",
            "ports": "ports",
            "strings": "strings",
        },
    )
    class MetricValueProperty:
        def __init__(
            self,
            *,
            cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
            count: typing.Optional[builtins.str] = None,
            number: typing.Optional[jsii.Number] = None,
            numbers: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[jsii.Number]]] = None,
            ports: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[jsii.Number]]] = None,
            strings: typing.Optional[typing.Sequence[builtins.str]] = None,
        ) -> None:
            '''
            :param cidrs: ``CfnSecurityProfile.MetricValueProperty.Cidrs``.
            :param count: ``CfnSecurityProfile.MetricValueProperty.Count``.
            :param number: ``CfnSecurityProfile.MetricValueProperty.Number``.
            :param numbers: ``CfnSecurityProfile.MetricValueProperty.Numbers``.
            :param ports: ``CfnSecurityProfile.MetricValueProperty.Ports``.
            :param strings: ``CfnSecurityProfile.MetricValueProperty.Strings``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                metric_value_property = iot.CfnSecurityProfile.MetricValueProperty(
                    cidrs=["cidrs"],
                    count="count",
                    number=123,
                    numbers=[123],
                    ports=[123],
                    strings=["strings"]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if cidrs is not None:
                self._values["cidrs"] = cidrs
            if count is not None:
                self._values["count"] = count
            if number is not None:
                self._values["number"] = number
            if numbers is not None:
                self._values["numbers"] = numbers
            if ports is not None:
                self._values["ports"] = ports
            if strings is not None:
                self._values["strings"] = strings

        @builtins.property
        def cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnSecurityProfile.MetricValueProperty.Cidrs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html#cfn-iot-securityprofile-metricvalue-cidrs
            '''
            result = self._values.get("cidrs")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def count(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityProfile.MetricValueProperty.Count``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html#cfn-iot-securityprofile-metricvalue-count
            '''
            result = self._values.get("count")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def number(self) -> typing.Optional[jsii.Number]:
            '''``CfnSecurityProfile.MetricValueProperty.Number``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html#cfn-iot-securityprofile-metricvalue-number
            '''
            result = self._values.get("number")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def numbers(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[jsii.Number]]]:
            '''``CfnSecurityProfile.MetricValueProperty.Numbers``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html#cfn-iot-securityprofile-metricvalue-numbers
            '''
            result = self._values.get("numbers")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[jsii.Number]]], result)

        @builtins.property
        def ports(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[jsii.Number]]]:
            '''``CfnSecurityProfile.MetricValueProperty.Ports``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html#cfn-iot-securityprofile-metricvalue-ports
            '''
            result = self._values.get("ports")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[jsii.Number]]], result)

        @builtins.property
        def strings(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnSecurityProfile.MetricValueProperty.Strings``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-metricvalue.html#cfn-iot-securityprofile-metricvalue-strings
            '''
            result = self._values.get("strings")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "MetricValueProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfile.StatisticalThresholdProperty",
        jsii_struct_bases=[],
        name_mapping={"statistic": "statistic"},
    )
    class StatisticalThresholdProperty:
        def __init__(self, *, statistic: typing.Optional[builtins.str] = None) -> None:
            '''
            :param statistic: ``CfnSecurityProfile.StatisticalThresholdProperty.Statistic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-statisticalthreshold.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                statistical_threshold_property = iot.CfnSecurityProfile.StatisticalThresholdProperty(
                    statistic="statistic"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if statistic is not None:
                self._values["statistic"] = statistic

        @builtins.property
        def statistic(self) -> typing.Optional[builtins.str]:
            '''``CfnSecurityProfile.StatisticalThresholdProperty.Statistic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-securityprofile-statisticalthreshold.html#cfn-iot-securityprofile-statisticalthreshold-statistic
            '''
            result = self._values.get("statistic")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StatisticalThresholdProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnSecurityProfileProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_metrics_to_retain_v2": "additionalMetricsToRetainV2",
        "alert_targets": "alertTargets",
        "behaviors": "behaviors",
        "security_profile_description": "securityProfileDescription",
        "security_profile_name": "securityProfileName",
        "tags": "tags",
        "target_arns": "targetArns",
    },
)
class CfnSecurityProfileProps:
    def __init__(
        self,
        *,
        additional_metrics_to_retain_v2: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnSecurityProfile.MetricToRetainProperty, _IResolvable_da3f097b]]]] = None,
        alert_targets: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union[CfnSecurityProfile.AlertTargetProperty, _IResolvable_da3f097b]]]] = None,
        behaviors: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnSecurityProfile.BehaviorProperty, _IResolvable_da3f097b]]]] = None,
        security_profile_description: typing.Optional[builtins.str] = None,
        security_profile_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        target_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::SecurityProfile``.

        :param additional_metrics_to_retain_v2: ``AWS::IoT::SecurityProfile.AdditionalMetricsToRetainV2``.
        :param alert_targets: ``AWS::IoT::SecurityProfile.AlertTargets``.
        :param behaviors: ``AWS::IoT::SecurityProfile.Behaviors``.
        :param security_profile_description: ``AWS::IoT::SecurityProfile.SecurityProfileDescription``.
        :param security_profile_name: ``AWS::IoT::SecurityProfile.SecurityProfileName``.
        :param tags: ``AWS::IoT::SecurityProfile.Tags``.
        :param target_arns: ``AWS::IoT::SecurityProfile.TargetArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_security_profile_props = iot.CfnSecurityProfileProps(
                additional_metrics_to_retain_v2=[iot.CfnSecurityProfile.MetricToRetainProperty(
                    metric="metric",
            
                    # the properties below are optional
                    metric_dimension=iot.CfnSecurityProfile.MetricDimensionProperty(
                        dimension_name="dimensionName",
            
                        # the properties below are optional
                        operator="operator"
                    )
                )],
                alert_targets={
                    "alert_targets_key": iot.CfnSecurityProfile.AlertTargetProperty(
                        alert_target_arn="alertTargetArn",
                        role_arn="roleArn"
                    )
                },
                behaviors=[iot.CfnSecurityProfile.BehaviorProperty(
                    name="name",
            
                    # the properties below are optional
                    criteria=iot.CfnSecurityProfile.BehaviorCriteriaProperty(
                        comparison_operator="comparisonOperator",
                        consecutive_datapoints_to_alarm=123,
                        consecutive_datapoints_to_clear=123,
                        duration_seconds=123,
                        ml_detection_config=iot.CfnSecurityProfile.MachineLearningDetectionConfigProperty(
                            confidence_level="confidenceLevel"
                        ),
                        statistical_threshold=iot.CfnSecurityProfile.StatisticalThresholdProperty(
                            statistic="statistic"
                        ),
                        value=iot.CfnSecurityProfile.MetricValueProperty(
                            cidrs=["cidrs"],
                            count="count",
                            number=123,
                            numbers=[123],
                            ports=[123],
                            strings=["strings"]
                        )
                    ),
                    metric="metric",
                    metric_dimension=iot.CfnSecurityProfile.MetricDimensionProperty(
                        dimension_name="dimensionName",
            
                        # the properties below are optional
                        operator="operator"
                    ),
                    suppress_alerts=False
                )],
                security_profile_description="securityProfileDescription",
                security_profile_name="securityProfileName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                target_arns=["targetArns"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_metrics_to_retain_v2 is not None:
            self._values["additional_metrics_to_retain_v2"] = additional_metrics_to_retain_v2
        if alert_targets is not None:
            self._values["alert_targets"] = alert_targets
        if behaviors is not None:
            self._values["behaviors"] = behaviors
        if security_profile_description is not None:
            self._values["security_profile_description"] = security_profile_description
        if security_profile_name is not None:
            self._values["security_profile_name"] = security_profile_name
        if tags is not None:
            self._values["tags"] = tags
        if target_arns is not None:
            self._values["target_arns"] = target_arns

    @builtins.property
    def additional_metrics_to_retain_v2(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnSecurityProfile.MetricToRetainProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::IoT::SecurityProfile.AdditionalMetricsToRetainV2``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-additionalmetricstoretainv2
        '''
        result = self._values.get("additional_metrics_to_retain_v2")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnSecurityProfile.MetricToRetainProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def alert_targets(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union[CfnSecurityProfile.AlertTargetProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::IoT::SecurityProfile.AlertTargets``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-alerttargets
        '''
        result = self._values.get("alert_targets")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, typing.Union[CfnSecurityProfile.AlertTargetProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def behaviors(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnSecurityProfile.BehaviorProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::IoT::SecurityProfile.Behaviors``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-behaviors
        '''
        result = self._values.get("behaviors")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnSecurityProfile.BehaviorProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def security_profile_description(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::SecurityProfile.SecurityProfileDescription``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-securityprofiledescription
        '''
        result = self._values.get("security_profile_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_profile_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::SecurityProfile.SecurityProfileName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-securityprofilename
        '''
        result = self._values.get("security_profile_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::SecurityProfile.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def target_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''``AWS::IoT::SecurityProfile.TargetArns``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-securityprofile.html#cfn-iot-securityprofile-targetarns
        '''
        result = self._values.get("target_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnSecurityProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnThing(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnThing",
):
    '''A CloudFormation ``AWS::IoT::Thing``.

    :cloudformationResource: AWS::IoT::Thing
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_thing = iot.CfnThing(self, "MyCfnThing",
            attribute_payload=iot.CfnThing.AttributePayloadProperty(
                attributes={
                    "attributes_key": "attributes"
                }
            ),
            thing_name="thingName"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        attribute_payload: typing.Optional[typing.Union["CfnThing.AttributePayloadProperty", _IResolvable_da3f097b]] = None,
        thing_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::Thing``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param attribute_payload: ``AWS::IoT::Thing.AttributePayload``.
        :param thing_name: ``AWS::IoT::Thing.ThingName``.
        '''
        props = CfnThingProps(
            attribute_payload=attribute_payload, thing_name=thing_name
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
    @jsii.member(jsii_name="attributePayload")
    def attribute_payload(
        self,
    ) -> typing.Optional[typing.Union["CfnThing.AttributePayloadProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::Thing.AttributePayload``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
        '''
        return typing.cast(typing.Optional[typing.Union["CfnThing.AttributePayloadProperty", _IResolvable_da3f097b]], jsii.get(self, "attributePayload"))

    @attribute_payload.setter
    def attribute_payload(
        self,
        value: typing.Optional[typing.Union["CfnThing.AttributePayloadProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "attributePayload", value)

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
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Thing.ThingName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "thingName"))

    @thing_name.setter
    def thing_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "thingName", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnThing.AttributePayloadProperty",
        jsii_struct_bases=[],
        name_mapping={"attributes": "attributes"},
    )
    class AttributePayloadProperty:
        def __init__(
            self,
            *,
            attributes: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]] = None,
        ) -> None:
            '''
            :param attributes: ``CfnThing.AttributePayloadProperty.Attributes``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                attribute_payload_property = iot.CfnThing.AttributePayloadProperty(
                    attributes={
                        "attributes_key": "attributes"
                    }
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if attributes is not None:
                self._values["attributes"] = attributes

        @builtins.property
        def attributes(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]]:
            '''``CfnThing.AttributePayloadProperty.Attributes``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-thing-attributepayload.html#cfn-iot-thing-attributepayload-attributes
            '''
            result = self._values.get("attributes")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AttributePayloadProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(_IInspectable_c2943556)
class CfnThingPrincipalAttachment(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnThingPrincipalAttachment",
):
    '''A CloudFormation ``AWS::IoT::ThingPrincipalAttachment``.

    :cloudformationResource: AWS::IoT::ThingPrincipalAttachment
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_thing_principal_attachment = iot.CfnThingPrincipalAttachment(self, "MyCfnThingPrincipalAttachment",
            principal="principal",
            thing_name="thingName"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        principal: builtins.str,
        thing_name: builtins.str,
    ) -> None:
        '''Create a new ``AWS::IoT::ThingPrincipalAttachment``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param principal: ``AWS::IoT::ThingPrincipalAttachment.Principal``.
        :param thing_name: ``AWS::IoT::ThingPrincipalAttachment.ThingName``.
        '''
        props = CfnThingPrincipalAttachmentProps(
            principal=principal, thing_name=thing_name
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
    @jsii.member(jsii_name="principal")
    def principal(self) -> builtins.str:
        '''``AWS::IoT::ThingPrincipalAttachment.Principal``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
        '''
        return typing.cast(builtins.str, jsii.get(self, "principal"))

    @principal.setter
    def principal(self, value: builtins.str) -> None:
        jsii.set(self, "principal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="thingName")
    def thing_name(self) -> builtins.str:
        '''``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
        '''
        return typing.cast(builtins.str, jsii.get(self, "thingName"))

    @thing_name.setter
    def thing_name(self, value: builtins.str) -> None:
        jsii.set(self, "thingName", value)


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnThingPrincipalAttachmentProps",
    jsii_struct_bases=[],
    name_mapping={"principal": "principal", "thing_name": "thingName"},
)
class CfnThingPrincipalAttachmentProps:
    def __init__(self, *, principal: builtins.str, thing_name: builtins.str) -> None:
        '''Properties for defining a ``AWS::IoT::ThingPrincipalAttachment``.

        :param principal: ``AWS::IoT::ThingPrincipalAttachment.Principal``.
        :param thing_name: ``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_thing_principal_attachment_props = iot.CfnThingPrincipalAttachmentProps(
                principal="principal",
                thing_name="thingName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "principal": principal,
            "thing_name": thing_name,
        }

    @builtins.property
    def principal(self) -> builtins.str:
        '''``AWS::IoT::ThingPrincipalAttachment.Principal``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-principal
        '''
        result = self._values.get("principal")
        assert result is not None, "Required property 'principal' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def thing_name(self) -> builtins.str:
        '''``AWS::IoT::ThingPrincipalAttachment.ThingName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thingprincipalattachment.html#cfn-iot-thingprincipalattachment-thingname
        '''
        result = self._values.get("thing_name")
        assert result is not None, "Required property 'thing_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnThingPrincipalAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnThingProps",
    jsii_struct_bases=[],
    name_mapping={"attribute_payload": "attributePayload", "thing_name": "thingName"},
)
class CfnThingProps:
    def __init__(
        self,
        *,
        attribute_payload: typing.Optional[typing.Union[CfnThing.AttributePayloadProperty, _IResolvable_da3f097b]] = None,
        thing_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::Thing``.

        :param attribute_payload: ``AWS::IoT::Thing.AttributePayload``.
        :param thing_name: ``AWS::IoT::Thing.ThingName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_thing_props = iot.CfnThingProps(
                attribute_payload=iot.CfnThing.AttributePayloadProperty(
                    attributes={
                        "attributes_key": "attributes"
                    }
                ),
                thing_name="thingName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if attribute_payload is not None:
            self._values["attribute_payload"] = attribute_payload
        if thing_name is not None:
            self._values["thing_name"] = thing_name

    @builtins.property
    def attribute_payload(
        self,
    ) -> typing.Optional[typing.Union[CfnThing.AttributePayloadProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::Thing.AttributePayload``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-attributepayload
        '''
        result = self._values.get("attribute_payload")
        return typing.cast(typing.Optional[typing.Union[CfnThing.AttributePayloadProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def thing_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::Thing.ThingName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-thing.html#cfn-iot-thing-thingname
        '''
        result = self._values.get("thing_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnThingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnTopicRule(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule",
):
    '''A CloudFormation ``AWS::IoT::TopicRule``.

    :cloudformationResource: AWS::IoT::TopicRule
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_topic_rule = iot.CfnTopicRule(self, "MyCfnTopicRule",
            topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                actions=[iot.CfnTopicRule.ActionProperty(
                    cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                        alarm_name="alarmName",
                        role_arn="roleArn",
                        state_reason="stateReason",
                        state_value="stateValue"
                    ),
                    cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                        log_group_name="logGroupName",
                        role_arn="roleArn"
                    ),
                    cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                        metric_name="metricName",
                        metric_namespace="metricNamespace",
                        metric_unit="metricUnit",
                        metric_value="metricValue",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        metric_timestamp="metricTimestamp"
                    ),
                    dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                        hash_key_field="hashKeyField",
                        hash_key_value="hashKeyValue",
                        role_arn="roleArn",
                        table_name="tableName",
        
                        # the properties below are optional
                        hash_key_type="hashKeyType",
                        payload_field="payloadField",
                        range_key_field="rangeKeyField",
                        range_key_type="rangeKeyType",
                        range_key_value="rangeKeyValue"
                    ),
                    dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                        put_item=iot.CfnTopicRule.PutItemInputProperty(
                            table_name="tableName"
                        ),
                        role_arn="roleArn"
                    ),
                    elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                        endpoint="endpoint",
                        id="id",
                        index="index",
                        role_arn="roleArn",
                        type="type"
                    ),
                    firehose=iot.CfnTopicRule.FirehoseActionProperty(
                        delivery_stream_name="deliveryStreamName",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        batch_mode=False,
                        separator="separator"
                    ),
                    http=iot.CfnTopicRule.HttpActionProperty(
                        url="url",
        
                        # the properties below are optional
                        auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                            sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                role_arn="roleArn",
                                service_name="serviceName",
                                signing_region="signingRegion"
                            )
                        ),
                        confirmation_url="confirmationUrl",
                        headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                            key="key",
                            value="value"
                        )]
                    ),
                    iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                        channel_name="channelName",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        batch_mode=False
                    ),
                    iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                        input_name="inputName",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        batch_mode=False,
                        message_id="messageId"
                    ),
                    iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                        put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="timeInSeconds",
        
                                    # the properties below are optional
                                    offset_in_nanos="offsetInNanos"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    boolean_value="booleanValue",
                                    double_value="doubleValue",
                                    integer_value="integerValue",
                                    string_value="stringValue"
                                ),
        
                                # the properties below are optional
                                quality="quality"
                            )],
        
                            # the properties below are optional
                            asset_id="assetId",
                            entry_id="entryId",
                            property_alias="propertyAlias",
                            property_id="propertyId"
                        )],
                        role_arn="roleArn"
                    ),
                    kafka=iot.CfnTopicRule.KafkaActionProperty(
                        client_properties={
                            "client_properties_key": "clientProperties"
                        },
                        destination_arn="destinationArn",
                        topic="topic",
        
                        # the properties below are optional
                        key="key",
                        partition="partition"
                    ),
                    kinesis=iot.CfnTopicRule.KinesisActionProperty(
                        role_arn="roleArn",
                        stream_name="streamName",
        
                        # the properties below are optional
                        partition_key="partitionKey"
                    ),
                    lambda_=iot.CfnTopicRule.LambdaActionProperty(
                        function_arn="functionArn"
                    ),
                    open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                        endpoint="endpoint",
                        id="id",
                        index="index",
                        role_arn="roleArn",
                        type="type"
                    ),
                    republish=iot.CfnTopicRule.RepublishActionProperty(
                        role_arn="roleArn",
                        topic="topic",
        
                        # the properties below are optional
                        qos=123
                    ),
                    s3=iot.CfnTopicRule.S3ActionProperty(
                        bucket_name="bucketName",
                        key="key",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        canned_acl="cannedAcl"
                    ),
                    sns=iot.CfnTopicRule.SnsActionProperty(
                        role_arn="roleArn",
                        target_arn="targetArn",
        
                        # the properties below are optional
                        message_format="messageFormat"
                    ),
                    sqs=iot.CfnTopicRule.SqsActionProperty(
                        queue_url="queueUrl",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        use_base64=False
                    ),
                    step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                        role_arn="roleArn",
                        state_machine_name="stateMachineName",
        
                        # the properties below are optional
                        execution_name_prefix="executionNamePrefix"
                    ),
                    timestream=iot.CfnTopicRule.TimestreamActionProperty(
                        database_name="databaseName",
                        dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                            name="name",
                            value="value"
                        )],
                        role_arn="roleArn",
                        table_name="tableName",
        
                        # the properties below are optional
                        batch_mode=False,
                        timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                            unit="unit",
                            value="value"
                        )
                    )
                )],
                sql="sql",
        
                # the properties below are optional
                aws_iot_sql_version="awsIotSqlVersion",
                description="description",
                error_action=iot.CfnTopicRule.ActionProperty(
                    cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                        alarm_name="alarmName",
                        role_arn="roleArn",
                        state_reason="stateReason",
                        state_value="stateValue"
                    ),
                    cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                        log_group_name="logGroupName",
                        role_arn="roleArn"
                    ),
                    cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                        metric_name="metricName",
                        metric_namespace="metricNamespace",
                        metric_unit="metricUnit",
                        metric_value="metricValue",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        metric_timestamp="metricTimestamp"
                    ),
                    dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                        hash_key_field="hashKeyField",
                        hash_key_value="hashKeyValue",
                        role_arn="roleArn",
                        table_name="tableName",
        
                        # the properties below are optional
                        hash_key_type="hashKeyType",
                        payload_field="payloadField",
                        range_key_field="rangeKeyField",
                        range_key_type="rangeKeyType",
                        range_key_value="rangeKeyValue"
                    ),
                    dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                        put_item=iot.CfnTopicRule.PutItemInputProperty(
                            table_name="tableName"
                        ),
                        role_arn="roleArn"
                    ),
                    elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                        endpoint="endpoint",
                        id="id",
                        index="index",
                        role_arn="roleArn",
                        type="type"
                    ),
                    firehose=iot.CfnTopicRule.FirehoseActionProperty(
                        delivery_stream_name="deliveryStreamName",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        batch_mode=False,
                        separator="separator"
                    ),
                    http=iot.CfnTopicRule.HttpActionProperty(
                        url="url",
        
                        # the properties below are optional
                        auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                            sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                role_arn="roleArn",
                                service_name="serviceName",
                                signing_region="signingRegion"
                            )
                        ),
                        confirmation_url="confirmationUrl",
                        headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                            key="key",
                            value="value"
                        )]
                    ),
                    iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                        channel_name="channelName",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        batch_mode=False
                    ),
                    iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                        input_name="inputName",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        batch_mode=False,
                        message_id="messageId"
                    ),
                    iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                        put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="timeInSeconds",
        
                                    # the properties below are optional
                                    offset_in_nanos="offsetInNanos"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    boolean_value="booleanValue",
                                    double_value="doubleValue",
                                    integer_value="integerValue",
                                    string_value="stringValue"
                                ),
        
                                # the properties below are optional
                                quality="quality"
                            )],
        
                            # the properties below are optional
                            asset_id="assetId",
                            entry_id="entryId",
                            property_alias="propertyAlias",
                            property_id="propertyId"
                        )],
                        role_arn="roleArn"
                    ),
                    kafka=iot.CfnTopicRule.KafkaActionProperty(
                        client_properties={
                            "client_properties_key": "clientProperties"
                        },
                        destination_arn="destinationArn",
                        topic="topic",
        
                        # the properties below are optional
                        key="key",
                        partition="partition"
                    ),
                    kinesis=iot.CfnTopicRule.KinesisActionProperty(
                        role_arn="roleArn",
                        stream_name="streamName",
        
                        # the properties below are optional
                        partition_key="partitionKey"
                    ),
                    lambda_=iot.CfnTopicRule.LambdaActionProperty(
                        function_arn="functionArn"
                    ),
                    open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                        endpoint="endpoint",
                        id="id",
                        index="index",
                        role_arn="roleArn",
                        type="type"
                    ),
                    republish=iot.CfnTopicRule.RepublishActionProperty(
                        role_arn="roleArn",
                        topic="topic",
        
                        # the properties below are optional
                        qos=123
                    ),
                    s3=iot.CfnTopicRule.S3ActionProperty(
                        bucket_name="bucketName",
                        key="key",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        canned_acl="cannedAcl"
                    ),
                    sns=iot.CfnTopicRule.SnsActionProperty(
                        role_arn="roleArn",
                        target_arn="targetArn",
        
                        # the properties below are optional
                        message_format="messageFormat"
                    ),
                    sqs=iot.CfnTopicRule.SqsActionProperty(
                        queue_url="queueUrl",
                        role_arn="roleArn",
        
                        # the properties below are optional
                        use_base64=False
                    ),
                    step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                        role_arn="roleArn",
                        state_machine_name="stateMachineName",
        
                        # the properties below are optional
                        execution_name_prefix="executionNamePrefix"
                    ),
                    timestream=iot.CfnTopicRule.TimestreamActionProperty(
                        database_name="databaseName",
                        dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                            name="name",
                            value="value"
                        )],
                        role_arn="roleArn",
                        table_name="tableName",
        
                        # the properties below are optional
                        batch_mode=False,
                        timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                            unit="unit",
                            value="value"
                        )
                    )
                ),
                rule_disabled=False
            ),
        
            # the properties below are optional
            rule_name="ruleName",
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
        rule_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        topic_rule_payload: typing.Union["CfnTopicRule.TopicRulePayloadProperty", _IResolvable_da3f097b],
    ) -> None:
        '''Create a new ``AWS::IoT::TopicRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param rule_name: ``AWS::IoT::TopicRule.RuleName``.
        :param tags: ``AWS::IoT::TopicRule.Tags``.
        :param topic_rule_payload: ``AWS::IoT::TopicRule.TopicRulePayload``.
        '''
        props = CfnTopicRuleProps(
            rule_name=rule_name, tags=tags, topic_rule_payload=topic_rule_payload
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
    @jsii.member(jsii_name="ruleName")
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::TopicRule.RuleName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleName"))

    @rule_name.setter
    def rule_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "ruleName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::IoT::TopicRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicRulePayload")
    def topic_rule_payload(
        self,
    ) -> typing.Union["CfnTopicRule.TopicRulePayloadProperty", _IResolvable_da3f097b]:
        '''``AWS::IoT::TopicRule.TopicRulePayload``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
        '''
        return typing.cast(typing.Union["CfnTopicRule.TopicRulePayloadProperty", _IResolvable_da3f097b], jsii.get(self, "topicRulePayload"))

    @topic_rule_payload.setter
    def topic_rule_payload(
        self,
        value: typing.Union["CfnTopicRule.TopicRulePayloadProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "topicRulePayload", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.ActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "cloudwatch_alarm": "cloudwatchAlarm",
            "cloudwatch_logs": "cloudwatchLogs",
            "cloudwatch_metric": "cloudwatchMetric",
            "dynamo_db": "dynamoDb",
            "dynamo_d_bv2": "dynamoDBv2",
            "elasticsearch": "elasticsearch",
            "firehose": "firehose",
            "http": "http",
            "iot_analytics": "iotAnalytics",
            "iot_events": "iotEvents",
            "iot_site_wise": "iotSiteWise",
            "kafka": "kafka",
            "kinesis": "kinesis",
            "lambda_": "lambda",
            "open_search": "openSearch",
            "republish": "republish",
            "s3": "s3",
            "sns": "sns",
            "sqs": "sqs",
            "step_functions": "stepFunctions",
            "timestream": "timestream",
        },
    )
    class ActionProperty:
        def __init__(
            self,
            *,
            cloudwatch_alarm: typing.Optional[typing.Union["CfnTopicRule.CloudwatchAlarmActionProperty", _IResolvable_da3f097b]] = None,
            cloudwatch_logs: typing.Optional[typing.Union["CfnTopicRule.CloudwatchLogsActionProperty", _IResolvable_da3f097b]] = None,
            cloudwatch_metric: typing.Optional[typing.Union["CfnTopicRule.CloudwatchMetricActionProperty", _IResolvable_da3f097b]] = None,
            dynamo_db: typing.Optional[typing.Union["CfnTopicRule.DynamoDBActionProperty", _IResolvable_da3f097b]] = None,
            dynamo_d_bv2: typing.Optional[typing.Union["CfnTopicRule.DynamoDBv2ActionProperty", _IResolvable_da3f097b]] = None,
            elasticsearch: typing.Optional[typing.Union["CfnTopicRule.ElasticsearchActionProperty", _IResolvable_da3f097b]] = None,
            firehose: typing.Optional[typing.Union["CfnTopicRule.FirehoseActionProperty", _IResolvable_da3f097b]] = None,
            http: typing.Optional[typing.Union["CfnTopicRule.HttpActionProperty", _IResolvable_da3f097b]] = None,
            iot_analytics: typing.Optional[typing.Union["CfnTopicRule.IotAnalyticsActionProperty", _IResolvable_da3f097b]] = None,
            iot_events: typing.Optional[typing.Union["CfnTopicRule.IotEventsActionProperty", _IResolvable_da3f097b]] = None,
            iot_site_wise: typing.Optional[typing.Union["CfnTopicRule.IotSiteWiseActionProperty", _IResolvable_da3f097b]] = None,
            kafka: typing.Optional[typing.Union["CfnTopicRule.KafkaActionProperty", _IResolvable_da3f097b]] = None,
            kinesis: typing.Optional[typing.Union["CfnTopicRule.KinesisActionProperty", _IResolvable_da3f097b]] = None,
            lambda_: typing.Optional[typing.Union["CfnTopicRule.LambdaActionProperty", _IResolvable_da3f097b]] = None,
            open_search: typing.Optional[typing.Union["CfnTopicRule.OpenSearchActionProperty", _IResolvable_da3f097b]] = None,
            republish: typing.Optional[typing.Union["CfnTopicRule.RepublishActionProperty", _IResolvable_da3f097b]] = None,
            s3: typing.Optional[typing.Union["CfnTopicRule.S3ActionProperty", _IResolvable_da3f097b]] = None,
            sns: typing.Optional[typing.Union["CfnTopicRule.SnsActionProperty", _IResolvable_da3f097b]] = None,
            sqs: typing.Optional[typing.Union["CfnTopicRule.SqsActionProperty", _IResolvable_da3f097b]] = None,
            step_functions: typing.Optional[typing.Union["CfnTopicRule.StepFunctionsActionProperty", _IResolvable_da3f097b]] = None,
            timestream: typing.Optional[typing.Union["CfnTopicRule.TimestreamActionProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param cloudwatch_alarm: ``CfnTopicRule.ActionProperty.CloudwatchAlarm``.
            :param cloudwatch_logs: ``CfnTopicRule.ActionProperty.CloudwatchLogs``.
            :param cloudwatch_metric: ``CfnTopicRule.ActionProperty.CloudwatchMetric``.
            :param dynamo_db: ``CfnTopicRule.ActionProperty.DynamoDB``.
            :param dynamo_d_bv2: ``CfnTopicRule.ActionProperty.DynamoDBv2``.
            :param elasticsearch: ``CfnTopicRule.ActionProperty.Elasticsearch``.
            :param firehose: ``CfnTopicRule.ActionProperty.Firehose``.
            :param http: ``CfnTopicRule.ActionProperty.Http``.
            :param iot_analytics: ``CfnTopicRule.ActionProperty.IotAnalytics``.
            :param iot_events: ``CfnTopicRule.ActionProperty.IotEvents``.
            :param iot_site_wise: ``CfnTopicRule.ActionProperty.IotSiteWise``.
            :param kafka: ``CfnTopicRule.ActionProperty.Kafka``.
            :param kinesis: ``CfnTopicRule.ActionProperty.Kinesis``.
            :param lambda_: ``CfnTopicRule.ActionProperty.Lambda``.
            :param open_search: ``CfnTopicRule.ActionProperty.OpenSearch``.
            :param republish: ``CfnTopicRule.ActionProperty.Republish``.
            :param s3: ``CfnTopicRule.ActionProperty.S3``.
            :param sns: ``CfnTopicRule.ActionProperty.Sns``.
            :param sqs: ``CfnTopicRule.ActionProperty.Sqs``.
            :param step_functions: ``CfnTopicRule.ActionProperty.StepFunctions``.
            :param timestream: ``CfnTopicRule.ActionProperty.Timestream``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                action_property = iot.CfnTopicRule.ActionProperty(
                    cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                        alarm_name="alarmName",
                        role_arn="roleArn",
                        state_reason="stateReason",
                        state_value="stateValue"
                    ),
                    cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                        log_group_name="logGroupName",
                        role_arn="roleArn"
                    ),
                    cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                        metric_name="metricName",
                        metric_namespace="metricNamespace",
                        metric_unit="metricUnit",
                        metric_value="metricValue",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        metric_timestamp="metricTimestamp"
                    ),
                    dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                        hash_key_field="hashKeyField",
                        hash_key_value="hashKeyValue",
                        role_arn="roleArn",
                        table_name="tableName",
                
                        # the properties below are optional
                        hash_key_type="hashKeyType",
                        payload_field="payloadField",
                        range_key_field="rangeKeyField",
                        range_key_type="rangeKeyType",
                        range_key_value="rangeKeyValue"
                    ),
                    dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                        put_item=iot.CfnTopicRule.PutItemInputProperty(
                            table_name="tableName"
                        ),
                        role_arn="roleArn"
                    ),
                    elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                        endpoint="endpoint",
                        id="id",
                        index="index",
                        role_arn="roleArn",
                        type="type"
                    ),
                    firehose=iot.CfnTopicRule.FirehoseActionProperty(
                        delivery_stream_name="deliveryStreamName",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        batch_mode=False,
                        separator="separator"
                    ),
                    http=iot.CfnTopicRule.HttpActionProperty(
                        url="url",
                
                        # the properties below are optional
                        auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                            sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                role_arn="roleArn",
                                service_name="serviceName",
                                signing_region="signingRegion"
                            )
                        ),
                        confirmation_url="confirmationUrl",
                        headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                            key="key",
                            value="value"
                        )]
                    ),
                    iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                        channel_name="channelName",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        batch_mode=False
                    ),
                    iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                        input_name="inputName",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        batch_mode=False,
                        message_id="messageId"
                    ),
                    iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                        put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                            property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                    time_in_seconds="timeInSeconds",
                
                                    # the properties below are optional
                                    offset_in_nanos="offsetInNanos"
                                ),
                                value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                    boolean_value="booleanValue",
                                    double_value="doubleValue",
                                    integer_value="integerValue",
                                    string_value="stringValue"
                                ),
                
                                # the properties below are optional
                                quality="quality"
                            )],
                
                            # the properties below are optional
                            asset_id="assetId",
                            entry_id="entryId",
                            property_alias="propertyAlias",
                            property_id="propertyId"
                        )],
                        role_arn="roleArn"
                    ),
                    kafka=iot.CfnTopicRule.KafkaActionProperty(
                        client_properties={
                            "client_properties_key": "clientProperties"
                        },
                        destination_arn="destinationArn",
                        topic="topic",
                
                        # the properties below are optional
                        key="key",
                        partition="partition"
                    ),
                    kinesis=iot.CfnTopicRule.KinesisActionProperty(
                        role_arn="roleArn",
                        stream_name="streamName",
                
                        # the properties below are optional
                        partition_key="partitionKey"
                    ),
                    lambda_=iot.CfnTopicRule.LambdaActionProperty(
                        function_arn="functionArn"
                    ),
                    open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                        endpoint="endpoint",
                        id="id",
                        index="index",
                        role_arn="roleArn",
                        type="type"
                    ),
                    republish=iot.CfnTopicRule.RepublishActionProperty(
                        role_arn="roleArn",
                        topic="topic",
                
                        # the properties below are optional
                        qos=123
                    ),
                    s3=iot.CfnTopicRule.S3ActionProperty(
                        bucket_name="bucketName",
                        key="key",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        canned_acl="cannedAcl"
                    ),
                    sns=iot.CfnTopicRule.SnsActionProperty(
                        role_arn="roleArn",
                        target_arn="targetArn",
                
                        # the properties below are optional
                        message_format="messageFormat"
                    ),
                    sqs=iot.CfnTopicRule.SqsActionProperty(
                        queue_url="queueUrl",
                        role_arn="roleArn",
                
                        # the properties below are optional
                        use_base64=False
                    ),
                    step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                        role_arn="roleArn",
                        state_machine_name="stateMachineName",
                
                        # the properties below are optional
                        execution_name_prefix="executionNamePrefix"
                    ),
                    timestream=iot.CfnTopicRule.TimestreamActionProperty(
                        database_name="databaseName",
                        dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                            name="name",
                            value="value"
                        )],
                        role_arn="roleArn",
                        table_name="tableName",
                
                        # the properties below are optional
                        batch_mode=False,
                        timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                            unit="unit",
                            value="value"
                        )
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if cloudwatch_alarm is not None:
                self._values["cloudwatch_alarm"] = cloudwatch_alarm
            if cloudwatch_logs is not None:
                self._values["cloudwatch_logs"] = cloudwatch_logs
            if cloudwatch_metric is not None:
                self._values["cloudwatch_metric"] = cloudwatch_metric
            if dynamo_db is not None:
                self._values["dynamo_db"] = dynamo_db
            if dynamo_d_bv2 is not None:
                self._values["dynamo_d_bv2"] = dynamo_d_bv2
            if elasticsearch is not None:
                self._values["elasticsearch"] = elasticsearch
            if firehose is not None:
                self._values["firehose"] = firehose
            if http is not None:
                self._values["http"] = http
            if iot_analytics is not None:
                self._values["iot_analytics"] = iot_analytics
            if iot_events is not None:
                self._values["iot_events"] = iot_events
            if iot_site_wise is not None:
                self._values["iot_site_wise"] = iot_site_wise
            if kafka is not None:
                self._values["kafka"] = kafka
            if kinesis is not None:
                self._values["kinesis"] = kinesis
            if lambda_ is not None:
                self._values["lambda_"] = lambda_
            if open_search is not None:
                self._values["open_search"] = open_search
            if republish is not None:
                self._values["republish"] = republish
            if s3 is not None:
                self._values["s3"] = s3
            if sns is not None:
                self._values["sns"] = sns
            if sqs is not None:
                self._values["sqs"] = sqs
            if step_functions is not None:
                self._values["step_functions"] = step_functions
            if timestream is not None:
                self._values["timestream"] = timestream

        @builtins.property
        def cloudwatch_alarm(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.CloudwatchAlarmActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.CloudwatchAlarm``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchalarm
            '''
            result = self._values.get("cloudwatch_alarm")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.CloudwatchAlarmActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def cloudwatch_logs(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.CloudwatchLogsActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.CloudwatchLogs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchlogs
            '''
            result = self._values.get("cloudwatch_logs")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.CloudwatchLogsActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def cloudwatch_metric(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.CloudwatchMetricActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.CloudwatchMetric``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-cloudwatchmetric
            '''
            result = self._values.get("cloudwatch_metric")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.CloudwatchMetricActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def dynamo_db(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.DynamoDBActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.DynamoDB``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodb
            '''
            result = self._values.get("dynamo_db")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.DynamoDBActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def dynamo_d_bv2(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.DynamoDBv2ActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.DynamoDBv2``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-dynamodbv2
            '''
            result = self._values.get("dynamo_d_bv2")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.DynamoDBv2ActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def elasticsearch(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.ElasticsearchActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Elasticsearch``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-elasticsearch
            '''
            result = self._values.get("elasticsearch")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.ElasticsearchActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def firehose(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.FirehoseActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Firehose``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-firehose
            '''
            result = self._values.get("firehose")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.FirehoseActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def http(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.HttpActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Http``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-http
            '''
            result = self._values.get("http")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.HttpActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_analytics(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.IotAnalyticsActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.IotAnalytics``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-iotanalytics
            '''
            result = self._values.get("iot_analytics")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.IotAnalyticsActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_events(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.IotEventsActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.IotEvents``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-iotevents
            '''
            result = self._values.get("iot_events")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.IotEventsActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def iot_site_wise(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.IotSiteWiseActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.IotSiteWise``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-iotsitewise
            '''
            result = self._values.get("iot_site_wise")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.IotSiteWiseActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def kafka(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.KafkaActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Kafka``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-kafka
            '''
            result = self._values.get("kafka")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.KafkaActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def kinesis(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.KinesisActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Kinesis``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-kinesis
            '''
            result = self._values.get("kinesis")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.KinesisActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def lambda_(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.LambdaActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Lambda``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-lambda
            '''
            result = self._values.get("lambda_")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.LambdaActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def open_search(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.OpenSearchActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.OpenSearch``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-opensearch
            '''
            result = self._values.get("open_search")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.OpenSearchActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def republish(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.RepublishActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Republish``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-republish
            '''
            result = self._values.get("republish")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.RepublishActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def s3(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.S3ActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.S3``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-s3
            '''
            result = self._values.get("s3")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.S3ActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sns(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.SnsActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Sns``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sns
            '''
            result = self._values.get("sns")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.SnsActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def sqs(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.SqsActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Sqs``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-sqs
            '''
            result = self._values.get("sqs")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.SqsActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def step_functions(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.StepFunctionsActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.StepFunctions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-stepfunctions
            '''
            result = self._values.get("step_functions")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.StepFunctionsActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def timestream(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.TimestreamActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.ActionProperty.Timestream``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-action.html#cfn-iot-topicrule-action-timestream
            '''
            result = self._values.get("timestream")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.TimestreamActionProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.AssetPropertyTimestampProperty",
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
            :param offset_in_nanos: ``CfnTopicRule.AssetPropertyTimestampProperty.OffsetInNanos``.
            :param time_in_seconds: ``CfnTopicRule.AssetPropertyTimestampProperty.TimeInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertytimestamp.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                asset_property_timestamp_property = iot.CfnTopicRule.AssetPropertyTimestampProperty(
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
            '''``CfnTopicRule.AssetPropertyTimestampProperty.OffsetInNanos``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertytimestamp.html#cfn-iot-topicrule-assetpropertytimestamp-offsetinnanos
            '''
            result = self._values.get("offset_in_nanos")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def time_in_seconds(self) -> builtins.str:
            '''``CfnTopicRule.AssetPropertyTimestampProperty.TimeInSeconds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertytimestamp.html#cfn-iot-topicrule-assetpropertytimestamp-timeinseconds
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
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.AssetPropertyValueProperty",
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
            timestamp: typing.Union["CfnTopicRule.AssetPropertyTimestampProperty", _IResolvable_da3f097b],
            value: typing.Union["CfnTopicRule.AssetPropertyVariantProperty", _IResolvable_da3f097b],
        ) -> None:
            '''
            :param quality: ``CfnTopicRule.AssetPropertyValueProperty.Quality``.
            :param timestamp: ``CfnTopicRule.AssetPropertyValueProperty.Timestamp``.
            :param value: ``CfnTopicRule.AssetPropertyValueProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvalue.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                asset_property_value_property = iot.CfnTopicRule.AssetPropertyValueProperty(
                    timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                        time_in_seconds="timeInSeconds",
                
                        # the properties below are optional
                        offset_in_nanos="offsetInNanos"
                    ),
                    value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                        boolean_value="booleanValue",
                        double_value="doubleValue",
                        integer_value="integerValue",
                        string_value="stringValue"
                    ),
                
                    # the properties below are optional
                    quality="quality"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "timestamp": timestamp,
                "value": value,
            }
            if quality is not None:
                self._values["quality"] = quality

        @builtins.property
        def quality(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.AssetPropertyValueProperty.Quality``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvalue.html#cfn-iot-topicrule-assetpropertyvalue-quality
            '''
            result = self._values.get("quality")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def timestamp(
            self,
        ) -> typing.Union["CfnTopicRule.AssetPropertyTimestampProperty", _IResolvable_da3f097b]:
            '''``CfnTopicRule.AssetPropertyValueProperty.Timestamp``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvalue.html#cfn-iot-topicrule-assetpropertyvalue-timestamp
            '''
            result = self._values.get("timestamp")
            assert result is not None, "Required property 'timestamp' is missing"
            return typing.cast(typing.Union["CfnTopicRule.AssetPropertyTimestampProperty", _IResolvable_da3f097b], result)

        @builtins.property
        def value(
            self,
        ) -> typing.Union["CfnTopicRule.AssetPropertyVariantProperty", _IResolvable_da3f097b]:
            '''``CfnTopicRule.AssetPropertyValueProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvalue.html#cfn-iot-topicrule-assetpropertyvalue-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(typing.Union["CfnTopicRule.AssetPropertyVariantProperty", _IResolvable_da3f097b], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AssetPropertyValueProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.AssetPropertyVariantProperty",
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
            :param boolean_value: ``CfnTopicRule.AssetPropertyVariantProperty.BooleanValue``.
            :param double_value: ``CfnTopicRule.AssetPropertyVariantProperty.DoubleValue``.
            :param integer_value: ``CfnTopicRule.AssetPropertyVariantProperty.IntegerValue``.
            :param string_value: ``CfnTopicRule.AssetPropertyVariantProperty.StringValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvariant.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                asset_property_variant_property = iot.CfnTopicRule.AssetPropertyVariantProperty(
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
            '''``CfnTopicRule.AssetPropertyVariantProperty.BooleanValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvariant.html#cfn-iot-topicrule-assetpropertyvariant-booleanvalue
            '''
            result = self._values.get("boolean_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def double_value(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.AssetPropertyVariantProperty.DoubleValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvariant.html#cfn-iot-topicrule-assetpropertyvariant-doublevalue
            '''
            result = self._values.get("double_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def integer_value(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.AssetPropertyVariantProperty.IntegerValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvariant.html#cfn-iot-topicrule-assetpropertyvariant-integervalue
            '''
            result = self._values.get("integer_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def string_value(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.AssetPropertyVariantProperty.StringValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-assetpropertyvariant.html#cfn-iot-topicrule-assetpropertyvariant-stringvalue
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
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.CloudwatchAlarmActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "alarm_name": "alarmName",
            "role_arn": "roleArn",
            "state_reason": "stateReason",
            "state_value": "stateValue",
        },
    )
    class CloudwatchAlarmActionProperty:
        def __init__(
            self,
            *,
            alarm_name: builtins.str,
            role_arn: builtins.str,
            state_reason: builtins.str,
            state_value: builtins.str,
        ) -> None:
            '''
            :param alarm_name: ``CfnTopicRule.CloudwatchAlarmActionProperty.AlarmName``.
            :param role_arn: ``CfnTopicRule.CloudwatchAlarmActionProperty.RoleArn``.
            :param state_reason: ``CfnTopicRule.CloudwatchAlarmActionProperty.StateReason``.
            :param state_value: ``CfnTopicRule.CloudwatchAlarmActionProperty.StateValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                cloudwatch_alarm_action_property = iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                    alarm_name="alarmName",
                    role_arn="roleArn",
                    state_reason="stateReason",
                    state_value="stateValue"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "alarm_name": alarm_name,
                "role_arn": role_arn,
                "state_reason": state_reason,
                "state_value": state_value,
            }

        @builtins.property
        def alarm_name(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchAlarmActionProperty.AlarmName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-alarmname
            '''
            result = self._values.get("alarm_name")
            assert result is not None, "Required property 'alarm_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchAlarmActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def state_reason(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchAlarmActionProperty.StateReason``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statereason
            '''
            result = self._values.get("state_reason")
            assert result is not None, "Required property 'state_reason' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def state_value(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchAlarmActionProperty.StateValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchalarmaction.html#cfn-iot-topicrule-cloudwatchalarmaction-statevalue
            '''
            result = self._values.get("state_value")
            assert result is not None, "Required property 'state_value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudwatchAlarmActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.CloudwatchLogsActionProperty",
        jsii_struct_bases=[],
        name_mapping={"log_group_name": "logGroupName", "role_arn": "roleArn"},
    )
    class CloudwatchLogsActionProperty:
        def __init__(
            self,
            *,
            log_group_name: builtins.str,
            role_arn: builtins.str,
        ) -> None:
            '''
            :param log_group_name: ``CfnTopicRule.CloudwatchLogsActionProperty.LogGroupName``.
            :param role_arn: ``CfnTopicRule.CloudwatchLogsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchlogsaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                cloudwatch_logs_action_property = iot.CfnTopicRule.CloudwatchLogsActionProperty(
                    log_group_name="logGroupName",
                    role_arn="roleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "log_group_name": log_group_name,
                "role_arn": role_arn,
            }

        @builtins.property
        def log_group_name(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchLogsActionProperty.LogGroupName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchlogsaction.html#cfn-iot-topicrule-cloudwatchlogsaction-loggroupname
            '''
            result = self._values.get("log_group_name")
            assert result is not None, "Required property 'log_group_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchLogsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchlogsaction.html#cfn-iot-topicrule-cloudwatchlogsaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudwatchLogsActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.CloudwatchMetricActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "metric_name": "metricName",
            "metric_namespace": "metricNamespace",
            "metric_timestamp": "metricTimestamp",
            "metric_unit": "metricUnit",
            "metric_value": "metricValue",
            "role_arn": "roleArn",
        },
    )
    class CloudwatchMetricActionProperty:
        def __init__(
            self,
            *,
            metric_name: builtins.str,
            metric_namespace: builtins.str,
            metric_timestamp: typing.Optional[builtins.str] = None,
            metric_unit: builtins.str,
            metric_value: builtins.str,
            role_arn: builtins.str,
        ) -> None:
            '''
            :param metric_name: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricName``.
            :param metric_namespace: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricNamespace``.
            :param metric_timestamp: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricTimestamp``.
            :param metric_unit: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricUnit``.
            :param metric_value: ``CfnTopicRule.CloudwatchMetricActionProperty.MetricValue``.
            :param role_arn: ``CfnTopicRule.CloudwatchMetricActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                cloudwatch_metric_action_property = iot.CfnTopicRule.CloudwatchMetricActionProperty(
                    metric_name="metricName",
                    metric_namespace="metricNamespace",
                    metric_unit="metricUnit",
                    metric_value="metricValue",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    metric_timestamp="metricTimestamp"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "metric_name": metric_name,
                "metric_namespace": metric_namespace,
                "metric_unit": metric_unit,
                "metric_value": metric_value,
                "role_arn": role_arn,
            }
            if metric_timestamp is not None:
                self._values["metric_timestamp"] = metric_timestamp

        @builtins.property
        def metric_name(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchMetricActionProperty.MetricName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricname
            '''
            result = self._values.get("metric_name")
            assert result is not None, "Required property 'metric_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def metric_namespace(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchMetricActionProperty.MetricNamespace``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricnamespace
            '''
            result = self._values.get("metric_namespace")
            assert result is not None, "Required property 'metric_namespace' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def metric_timestamp(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.CloudwatchMetricActionProperty.MetricTimestamp``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metrictimestamp
            '''
            result = self._values.get("metric_timestamp")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def metric_unit(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchMetricActionProperty.MetricUnit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricunit
            '''
            result = self._values.get("metric_unit")
            assert result is not None, "Required property 'metric_unit' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def metric_value(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchMetricActionProperty.MetricValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-metricvalue
            '''
            result = self._values.get("metric_value")
            assert result is not None, "Required property 'metric_value' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.CloudwatchMetricActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-cloudwatchmetricaction.html#cfn-iot-topicrule-cloudwatchmetricaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CloudwatchMetricActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.DynamoDBActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "hash_key_field": "hashKeyField",
            "hash_key_type": "hashKeyType",
            "hash_key_value": "hashKeyValue",
            "payload_field": "payloadField",
            "range_key_field": "rangeKeyField",
            "range_key_type": "rangeKeyType",
            "range_key_value": "rangeKeyValue",
            "role_arn": "roleArn",
            "table_name": "tableName",
        },
    )
    class DynamoDBActionProperty:
        def __init__(
            self,
            *,
            hash_key_field: builtins.str,
            hash_key_type: typing.Optional[builtins.str] = None,
            hash_key_value: builtins.str,
            payload_field: typing.Optional[builtins.str] = None,
            range_key_field: typing.Optional[builtins.str] = None,
            range_key_type: typing.Optional[builtins.str] = None,
            range_key_value: typing.Optional[builtins.str] = None,
            role_arn: builtins.str,
            table_name: builtins.str,
        ) -> None:
            '''
            :param hash_key_field: ``CfnTopicRule.DynamoDBActionProperty.HashKeyField``.
            :param hash_key_type: ``CfnTopicRule.DynamoDBActionProperty.HashKeyType``.
            :param hash_key_value: ``CfnTopicRule.DynamoDBActionProperty.HashKeyValue``.
            :param payload_field: ``CfnTopicRule.DynamoDBActionProperty.PayloadField``.
            :param range_key_field: ``CfnTopicRule.DynamoDBActionProperty.RangeKeyField``.
            :param range_key_type: ``CfnTopicRule.DynamoDBActionProperty.RangeKeyType``.
            :param range_key_value: ``CfnTopicRule.DynamoDBActionProperty.RangeKeyValue``.
            :param role_arn: ``CfnTopicRule.DynamoDBActionProperty.RoleArn``.
            :param table_name: ``CfnTopicRule.DynamoDBActionProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                dynamo_dBAction_property = iot.CfnTopicRule.DynamoDBActionProperty(
                    hash_key_field="hashKeyField",
                    hash_key_value="hashKeyValue",
                    role_arn="roleArn",
                    table_name="tableName",
                
                    # the properties below are optional
                    hash_key_type="hashKeyType",
                    payload_field="payloadField",
                    range_key_field="rangeKeyField",
                    range_key_type="rangeKeyType",
                    range_key_value="rangeKeyValue"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "hash_key_field": hash_key_field,
                "hash_key_value": hash_key_value,
                "role_arn": role_arn,
                "table_name": table_name,
            }
            if hash_key_type is not None:
                self._values["hash_key_type"] = hash_key_type
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
            '''``CfnTopicRule.DynamoDBActionProperty.HashKeyField``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyfield
            '''
            result = self._values.get("hash_key_field")
            assert result is not None, "Required property 'hash_key_field' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def hash_key_type(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.DynamoDBActionProperty.HashKeyType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeytype
            '''
            result = self._values.get("hash_key_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def hash_key_value(self) -> builtins.str:
            '''``CfnTopicRule.DynamoDBActionProperty.HashKeyValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-hashkeyvalue
            '''
            result = self._values.get("hash_key_value")
            assert result is not None, "Required property 'hash_key_value' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def payload_field(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.DynamoDBActionProperty.PayloadField``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-payloadfield
            '''
            result = self._values.get("payload_field")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def range_key_field(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.DynamoDBActionProperty.RangeKeyField``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyfield
            '''
            result = self._values.get("range_key_field")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def range_key_type(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.DynamoDBActionProperty.RangeKeyType``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeytype
            '''
            result = self._values.get("range_key_type")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def range_key_value(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.DynamoDBActionProperty.RangeKeyValue``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rangekeyvalue
            '''
            result = self._values.get("range_key_value")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.DynamoDBActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def table_name(self) -> builtins.str:
            '''``CfnTopicRule.DynamoDBActionProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbaction.html#cfn-iot-topicrule-dynamodbaction-tablename
            '''
            result = self._values.get("table_name")
            assert result is not None, "Required property 'table_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDBActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.DynamoDBv2ActionProperty",
        jsii_struct_bases=[],
        name_mapping={"put_item": "putItem", "role_arn": "roleArn"},
    )
    class DynamoDBv2ActionProperty:
        def __init__(
            self,
            *,
            put_item: typing.Optional[typing.Union["CfnTopicRule.PutItemInputProperty", _IResolvable_da3f097b]] = None,
            role_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param put_item: ``CfnTopicRule.DynamoDBv2ActionProperty.PutItem``.
            :param role_arn: ``CfnTopicRule.DynamoDBv2ActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                dynamo_dBv2_action_property = iot.CfnTopicRule.DynamoDBv2ActionProperty(
                    put_item=iot.CfnTopicRule.PutItemInputProperty(
                        table_name="tableName"
                    ),
                    role_arn="roleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if put_item is not None:
                self._values["put_item"] = put_item
            if role_arn is not None:
                self._values["role_arn"] = role_arn

        @builtins.property
        def put_item(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.PutItemInputProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.DynamoDBv2ActionProperty.PutItem``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-putitem
            '''
            result = self._values.get("put_item")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.PutItemInputProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.DynamoDBv2ActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-dynamodbv2action.html#cfn-iot-topicrule-dynamodbv2action-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DynamoDBv2ActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.ElasticsearchActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "endpoint": "endpoint",
            "id": "id",
            "index": "index",
            "role_arn": "roleArn",
            "type": "type",
        },
    )
    class ElasticsearchActionProperty:
        def __init__(
            self,
            *,
            endpoint: builtins.str,
            id: builtins.str,
            index: builtins.str,
            role_arn: builtins.str,
            type: builtins.str,
        ) -> None:
            '''
            :param endpoint: ``CfnTopicRule.ElasticsearchActionProperty.Endpoint``.
            :param id: ``CfnTopicRule.ElasticsearchActionProperty.Id``.
            :param index: ``CfnTopicRule.ElasticsearchActionProperty.Index``.
            :param role_arn: ``CfnTopicRule.ElasticsearchActionProperty.RoleArn``.
            :param type: ``CfnTopicRule.ElasticsearchActionProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                elasticsearch_action_property = iot.CfnTopicRule.ElasticsearchActionProperty(
                    endpoint="endpoint",
                    id="id",
                    index="index",
                    role_arn="roleArn",
                    type="type"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "endpoint": endpoint,
                "id": id,
                "index": index,
                "role_arn": role_arn,
                "type": type,
            }

        @builtins.property
        def endpoint(self) -> builtins.str:
            '''``CfnTopicRule.ElasticsearchActionProperty.Endpoint``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-endpoint
            '''
            result = self._values.get("endpoint")
            assert result is not None, "Required property 'endpoint' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnTopicRule.ElasticsearchActionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def index(self) -> builtins.str:
            '''``CfnTopicRule.ElasticsearchActionProperty.Index``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-index
            '''
            result = self._values.get("index")
            assert result is not None, "Required property 'index' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.ElasticsearchActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnTopicRule.ElasticsearchActionProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-elasticsearchaction.html#cfn-iot-topicrule-elasticsearchaction-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ElasticsearchActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.FirehoseActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "batch_mode": "batchMode",
            "delivery_stream_name": "deliveryStreamName",
            "role_arn": "roleArn",
            "separator": "separator",
        },
    )
    class FirehoseActionProperty:
        def __init__(
            self,
            *,
            batch_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            delivery_stream_name: builtins.str,
            role_arn: builtins.str,
            separator: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param batch_mode: ``CfnTopicRule.FirehoseActionProperty.BatchMode``.
            :param delivery_stream_name: ``CfnTopicRule.FirehoseActionProperty.DeliveryStreamName``.
            :param role_arn: ``CfnTopicRule.FirehoseActionProperty.RoleArn``.
            :param separator: ``CfnTopicRule.FirehoseActionProperty.Separator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                firehose_action_property = iot.CfnTopicRule.FirehoseActionProperty(
                    delivery_stream_name="deliveryStreamName",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    batch_mode=False,
                    separator="separator"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "delivery_stream_name": delivery_stream_name,
                "role_arn": role_arn,
            }
            if batch_mode is not None:
                self._values["batch_mode"] = batch_mode
            if separator is not None:
                self._values["separator"] = separator

        @builtins.property
        def batch_mode(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTopicRule.FirehoseActionProperty.BatchMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-batchmode
            '''
            result = self._values.get("batch_mode")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def delivery_stream_name(self) -> builtins.str:
            '''``CfnTopicRule.FirehoseActionProperty.DeliveryStreamName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-deliverystreamname
            '''
            result = self._values.get("delivery_stream_name")
            assert result is not None, "Required property 'delivery_stream_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.FirehoseActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def separator(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.FirehoseActionProperty.Separator``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-firehoseaction.html#cfn-iot-topicrule-firehoseaction-separator
            '''
            result = self._values.get("separator")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "FirehoseActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.HttpActionHeaderProperty",
        jsii_struct_bases=[],
        name_mapping={"key": "key", "value": "value"},
    )
    class HttpActionHeaderProperty:
        def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
            '''
            :param key: ``CfnTopicRule.HttpActionHeaderProperty.Key``.
            :param value: ``CfnTopicRule.HttpActionHeaderProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpactionheader.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                http_action_header_property = iot.CfnTopicRule.HttpActionHeaderProperty(
                    key="key",
                    value="value"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "key": key,
                "value": value,
            }

        @builtins.property
        def key(self) -> builtins.str:
            '''``CfnTopicRule.HttpActionHeaderProperty.Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpactionheader.html#cfn-iot-topicrule-httpactionheader-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''``CfnTopicRule.HttpActionHeaderProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpactionheader.html#cfn-iot-topicrule-httpactionheader-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpActionHeaderProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.HttpActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "auth": "auth",
            "confirmation_url": "confirmationUrl",
            "headers": "headers",
            "url": "url",
        },
    )
    class HttpActionProperty:
        def __init__(
            self,
            *,
            auth: typing.Optional[typing.Union["CfnTopicRule.HttpAuthorizationProperty", _IResolvable_da3f097b]] = None,
            confirmation_url: typing.Optional[builtins.str] = None,
            headers: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTopicRule.HttpActionHeaderProperty", _IResolvable_da3f097b]]]] = None,
            url: builtins.str,
        ) -> None:
            '''
            :param auth: ``CfnTopicRule.HttpActionProperty.Auth``.
            :param confirmation_url: ``CfnTopicRule.HttpActionProperty.ConfirmationUrl``.
            :param headers: ``CfnTopicRule.HttpActionProperty.Headers``.
            :param url: ``CfnTopicRule.HttpActionProperty.Url``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                http_action_property = iot.CfnTopicRule.HttpActionProperty(
                    url="url",
                
                    # the properties below are optional
                    auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                        sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                            role_arn="roleArn",
                            service_name="serviceName",
                            signing_region="signingRegion"
                        )
                    ),
                    confirmation_url="confirmationUrl",
                    headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                        key="key",
                        value="value"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "url": url,
            }
            if auth is not None:
                self._values["auth"] = auth
            if confirmation_url is not None:
                self._values["confirmation_url"] = confirmation_url
            if headers is not None:
                self._values["headers"] = headers

        @builtins.property
        def auth(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.HttpAuthorizationProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.HttpActionProperty.Auth``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpaction.html#cfn-iot-topicrule-httpaction-auth
            '''
            result = self._values.get("auth")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.HttpAuthorizationProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def confirmation_url(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.HttpActionProperty.ConfirmationUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpaction.html#cfn-iot-topicrule-httpaction-confirmationurl
            '''
            result = self._values.get("confirmation_url")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def headers(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.HttpActionHeaderProperty", _IResolvable_da3f097b]]]]:
            '''``CfnTopicRule.HttpActionProperty.Headers``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpaction.html#cfn-iot-topicrule-httpaction-headers
            '''
            result = self._values.get("headers")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.HttpActionHeaderProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def url(self) -> builtins.str:
            '''``CfnTopicRule.HttpActionProperty.Url``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpaction.html#cfn-iot-topicrule-httpaction-url
            '''
            result = self._values.get("url")
            assert result is not None, "Required property 'url' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.HttpAuthorizationProperty",
        jsii_struct_bases=[],
        name_mapping={"sigv4": "sigv4"},
    )
    class HttpAuthorizationProperty:
        def __init__(
            self,
            *,
            sigv4: typing.Optional[typing.Union["CfnTopicRule.SigV4AuthorizationProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param sigv4: ``CfnTopicRule.HttpAuthorizationProperty.Sigv4``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpauthorization.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                http_authorization_property = iot.CfnTopicRule.HttpAuthorizationProperty(
                    sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                        role_arn="roleArn",
                        service_name="serviceName",
                        signing_region="signingRegion"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if sigv4 is not None:
                self._values["sigv4"] = sigv4

        @builtins.property
        def sigv4(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.SigV4AuthorizationProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.HttpAuthorizationProperty.Sigv4``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-httpauthorization.html#cfn-iot-topicrule-httpauthorization-sigv4
            '''
            result = self._values.get("sigv4")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.SigV4AuthorizationProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpAuthorizationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.IotAnalyticsActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "batch_mode": "batchMode",
            "channel_name": "channelName",
            "role_arn": "roleArn",
        },
    )
    class IotAnalyticsActionProperty:
        def __init__(
            self,
            *,
            batch_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            channel_name: builtins.str,
            role_arn: builtins.str,
        ) -> None:
            '''
            :param batch_mode: ``CfnTopicRule.IotAnalyticsActionProperty.BatchMode``.
            :param channel_name: ``CfnTopicRule.IotAnalyticsActionProperty.ChannelName``.
            :param role_arn: ``CfnTopicRule.IotAnalyticsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                iot_analytics_action_property = iot.CfnTopicRule.IotAnalyticsActionProperty(
                    channel_name="channelName",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    batch_mode=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "channel_name": channel_name,
                "role_arn": role_arn,
            }
            if batch_mode is not None:
                self._values["batch_mode"] = batch_mode

        @builtins.property
        def batch_mode(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTopicRule.IotAnalyticsActionProperty.BatchMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-batchmode
            '''
            result = self._values.get("batch_mode")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def channel_name(self) -> builtins.str:
            '''``CfnTopicRule.IotAnalyticsActionProperty.ChannelName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-channelname
            '''
            result = self._values.get("channel_name")
            assert result is not None, "Required property 'channel_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.IotAnalyticsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotanalyticsaction.html#cfn-iot-topicrule-iotanalyticsaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IotAnalyticsActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.IotEventsActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "batch_mode": "batchMode",
            "input_name": "inputName",
            "message_id": "messageId",
            "role_arn": "roleArn",
        },
    )
    class IotEventsActionProperty:
        def __init__(
            self,
            *,
            batch_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            input_name: builtins.str,
            message_id: typing.Optional[builtins.str] = None,
            role_arn: builtins.str,
        ) -> None:
            '''
            :param batch_mode: ``CfnTopicRule.IotEventsActionProperty.BatchMode``.
            :param input_name: ``CfnTopicRule.IotEventsActionProperty.InputName``.
            :param message_id: ``CfnTopicRule.IotEventsActionProperty.MessageId``.
            :param role_arn: ``CfnTopicRule.IotEventsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-ioteventsaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                iot_events_action_property = iot.CfnTopicRule.IotEventsActionProperty(
                    input_name="inputName",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    batch_mode=False,
                    message_id="messageId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "input_name": input_name,
                "role_arn": role_arn,
            }
            if batch_mode is not None:
                self._values["batch_mode"] = batch_mode
            if message_id is not None:
                self._values["message_id"] = message_id

        @builtins.property
        def batch_mode(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTopicRule.IotEventsActionProperty.BatchMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-ioteventsaction.html#cfn-iot-topicrule-ioteventsaction-batchmode
            '''
            result = self._values.get("batch_mode")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def input_name(self) -> builtins.str:
            '''``CfnTopicRule.IotEventsActionProperty.InputName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-ioteventsaction.html#cfn-iot-topicrule-ioteventsaction-inputname
            '''
            result = self._values.get("input_name")
            assert result is not None, "Required property 'input_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def message_id(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.IotEventsActionProperty.MessageId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-ioteventsaction.html#cfn-iot-topicrule-ioteventsaction-messageid
            '''
            result = self._values.get("message_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.IotEventsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-ioteventsaction.html#cfn-iot-topicrule-ioteventsaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IotEventsActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.IotSiteWiseActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "put_asset_property_value_entries": "putAssetPropertyValueEntries",
            "role_arn": "roleArn",
        },
    )
    class IotSiteWiseActionProperty:
        def __init__(
            self,
            *,
            put_asset_property_value_entries: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTopicRule.PutAssetPropertyValueEntryProperty", _IResolvable_da3f097b]]],
            role_arn: builtins.str,
        ) -> None:
            '''
            :param put_asset_property_value_entries: ``CfnTopicRule.IotSiteWiseActionProperty.PutAssetPropertyValueEntries``.
            :param role_arn: ``CfnTopicRule.IotSiteWiseActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotsitewiseaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                iot_site_wise_action_property = iot.CfnTopicRule.IotSiteWiseActionProperty(
                    put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                        property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                            timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                time_in_seconds="timeInSeconds",
                
                                # the properties below are optional
                                offset_in_nanos="offsetInNanos"
                            ),
                            value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                boolean_value="booleanValue",
                                double_value="doubleValue",
                                integer_value="integerValue",
                                string_value="stringValue"
                            ),
                
                            # the properties below are optional
                            quality="quality"
                        )],
                
                        # the properties below are optional
                        asset_id="assetId",
                        entry_id="entryId",
                        property_alias="propertyAlias",
                        property_id="propertyId"
                    )],
                    role_arn="roleArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "put_asset_property_value_entries": put_asset_property_value_entries,
                "role_arn": role_arn,
            }

        @builtins.property
        def put_asset_property_value_entries(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.PutAssetPropertyValueEntryProperty", _IResolvable_da3f097b]]]:
            '''``CfnTopicRule.IotSiteWiseActionProperty.PutAssetPropertyValueEntries``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotsitewiseaction.html#cfn-iot-topicrule-iotsitewiseaction-putassetpropertyvalueentries
            '''
            result = self._values.get("put_asset_property_value_entries")
            assert result is not None, "Required property 'put_asset_property_value_entries' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.PutAssetPropertyValueEntryProperty", _IResolvable_da3f097b]]], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.IotSiteWiseActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-iotsitewiseaction.html#cfn-iot-topicrule-iotsitewiseaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "IotSiteWiseActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.KafkaActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "client_properties": "clientProperties",
            "destination_arn": "destinationArn",
            "key": "key",
            "partition": "partition",
            "topic": "topic",
        },
    )
    class KafkaActionProperty:
        def __init__(
            self,
            *,
            client_properties: typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]],
            destination_arn: builtins.str,
            key: typing.Optional[builtins.str] = None,
            partition: typing.Optional[builtins.str] = None,
            topic: builtins.str,
        ) -> None:
            '''
            :param client_properties: ``CfnTopicRule.KafkaActionProperty.ClientProperties``.
            :param destination_arn: ``CfnTopicRule.KafkaActionProperty.DestinationArn``.
            :param key: ``CfnTopicRule.KafkaActionProperty.Key``.
            :param partition: ``CfnTopicRule.KafkaActionProperty.Partition``.
            :param topic: ``CfnTopicRule.KafkaActionProperty.Topic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kafkaaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                kafka_action_property = iot.CfnTopicRule.KafkaActionProperty(
                    client_properties={
                        "client_properties_key": "clientProperties"
                    },
                    destination_arn="destinationArn",
                    topic="topic",
                
                    # the properties below are optional
                    key="key",
                    partition="partition"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "client_properties": client_properties,
                "destination_arn": destination_arn,
                "topic": topic,
            }
            if key is not None:
                self._values["key"] = key
            if partition is not None:
                self._values["partition"] = partition

        @builtins.property
        def client_properties(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]]:
            '''``CfnTopicRule.KafkaActionProperty.ClientProperties``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kafkaaction.html#cfn-iot-topicrule-kafkaaction-clientproperties
            '''
            result = self._values.get("client_properties")
            assert result is not None, "Required property 'client_properties' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.Mapping[builtins.str, builtins.str]], result)

        @builtins.property
        def destination_arn(self) -> builtins.str:
            '''``CfnTopicRule.KafkaActionProperty.DestinationArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kafkaaction.html#cfn-iot-topicrule-kafkaaction-destinationarn
            '''
            result = self._values.get("destination_arn")
            assert result is not None, "Required property 'destination_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def key(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.KafkaActionProperty.Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kafkaaction.html#cfn-iot-topicrule-kafkaaction-key
            '''
            result = self._values.get("key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def partition(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.KafkaActionProperty.Partition``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kafkaaction.html#cfn-iot-topicrule-kafkaaction-partition
            '''
            result = self._values.get("partition")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def topic(self) -> builtins.str:
            '''``CfnTopicRule.KafkaActionProperty.Topic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kafkaaction.html#cfn-iot-topicrule-kafkaaction-topic
            '''
            result = self._values.get("topic")
            assert result is not None, "Required property 'topic' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KafkaActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.KinesisActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "partition_key": "partitionKey",
            "role_arn": "roleArn",
            "stream_name": "streamName",
        },
    )
    class KinesisActionProperty:
        def __init__(
            self,
            *,
            partition_key: typing.Optional[builtins.str] = None,
            role_arn: builtins.str,
            stream_name: builtins.str,
        ) -> None:
            '''
            :param partition_key: ``CfnTopicRule.KinesisActionProperty.PartitionKey``.
            :param role_arn: ``CfnTopicRule.KinesisActionProperty.RoleArn``.
            :param stream_name: ``CfnTopicRule.KinesisActionProperty.StreamName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                kinesis_action_property = iot.CfnTopicRule.KinesisActionProperty(
                    role_arn="roleArn",
                    stream_name="streamName",
                
                    # the properties below are optional
                    partition_key="partitionKey"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "role_arn": role_arn,
                "stream_name": stream_name,
            }
            if partition_key is not None:
                self._values["partition_key"] = partition_key

        @builtins.property
        def partition_key(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.KinesisActionProperty.PartitionKey``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-partitionkey
            '''
            result = self._values.get("partition_key")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.KinesisActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def stream_name(self) -> builtins.str:
            '''``CfnTopicRule.KinesisActionProperty.StreamName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-kinesisaction.html#cfn-iot-topicrule-kinesisaction-streamname
            '''
            result = self._values.get("stream_name")
            assert result is not None, "Required property 'stream_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "KinesisActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.LambdaActionProperty",
        jsii_struct_bases=[],
        name_mapping={"function_arn": "functionArn"},
    )
    class LambdaActionProperty:
        def __init__(
            self,
            *,
            function_arn: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param function_arn: ``CfnTopicRule.LambdaActionProperty.FunctionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                lambda_action_property = iot.CfnTopicRule.LambdaActionProperty(
                    function_arn="functionArn"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if function_arn is not None:
                self._values["function_arn"] = function_arn

        @builtins.property
        def function_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.LambdaActionProperty.FunctionArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-lambdaaction.html#cfn-iot-topicrule-lambdaaction-functionarn
            '''
            result = self._values.get("function_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "LambdaActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.OpenSearchActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "endpoint": "endpoint",
            "id": "id",
            "index": "index",
            "role_arn": "roleArn",
            "type": "type",
        },
    )
    class OpenSearchActionProperty:
        def __init__(
            self,
            *,
            endpoint: builtins.str,
            id: builtins.str,
            index: builtins.str,
            role_arn: builtins.str,
            type: builtins.str,
        ) -> None:
            '''
            :param endpoint: ``CfnTopicRule.OpenSearchActionProperty.Endpoint``.
            :param id: ``CfnTopicRule.OpenSearchActionProperty.Id``.
            :param index: ``CfnTopicRule.OpenSearchActionProperty.Index``.
            :param role_arn: ``CfnTopicRule.OpenSearchActionProperty.RoleArn``.
            :param type: ``CfnTopicRule.OpenSearchActionProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-opensearchaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                open_search_action_property = iot.CfnTopicRule.OpenSearchActionProperty(
                    endpoint="endpoint",
                    id="id",
                    index="index",
                    role_arn="roleArn",
                    type="type"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "endpoint": endpoint,
                "id": id,
                "index": index,
                "role_arn": role_arn,
                "type": type,
            }

        @builtins.property
        def endpoint(self) -> builtins.str:
            '''``CfnTopicRule.OpenSearchActionProperty.Endpoint``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-opensearchaction.html#cfn-iot-topicrule-opensearchaction-endpoint
            '''
            result = self._values.get("endpoint")
            assert result is not None, "Required property 'endpoint' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnTopicRule.OpenSearchActionProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-opensearchaction.html#cfn-iot-topicrule-opensearchaction-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def index(self) -> builtins.str:
            '''``CfnTopicRule.OpenSearchActionProperty.Index``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-opensearchaction.html#cfn-iot-topicrule-opensearchaction-index
            '''
            result = self._values.get("index")
            assert result is not None, "Required property 'index' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.OpenSearchActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-opensearchaction.html#cfn-iot-topicrule-opensearchaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnTopicRule.OpenSearchActionProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-opensearchaction.html#cfn-iot-topicrule-opensearchaction-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OpenSearchActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.PutAssetPropertyValueEntryProperty",
        jsii_struct_bases=[],
        name_mapping={
            "asset_id": "assetId",
            "entry_id": "entryId",
            "property_alias": "propertyAlias",
            "property_id": "propertyId",
            "property_values": "propertyValues",
        },
    )
    class PutAssetPropertyValueEntryProperty:
        def __init__(
            self,
            *,
            asset_id: typing.Optional[builtins.str] = None,
            entry_id: typing.Optional[builtins.str] = None,
            property_alias: typing.Optional[builtins.str] = None,
            property_id: typing.Optional[builtins.str] = None,
            property_values: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTopicRule.AssetPropertyValueProperty", _IResolvable_da3f097b]]],
        ) -> None:
            '''
            :param asset_id: ``CfnTopicRule.PutAssetPropertyValueEntryProperty.AssetId``.
            :param entry_id: ``CfnTopicRule.PutAssetPropertyValueEntryProperty.EntryId``.
            :param property_alias: ``CfnTopicRule.PutAssetPropertyValueEntryProperty.PropertyAlias``.
            :param property_id: ``CfnTopicRule.PutAssetPropertyValueEntryProperty.PropertyId``.
            :param property_values: ``CfnTopicRule.PutAssetPropertyValueEntryProperty.PropertyValues``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putassetpropertyvalueentry.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                put_asset_property_value_entry_property = iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                    property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                        timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                            time_in_seconds="timeInSeconds",
                
                            # the properties below are optional
                            offset_in_nanos="offsetInNanos"
                        ),
                        value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                            boolean_value="booleanValue",
                            double_value="doubleValue",
                            integer_value="integerValue",
                            string_value="stringValue"
                        ),
                
                        # the properties below are optional
                        quality="quality"
                    )],
                
                    # the properties below are optional
                    asset_id="assetId",
                    entry_id="entryId",
                    property_alias="propertyAlias",
                    property_id="propertyId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "property_values": property_values,
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
            '''``CfnTopicRule.PutAssetPropertyValueEntryProperty.AssetId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putassetpropertyvalueentry.html#cfn-iot-topicrule-putassetpropertyvalueentry-assetid
            '''
            result = self._values.get("asset_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def entry_id(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.PutAssetPropertyValueEntryProperty.EntryId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putassetpropertyvalueentry.html#cfn-iot-topicrule-putassetpropertyvalueentry-entryid
            '''
            result = self._values.get("entry_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def property_alias(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.PutAssetPropertyValueEntryProperty.PropertyAlias``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putassetpropertyvalueentry.html#cfn-iot-topicrule-putassetpropertyvalueentry-propertyalias
            '''
            result = self._values.get("property_alias")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def property_id(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.PutAssetPropertyValueEntryProperty.PropertyId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putassetpropertyvalueentry.html#cfn-iot-topicrule-putassetpropertyvalueentry-propertyid
            '''
            result = self._values.get("property_id")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def property_values(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.AssetPropertyValueProperty", _IResolvable_da3f097b]]]:
            '''``CfnTopicRule.PutAssetPropertyValueEntryProperty.PropertyValues``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putassetpropertyvalueentry.html#cfn-iot-topicrule-putassetpropertyvalueentry-propertyvalues
            '''
            result = self._values.get("property_values")
            assert result is not None, "Required property 'property_values' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.AssetPropertyValueProperty", _IResolvable_da3f097b]]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PutAssetPropertyValueEntryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.PutItemInputProperty",
        jsii_struct_bases=[],
        name_mapping={"table_name": "tableName"},
    )
    class PutItemInputProperty:
        def __init__(self, *, table_name: builtins.str) -> None:
            '''
            :param table_name: ``CfnTopicRule.PutItemInputProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                put_item_input_property = iot.CfnTopicRule.PutItemInputProperty(
                    table_name="tableName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "table_name": table_name,
            }

        @builtins.property
        def table_name(self) -> builtins.str:
            '''``CfnTopicRule.PutItemInputProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-putiteminput.html#cfn-iot-topicrule-putiteminput-tablename
            '''
            result = self._values.get("table_name")
            assert result is not None, "Required property 'table_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PutItemInputProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.RepublishActionProperty",
        jsii_struct_bases=[],
        name_mapping={"qos": "qos", "role_arn": "roleArn", "topic": "topic"},
    )
    class RepublishActionProperty:
        def __init__(
            self,
            *,
            qos: typing.Optional[jsii.Number] = None,
            role_arn: builtins.str,
            topic: builtins.str,
        ) -> None:
            '''
            :param qos: ``CfnTopicRule.RepublishActionProperty.Qos``.
            :param role_arn: ``CfnTopicRule.RepublishActionProperty.RoleArn``.
            :param topic: ``CfnTopicRule.RepublishActionProperty.Topic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                republish_action_property = iot.CfnTopicRule.RepublishActionProperty(
                    role_arn="roleArn",
                    topic="topic",
                
                    # the properties below are optional
                    qos=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "role_arn": role_arn,
                "topic": topic,
            }
            if qos is not None:
                self._values["qos"] = qos

        @builtins.property
        def qos(self) -> typing.Optional[jsii.Number]:
            '''``CfnTopicRule.RepublishActionProperty.Qos``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-qos
            '''
            result = self._values.get("qos")
            return typing.cast(typing.Optional[jsii.Number], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.RepublishActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def topic(self) -> builtins.str:
            '''``CfnTopicRule.RepublishActionProperty.Topic``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-republishaction.html#cfn-iot-topicrule-republishaction-topic
            '''
            result = self._values.get("topic")
            assert result is not None, "Required property 'topic' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RepublishActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.S3ActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "bucket_name": "bucketName",
            "canned_acl": "cannedAcl",
            "key": "key",
            "role_arn": "roleArn",
        },
    )
    class S3ActionProperty:
        def __init__(
            self,
            *,
            bucket_name: builtins.str,
            canned_acl: typing.Optional[builtins.str] = None,
            key: builtins.str,
            role_arn: builtins.str,
        ) -> None:
            '''
            :param bucket_name: ``CfnTopicRule.S3ActionProperty.BucketName``.
            :param canned_acl: ``CfnTopicRule.S3ActionProperty.CannedAcl``.
            :param key: ``CfnTopicRule.S3ActionProperty.Key``.
            :param role_arn: ``CfnTopicRule.S3ActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                s3_action_property = iot.CfnTopicRule.S3ActionProperty(
                    bucket_name="bucketName",
                    key="key",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    canned_acl="cannedAcl"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "bucket_name": bucket_name,
                "key": key,
                "role_arn": role_arn,
            }
            if canned_acl is not None:
                self._values["canned_acl"] = canned_acl

        @builtins.property
        def bucket_name(self) -> builtins.str:
            '''``CfnTopicRule.S3ActionProperty.BucketName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-bucketname
            '''
            result = self._values.get("bucket_name")
            assert result is not None, "Required property 'bucket_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def canned_acl(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.S3ActionProperty.CannedAcl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-cannedacl
            '''
            result = self._values.get("canned_acl")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def key(self) -> builtins.str:
            '''``CfnTopicRule.S3ActionProperty.Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.S3ActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-s3action.html#cfn-iot-topicrule-s3action-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3ActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.SigV4AuthorizationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "role_arn": "roleArn",
            "service_name": "serviceName",
            "signing_region": "signingRegion",
        },
    )
    class SigV4AuthorizationProperty:
        def __init__(
            self,
            *,
            role_arn: builtins.str,
            service_name: builtins.str,
            signing_region: builtins.str,
        ) -> None:
            '''
            :param role_arn: ``CfnTopicRule.SigV4AuthorizationProperty.RoleArn``.
            :param service_name: ``CfnTopicRule.SigV4AuthorizationProperty.ServiceName``.
            :param signing_region: ``CfnTopicRule.SigV4AuthorizationProperty.SigningRegion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sigv4authorization.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                sig_v4_authorization_property = iot.CfnTopicRule.SigV4AuthorizationProperty(
                    role_arn="roleArn",
                    service_name="serviceName",
                    signing_region="signingRegion"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "role_arn": role_arn,
                "service_name": service_name,
                "signing_region": signing_region,
            }

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.SigV4AuthorizationProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sigv4authorization.html#cfn-iot-topicrule-sigv4authorization-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def service_name(self) -> builtins.str:
            '''``CfnTopicRule.SigV4AuthorizationProperty.ServiceName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sigv4authorization.html#cfn-iot-topicrule-sigv4authorization-servicename
            '''
            result = self._values.get("service_name")
            assert result is not None, "Required property 'service_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def signing_region(self) -> builtins.str:
            '''``CfnTopicRule.SigV4AuthorizationProperty.SigningRegion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sigv4authorization.html#cfn-iot-topicrule-sigv4authorization-signingregion
            '''
            result = self._values.get("signing_region")
            assert result is not None, "Required property 'signing_region' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SigV4AuthorizationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.SnsActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "message_format": "messageFormat",
            "role_arn": "roleArn",
            "target_arn": "targetArn",
        },
    )
    class SnsActionProperty:
        def __init__(
            self,
            *,
            message_format: typing.Optional[builtins.str] = None,
            role_arn: builtins.str,
            target_arn: builtins.str,
        ) -> None:
            '''
            :param message_format: ``CfnTopicRule.SnsActionProperty.MessageFormat``.
            :param role_arn: ``CfnTopicRule.SnsActionProperty.RoleArn``.
            :param target_arn: ``CfnTopicRule.SnsActionProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                sns_action_property = iot.CfnTopicRule.SnsActionProperty(
                    role_arn="roleArn",
                    target_arn="targetArn",
                
                    # the properties below are optional
                    message_format="messageFormat"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "role_arn": role_arn,
                "target_arn": target_arn,
            }
            if message_format is not None:
                self._values["message_format"] = message_format

        @builtins.property
        def message_format(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.SnsActionProperty.MessageFormat``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-messageformat
            '''
            result = self._values.get("message_format")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.SnsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def target_arn(self) -> builtins.str:
            '''``CfnTopicRule.SnsActionProperty.TargetArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-snsaction.html#cfn-iot-topicrule-snsaction-targetarn
            '''
            result = self._values.get("target_arn")
            assert result is not None, "Required property 'target_arn' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SnsActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.SqsActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "queue_url": "queueUrl",
            "role_arn": "roleArn",
            "use_base64": "useBase64",
        },
    )
    class SqsActionProperty:
        def __init__(
            self,
            *,
            queue_url: builtins.str,
            role_arn: builtins.str,
            use_base64: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param queue_url: ``CfnTopicRule.SqsActionProperty.QueueUrl``.
            :param role_arn: ``CfnTopicRule.SqsActionProperty.RoleArn``.
            :param use_base64: ``CfnTopicRule.SqsActionProperty.UseBase64``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                sqs_action_property = iot.CfnTopicRule.SqsActionProperty(
                    queue_url="queueUrl",
                    role_arn="roleArn",
                
                    # the properties below are optional
                    use_base64=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "queue_url": queue_url,
                "role_arn": role_arn,
            }
            if use_base64 is not None:
                self._values["use_base64"] = use_base64

        @builtins.property
        def queue_url(self) -> builtins.str:
            '''``CfnTopicRule.SqsActionProperty.QueueUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-queueurl
            '''
            result = self._values.get("queue_url")
            assert result is not None, "Required property 'queue_url' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.SqsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def use_base64(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTopicRule.SqsActionProperty.UseBase64``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-sqsaction.html#cfn-iot-topicrule-sqsaction-usebase64
            '''
            result = self._values.get("use_base64")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SqsActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.StepFunctionsActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "execution_name_prefix": "executionNamePrefix",
            "role_arn": "roleArn",
            "state_machine_name": "stateMachineName",
        },
    )
    class StepFunctionsActionProperty:
        def __init__(
            self,
            *,
            execution_name_prefix: typing.Optional[builtins.str] = None,
            role_arn: builtins.str,
            state_machine_name: builtins.str,
        ) -> None:
            '''
            :param execution_name_prefix: ``CfnTopicRule.StepFunctionsActionProperty.ExecutionNamePrefix``.
            :param role_arn: ``CfnTopicRule.StepFunctionsActionProperty.RoleArn``.
            :param state_machine_name: ``CfnTopicRule.StepFunctionsActionProperty.StateMachineName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                step_functions_action_property = iot.CfnTopicRule.StepFunctionsActionProperty(
                    role_arn="roleArn",
                    state_machine_name="stateMachineName",
                
                    # the properties below are optional
                    execution_name_prefix="executionNamePrefix"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "role_arn": role_arn,
                "state_machine_name": state_machine_name,
            }
            if execution_name_prefix is not None:
                self._values["execution_name_prefix"] = execution_name_prefix

        @builtins.property
        def execution_name_prefix(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.StepFunctionsActionProperty.ExecutionNamePrefix``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-executionnameprefix
            '''
            result = self._values.get("execution_name_prefix")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.StepFunctionsActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def state_machine_name(self) -> builtins.str:
            '''``CfnTopicRule.StepFunctionsActionProperty.StateMachineName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-stepfunctionsaction.html#cfn-iot-topicrule-stepfunctionsaction-statemachinename
            '''
            result = self._values.get("state_machine_name")
            assert result is not None, "Required property 'state_machine_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StepFunctionsActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.TimestreamActionProperty",
        jsii_struct_bases=[],
        name_mapping={
            "batch_mode": "batchMode",
            "database_name": "databaseName",
            "dimensions": "dimensions",
            "role_arn": "roleArn",
            "table_name": "tableName",
            "timestamp": "timestamp",
        },
    )
    class TimestreamActionProperty:
        def __init__(
            self,
            *,
            batch_mode: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            database_name: builtins.str,
            dimensions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTopicRule.TimestreamDimensionProperty", _IResolvable_da3f097b]]],
            role_arn: builtins.str,
            table_name: builtins.str,
            timestamp: typing.Optional[typing.Union["CfnTopicRule.TimestreamTimestampProperty", _IResolvable_da3f097b]] = None,
        ) -> None:
            '''
            :param batch_mode: ``CfnTopicRule.TimestreamActionProperty.BatchMode``.
            :param database_name: ``CfnTopicRule.TimestreamActionProperty.DatabaseName``.
            :param dimensions: ``CfnTopicRule.TimestreamActionProperty.Dimensions``.
            :param role_arn: ``CfnTopicRule.TimestreamActionProperty.RoleArn``.
            :param table_name: ``CfnTopicRule.TimestreamActionProperty.TableName``.
            :param timestamp: ``CfnTopicRule.TimestreamActionProperty.Timestamp``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                timestream_action_property = iot.CfnTopicRule.TimestreamActionProperty(
                    database_name="databaseName",
                    dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                        name="name",
                        value="value"
                    )],
                    role_arn="roleArn",
                    table_name="tableName",
                
                    # the properties below are optional
                    batch_mode=False,
                    timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                        unit="unit",
                        value="value"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "database_name": database_name,
                "dimensions": dimensions,
                "role_arn": role_arn,
                "table_name": table_name,
            }
            if batch_mode is not None:
                self._values["batch_mode"] = batch_mode
            if timestamp is not None:
                self._values["timestamp"] = timestamp

        @builtins.property
        def batch_mode(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTopicRule.TimestreamActionProperty.BatchMode``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html#cfn-iot-topicrule-timestreamaction-batchmode
            '''
            result = self._values.get("batch_mode")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def database_name(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamActionProperty.DatabaseName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html#cfn-iot-topicrule-timestreamaction-databasename
            '''
            result = self._values.get("database_name")
            assert result is not None, "Required property 'database_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def dimensions(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.TimestreamDimensionProperty", _IResolvable_da3f097b]]]:
            '''``CfnTopicRule.TimestreamActionProperty.Dimensions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html#cfn-iot-topicrule-timestreamaction-dimensions
            '''
            result = self._values.get("dimensions")
            assert result is not None, "Required property 'dimensions' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.TimestreamDimensionProperty", _IResolvable_da3f097b]]], result)

        @builtins.property
        def role_arn(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamActionProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html#cfn-iot-topicrule-timestreamaction-rolearn
            '''
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def table_name(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamActionProperty.TableName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html#cfn-iot-topicrule-timestreamaction-tablename
            '''
            result = self._values.get("table_name")
            assert result is not None, "Required property 'table_name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def timestamp(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.TimestreamTimestampProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.TimestreamActionProperty.Timestamp``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamaction.html#cfn-iot-topicrule-timestreamaction-timestamp
            '''
            result = self._values.get("timestamp")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.TimestreamTimestampProperty", _IResolvable_da3f097b]], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TimestreamActionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.TimestreamDimensionProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "value": "value"},
    )
    class TimestreamDimensionProperty:
        def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
            '''
            :param name: ``CfnTopicRule.TimestreamDimensionProperty.Name``.
            :param value: ``CfnTopicRule.TimestreamDimensionProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamdimension.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                timestream_dimension_property = iot.CfnTopicRule.TimestreamDimensionProperty(
                    name="name",
                    value="value"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
                "value": value,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamDimensionProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamdimension.html#cfn-iot-topicrule-timestreamdimension-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamDimensionProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamdimension.html#cfn-iot-topicrule-timestreamdimension-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TimestreamDimensionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.TimestreamTimestampProperty",
        jsii_struct_bases=[],
        name_mapping={"unit": "unit", "value": "value"},
    )
    class TimestreamTimestampProperty:
        def __init__(self, *, unit: builtins.str, value: builtins.str) -> None:
            '''
            :param unit: ``CfnTopicRule.TimestreamTimestampProperty.Unit``.
            :param value: ``CfnTopicRule.TimestreamTimestampProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamtimestamp.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                timestream_timestamp_property = iot.CfnTopicRule.TimestreamTimestampProperty(
                    unit="unit",
                    value="value"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "unit": unit,
                "value": value,
            }

        @builtins.property
        def unit(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamTimestampProperty.Unit``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamtimestamp.html#cfn-iot-topicrule-timestreamtimestamp-unit
            '''
            result = self._values.get("unit")
            assert result is not None, "Required property 'unit' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def value(self) -> builtins.str:
            '''``CfnTopicRule.TimestreamTimestampProperty.Value``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-timestreamtimestamp.html#cfn-iot-topicrule-timestreamtimestamp-value
            '''
            result = self._values.get("value")
            assert result is not None, "Required property 'value' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TimestreamTimestampProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRule.TopicRulePayloadProperty",
        jsii_struct_bases=[],
        name_mapping={
            "actions": "actions",
            "aws_iot_sql_version": "awsIotSqlVersion",
            "description": "description",
            "error_action": "errorAction",
            "rule_disabled": "ruleDisabled",
            "sql": "sql",
        },
    )
    class TopicRulePayloadProperty:
        def __init__(
            self,
            *,
            actions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnTopicRule.ActionProperty", _IResolvable_da3f097b]]],
            aws_iot_sql_version: typing.Optional[builtins.str] = None,
            description: typing.Optional[builtins.str] = None,
            error_action: typing.Optional[typing.Union["CfnTopicRule.ActionProperty", _IResolvable_da3f097b]] = None,
            rule_disabled: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            sql: builtins.str,
        ) -> None:
            '''
            :param actions: ``CfnTopicRule.TopicRulePayloadProperty.Actions``.
            :param aws_iot_sql_version: ``CfnTopicRule.TopicRulePayloadProperty.AwsIotSqlVersion``.
            :param description: ``CfnTopicRule.TopicRulePayloadProperty.Description``.
            :param error_action: ``CfnTopicRule.TopicRulePayloadProperty.ErrorAction``.
            :param rule_disabled: ``CfnTopicRule.TopicRulePayloadProperty.RuleDisabled``.
            :param sql: ``CfnTopicRule.TopicRulePayloadProperty.Sql``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                topic_rule_payload_property = iot.CfnTopicRule.TopicRulePayloadProperty(
                    actions=[iot.CfnTopicRule.ActionProperty(
                        cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                            alarm_name="alarmName",
                            role_arn="roleArn",
                            state_reason="stateReason",
                            state_value="stateValue"
                        ),
                        cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                            log_group_name="logGroupName",
                            role_arn="roleArn"
                        ),
                        cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                            metric_name="metricName",
                            metric_namespace="metricNamespace",
                            metric_unit="metricUnit",
                            metric_value="metricValue",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            metric_timestamp="metricTimestamp"
                        ),
                        dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                            hash_key_field="hashKeyField",
                            hash_key_value="hashKeyValue",
                            role_arn="roleArn",
                            table_name="tableName",
                
                            # the properties below are optional
                            hash_key_type="hashKeyType",
                            payload_field="payloadField",
                            range_key_field="rangeKeyField",
                            range_key_type="rangeKeyType",
                            range_key_value="rangeKeyValue"
                        ),
                        dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                            put_item=iot.CfnTopicRule.PutItemInputProperty(
                                table_name="tableName"
                            ),
                            role_arn="roleArn"
                        ),
                        elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        firehose=iot.CfnTopicRule.FirehoseActionProperty(
                            delivery_stream_name="deliveryStreamName",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            batch_mode=False,
                            separator="separator"
                        ),
                        http=iot.CfnTopicRule.HttpActionProperty(
                            url="url",
                
                            # the properties below are optional
                            auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                                sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                    role_arn="roleArn",
                                    service_name="serviceName",
                                    signing_region="signingRegion"
                                )
                            ),
                            confirmation_url="confirmationUrl",
                            headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                                key="key",
                                value="value"
                            )]
                        ),
                        iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                            channel_name="channelName",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            batch_mode=False
                        ),
                        iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                            input_name="inputName",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            batch_mode=False,
                            message_id="messageId"
                        ),
                        iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                            put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                                property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                    timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
                
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    ),
                                    value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
                
                                    # the properties below are optional
                                    quality="quality"
                                )],
                
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            )],
                            role_arn="roleArn"
                        ),
                        kafka=iot.CfnTopicRule.KafkaActionProperty(
                            client_properties={
                                "client_properties_key": "clientProperties"
                            },
                            destination_arn="destinationArn",
                            topic="topic",
                
                            # the properties below are optional
                            key="key",
                            partition="partition"
                        ),
                        kinesis=iot.CfnTopicRule.KinesisActionProperty(
                            role_arn="roleArn",
                            stream_name="streamName",
                
                            # the properties below are optional
                            partition_key="partitionKey"
                        ),
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn="functionArn"
                        ),
                        open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        republish=iot.CfnTopicRule.RepublishActionProperty(
                            role_arn="roleArn",
                            topic="topic",
                
                            # the properties below are optional
                            qos=123
                        ),
                        s3=iot.CfnTopicRule.S3ActionProperty(
                            bucket_name="bucketName",
                            key="key",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            canned_acl="cannedAcl"
                        ),
                        sns=iot.CfnTopicRule.SnsActionProperty(
                            role_arn="roleArn",
                            target_arn="targetArn",
                
                            # the properties below are optional
                            message_format="messageFormat"
                        ),
                        sqs=iot.CfnTopicRule.SqsActionProperty(
                            queue_url="queueUrl",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            use_base64=False
                        ),
                        step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                            role_arn="roleArn",
                            state_machine_name="stateMachineName",
                
                            # the properties below are optional
                            execution_name_prefix="executionNamePrefix"
                        ),
                        timestream=iot.CfnTopicRule.TimestreamActionProperty(
                            database_name="databaseName",
                            dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                                name="name",
                                value="value"
                            )],
                            role_arn="roleArn",
                            table_name="tableName",
                
                            # the properties below are optional
                            batch_mode=False,
                            timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                                unit="unit",
                                value="value"
                            )
                        )
                    )],
                    sql="sql",
                
                    # the properties below are optional
                    aws_iot_sql_version="awsIotSqlVersion",
                    description="description",
                    error_action=iot.CfnTopicRule.ActionProperty(
                        cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                            alarm_name="alarmName",
                            role_arn="roleArn",
                            state_reason="stateReason",
                            state_value="stateValue"
                        ),
                        cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                            log_group_name="logGroupName",
                            role_arn="roleArn"
                        ),
                        cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                            metric_name="metricName",
                            metric_namespace="metricNamespace",
                            metric_unit="metricUnit",
                            metric_value="metricValue",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            metric_timestamp="metricTimestamp"
                        ),
                        dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                            hash_key_field="hashKeyField",
                            hash_key_value="hashKeyValue",
                            role_arn="roleArn",
                            table_name="tableName",
                
                            # the properties below are optional
                            hash_key_type="hashKeyType",
                            payload_field="payloadField",
                            range_key_field="rangeKeyField",
                            range_key_type="rangeKeyType",
                            range_key_value="rangeKeyValue"
                        ),
                        dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                            put_item=iot.CfnTopicRule.PutItemInputProperty(
                                table_name="tableName"
                            ),
                            role_arn="roleArn"
                        ),
                        elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        firehose=iot.CfnTopicRule.FirehoseActionProperty(
                            delivery_stream_name="deliveryStreamName",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            batch_mode=False,
                            separator="separator"
                        ),
                        http=iot.CfnTopicRule.HttpActionProperty(
                            url="url",
                
                            # the properties below are optional
                            auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                                sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                    role_arn="roleArn",
                                    service_name="serviceName",
                                    signing_region="signingRegion"
                                )
                            ),
                            confirmation_url="confirmationUrl",
                            headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                                key="key",
                                value="value"
                            )]
                        ),
                        iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                            channel_name="channelName",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            batch_mode=False
                        ),
                        iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                            input_name="inputName",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            batch_mode=False,
                            message_id="messageId"
                        ),
                        iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                            put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                                property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                    timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
                
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    ),
                                    value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
                
                                    # the properties below are optional
                                    quality="quality"
                                )],
                
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            )],
                            role_arn="roleArn"
                        ),
                        kafka=iot.CfnTopicRule.KafkaActionProperty(
                            client_properties={
                                "client_properties_key": "clientProperties"
                            },
                            destination_arn="destinationArn",
                            topic="topic",
                
                            # the properties below are optional
                            key="key",
                            partition="partition"
                        ),
                        kinesis=iot.CfnTopicRule.KinesisActionProperty(
                            role_arn="roleArn",
                            stream_name="streamName",
                
                            # the properties below are optional
                            partition_key="partitionKey"
                        ),
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn="functionArn"
                        ),
                        open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        republish=iot.CfnTopicRule.RepublishActionProperty(
                            role_arn="roleArn",
                            topic="topic",
                
                            # the properties below are optional
                            qos=123
                        ),
                        s3=iot.CfnTopicRule.S3ActionProperty(
                            bucket_name="bucketName",
                            key="key",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            canned_acl="cannedAcl"
                        ),
                        sns=iot.CfnTopicRule.SnsActionProperty(
                            role_arn="roleArn",
                            target_arn="targetArn",
                
                            # the properties below are optional
                            message_format="messageFormat"
                        ),
                        sqs=iot.CfnTopicRule.SqsActionProperty(
                            queue_url="queueUrl",
                            role_arn="roleArn",
                
                            # the properties below are optional
                            use_base64=False
                        ),
                        step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                            role_arn="roleArn",
                            state_machine_name="stateMachineName",
                
                            # the properties below are optional
                            execution_name_prefix="executionNamePrefix"
                        ),
                        timestream=iot.CfnTopicRule.TimestreamActionProperty(
                            database_name="databaseName",
                            dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                                name="name",
                                value="value"
                            )],
                            role_arn="roleArn",
                            table_name="tableName",
                
                            # the properties below are optional
                            batch_mode=False,
                            timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                                unit="unit",
                                value="value"
                            )
                        )
                    ),
                    rule_disabled=False
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "actions": actions,
                "sql": sql,
            }
            if aws_iot_sql_version is not None:
                self._values["aws_iot_sql_version"] = aws_iot_sql_version
            if description is not None:
                self._values["description"] = description
            if error_action is not None:
                self._values["error_action"] = error_action
            if rule_disabled is not None:
                self._values["rule_disabled"] = rule_disabled

        @builtins.property
        def actions(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.ActionProperty", _IResolvable_da3f097b]]]:
            '''``CfnTopicRule.TopicRulePayloadProperty.Actions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-actions
            '''
            result = self._values.get("actions")
            assert result is not None, "Required property 'actions' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnTopicRule.ActionProperty", _IResolvable_da3f097b]]], result)

        @builtins.property
        def aws_iot_sql_version(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.TopicRulePayloadProperty.AwsIotSqlVersion``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-awsiotsqlversion
            '''
            result = self._values.get("aws_iot_sql_version")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRule.TopicRulePayloadProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def error_action(
            self,
        ) -> typing.Optional[typing.Union["CfnTopicRule.ActionProperty", _IResolvable_da3f097b]]:
            '''``CfnTopicRule.TopicRulePayloadProperty.ErrorAction``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-erroraction
            '''
            result = self._values.get("error_action")
            return typing.cast(typing.Optional[typing.Union["CfnTopicRule.ActionProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def rule_disabled(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnTopicRule.TopicRulePayloadProperty.RuleDisabled``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-ruledisabled
            '''
            result = self._values.get("rule_disabled")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def sql(self) -> builtins.str:
            '''``CfnTopicRule.TopicRulePayloadProperty.Sql``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicrule-topicrulepayload.html#cfn-iot-topicrule-topicrulepayload-sql
            '''
            result = self._values.get("sql")
            assert result is not None, "Required property 'sql' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "TopicRulePayloadProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.implements(_IInspectable_c2943556)
class CfnTopicRuleDestination(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_iot.CfnTopicRuleDestination",
):
    '''A CloudFormation ``AWS::IoT::TopicRuleDestination``.

    :cloudformationResource: AWS::IoT::TopicRuleDestination
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_iot as iot
        
        cfn_topic_rule_destination = iot.CfnTopicRuleDestination(self, "MyCfnTopicRuleDestination",
            http_url_properties=iot.CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty(
                confirmation_url="confirmationUrl"
            ),
            status="status",
            vpc_properties=iot.CfnTopicRuleDestination.VpcDestinationPropertiesProperty(
                role_arn="roleArn",
                security_groups=["securityGroups"],
                subnet_ids=["subnetIds"],
                vpc_id="vpcId"
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        http_url_properties: typing.Optional[typing.Union["CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty", _IResolvable_da3f097b]] = None,
        status: typing.Optional[builtins.str] = None,
        vpc_properties: typing.Optional[typing.Union["CfnTopicRuleDestination.VpcDestinationPropertiesProperty", _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Create a new ``AWS::IoT::TopicRuleDestination``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param http_url_properties: ``AWS::IoT::TopicRuleDestination.HttpUrlProperties``.
        :param status: ``AWS::IoT::TopicRuleDestination.Status``.
        :param vpc_properties: ``AWS::IoT::TopicRuleDestination.VpcProperties``.
        '''
        props = CfnTopicRuleDestinationProps(
            http_url_properties=http_url_properties,
            status=status,
            vpc_properties=vpc_properties,
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
    @jsii.member(jsii_name="attrStatusReason")
    def attr_status_reason(self) -> builtins.str:
        '''
        :cloudformationAttribute: StatusReason
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrStatusReason"))

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
    @jsii.member(jsii_name="httpUrlProperties")
    def http_url_properties(
        self,
    ) -> typing.Optional[typing.Union["CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::TopicRuleDestination.HttpUrlProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html#cfn-iot-topicruledestination-httpurlproperties
        '''
        return typing.cast(typing.Optional[typing.Union["CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty", _IResolvable_da3f097b]], jsii.get(self, "httpUrlProperties"))

    @http_url_properties.setter
    def http_url_properties(
        self,
        value: typing.Optional[typing.Union["CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "httpUrlProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::TopicRuleDestination.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html#cfn-iot-topicruledestination-status
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @status.setter
    def status(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcProperties")
    def vpc_properties(
        self,
    ) -> typing.Optional[typing.Union["CfnTopicRuleDestination.VpcDestinationPropertiesProperty", _IResolvable_da3f097b]]:
        '''``AWS::IoT::TopicRuleDestination.VpcProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html#cfn-iot-topicruledestination-vpcproperties
        '''
        return typing.cast(typing.Optional[typing.Union["CfnTopicRuleDestination.VpcDestinationPropertiesProperty", _IResolvable_da3f097b]], jsii.get(self, "vpcProperties"))

    @vpc_properties.setter
    def vpc_properties(
        self,
        value: typing.Optional[typing.Union["CfnTopicRuleDestination.VpcDestinationPropertiesProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "vpcProperties", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty",
        jsii_struct_bases=[],
        name_mapping={"confirmation_url": "confirmationUrl"},
    )
    class HttpUrlDestinationSummaryProperty:
        def __init__(
            self,
            *,
            confirmation_url: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param confirmation_url: ``CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty.ConfirmationUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-httpurldestinationsummary.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                http_url_destination_summary_property = iot.CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty(
                    confirmation_url="confirmationUrl"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if confirmation_url is not None:
                self._values["confirmation_url"] = confirmation_url

        @builtins.property
        def confirmation_url(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty.ConfirmationUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-httpurldestinationsummary.html#cfn-iot-topicruledestination-httpurldestinationsummary-confirmationurl
            '''
            result = self._values.get("confirmation_url")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "HttpUrlDestinationSummaryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_iot.CfnTopicRuleDestination.VpcDestinationPropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "role_arn": "roleArn",
            "security_groups": "securityGroups",
            "subnet_ids": "subnetIds",
            "vpc_id": "vpcId",
        },
    )
    class VpcDestinationPropertiesProperty:
        def __init__(
            self,
            *,
            role_arn: typing.Optional[builtins.str] = None,
            security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
            subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
            vpc_id: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param role_arn: ``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.RoleArn``.
            :param security_groups: ``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.SecurityGroups``.
            :param subnet_ids: ``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.SubnetIds``.
            :param vpc_id: ``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.VpcId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-vpcdestinationproperties.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_iot as iot
                
                vpc_destination_properties_property = iot.CfnTopicRuleDestination.VpcDestinationPropertiesProperty(
                    role_arn="roleArn",
                    security_groups=["securityGroups"],
                    subnet_ids=["subnetIds"],
                    vpc_id="vpcId"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if role_arn is not None:
                self._values["role_arn"] = role_arn
            if security_groups is not None:
                self._values["security_groups"] = security_groups
            if subnet_ids is not None:
                self._values["subnet_ids"] = subnet_ids
            if vpc_id is not None:
                self._values["vpc_id"] = vpc_id

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-vpcdestinationproperties.html#cfn-iot-topicruledestination-vpcdestinationproperties-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.SecurityGroups``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-vpcdestinationproperties.html#cfn-iot-topicruledestination-vpcdestinationproperties-securitygroups
            '''
            result = self._values.get("security_groups")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def subnet_ids(self) -> typing.Optional[typing.List[builtins.str]]:
            '''``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.SubnetIds``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-vpcdestinationproperties.html#cfn-iot-topicruledestination-vpcdestinationproperties-subnetids
            '''
            result = self._values.get("subnet_ids")
            return typing.cast(typing.Optional[typing.List[builtins.str]], result)

        @builtins.property
        def vpc_id(self) -> typing.Optional[builtins.str]:
            '''``CfnTopicRuleDestination.VpcDestinationPropertiesProperty.VpcId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-iot-topicruledestination-vpcdestinationproperties.html#cfn-iot-topicruledestination-vpcdestinationproperties-vpcid
            '''
            result = self._values.get("vpc_id")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "VpcDestinationPropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnTopicRuleDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "http_url_properties": "httpUrlProperties",
        "status": "status",
        "vpc_properties": "vpcProperties",
    },
)
class CfnTopicRuleDestinationProps:
    def __init__(
        self,
        *,
        http_url_properties: typing.Optional[typing.Union[CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty, _IResolvable_da3f097b]] = None,
        status: typing.Optional[builtins.str] = None,
        vpc_properties: typing.Optional[typing.Union[CfnTopicRuleDestination.VpcDestinationPropertiesProperty, _IResolvable_da3f097b]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::IoT::TopicRuleDestination``.

        :param http_url_properties: ``AWS::IoT::TopicRuleDestination.HttpUrlProperties``.
        :param status: ``AWS::IoT::TopicRuleDestination.Status``.
        :param vpc_properties: ``AWS::IoT::TopicRuleDestination.VpcProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_topic_rule_destination_props = iot.CfnTopicRuleDestinationProps(
                http_url_properties=iot.CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty(
                    confirmation_url="confirmationUrl"
                ),
                status="status",
                vpc_properties=iot.CfnTopicRuleDestination.VpcDestinationPropertiesProperty(
                    role_arn="roleArn",
                    security_groups=["securityGroups"],
                    subnet_ids=["subnetIds"],
                    vpc_id="vpcId"
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if http_url_properties is not None:
            self._values["http_url_properties"] = http_url_properties
        if status is not None:
            self._values["status"] = status
        if vpc_properties is not None:
            self._values["vpc_properties"] = vpc_properties

    @builtins.property
    def http_url_properties(
        self,
    ) -> typing.Optional[typing.Union[CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::TopicRuleDestination.HttpUrlProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html#cfn-iot-topicruledestination-httpurlproperties
        '''
        result = self._values.get("http_url_properties")
        return typing.cast(typing.Optional[typing.Union[CfnTopicRuleDestination.HttpUrlDestinationSummaryProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::TopicRuleDestination.Status``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html#cfn-iot-topicruledestination-status
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_properties(
        self,
    ) -> typing.Optional[typing.Union[CfnTopicRuleDestination.VpcDestinationPropertiesProperty, _IResolvable_da3f097b]]:
        '''``AWS::IoT::TopicRuleDestination.VpcProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicruledestination.html#cfn-iot-topicruledestination-vpcproperties
        '''
        result = self._values.get("vpc_properties")
        return typing.cast(typing.Optional[typing.Union[CfnTopicRuleDestination.VpcDestinationPropertiesProperty, _IResolvable_da3f097b]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnTopicRuleDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_iot.CfnTopicRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "rule_name": "ruleName",
        "tags": "tags",
        "topic_rule_payload": "topicRulePayload",
    },
)
class CfnTopicRuleProps:
    def __init__(
        self,
        *,
        rule_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        topic_rule_payload: typing.Union[CfnTopicRule.TopicRulePayloadProperty, _IResolvable_da3f097b],
    ) -> None:
        '''Properties for defining a ``AWS::IoT::TopicRule``.

        :param rule_name: ``AWS::IoT::TopicRule.RuleName``.
        :param tags: ``AWS::IoT::TopicRule.Tags``.
        :param topic_rule_payload: ``AWS::IoT::TopicRule.TopicRulePayload``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_iot as iot
            
            cfn_topic_rule_props = iot.CfnTopicRuleProps(
                topic_rule_payload=iot.CfnTopicRule.TopicRulePayloadProperty(
                    actions=[iot.CfnTopicRule.ActionProperty(
                        cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                            alarm_name="alarmName",
                            role_arn="roleArn",
                            state_reason="stateReason",
                            state_value="stateValue"
                        ),
                        cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                            log_group_name="logGroupName",
                            role_arn="roleArn"
                        ),
                        cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                            metric_name="metricName",
                            metric_namespace="metricNamespace",
                            metric_unit="metricUnit",
                            metric_value="metricValue",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            metric_timestamp="metricTimestamp"
                        ),
                        dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                            hash_key_field="hashKeyField",
                            hash_key_value="hashKeyValue",
                            role_arn="roleArn",
                            table_name="tableName",
            
                            # the properties below are optional
                            hash_key_type="hashKeyType",
                            payload_field="payloadField",
                            range_key_field="rangeKeyField",
                            range_key_type="rangeKeyType",
                            range_key_value="rangeKeyValue"
                        ),
                        dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                            put_item=iot.CfnTopicRule.PutItemInputProperty(
                                table_name="tableName"
                            ),
                            role_arn="roleArn"
                        ),
                        elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        firehose=iot.CfnTopicRule.FirehoseActionProperty(
                            delivery_stream_name="deliveryStreamName",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            batch_mode=False,
                            separator="separator"
                        ),
                        http=iot.CfnTopicRule.HttpActionProperty(
                            url="url",
            
                            # the properties below are optional
                            auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                                sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                    role_arn="roleArn",
                                    service_name="serviceName",
                                    signing_region="signingRegion"
                                )
                            ),
                            confirmation_url="confirmationUrl",
                            headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                                key="key",
                                value="value"
                            )]
                        ),
                        iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                            channel_name="channelName",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            batch_mode=False
                        ),
                        iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                            input_name="inputName",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            batch_mode=False,
                            message_id="messageId"
                        ),
                        iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                            put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                                property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                    timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
            
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    ),
                                    value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
            
                                    # the properties below are optional
                                    quality="quality"
                                )],
            
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            )],
                            role_arn="roleArn"
                        ),
                        kafka=iot.CfnTopicRule.KafkaActionProperty(
                            client_properties={
                                "client_properties_key": "clientProperties"
                            },
                            destination_arn="destinationArn",
                            topic="topic",
            
                            # the properties below are optional
                            key="key",
                            partition="partition"
                        ),
                        kinesis=iot.CfnTopicRule.KinesisActionProperty(
                            role_arn="roleArn",
                            stream_name="streamName",
            
                            # the properties below are optional
                            partition_key="partitionKey"
                        ),
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn="functionArn"
                        ),
                        open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        republish=iot.CfnTopicRule.RepublishActionProperty(
                            role_arn="roleArn",
                            topic="topic",
            
                            # the properties below are optional
                            qos=123
                        ),
                        s3=iot.CfnTopicRule.S3ActionProperty(
                            bucket_name="bucketName",
                            key="key",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            canned_acl="cannedAcl"
                        ),
                        sns=iot.CfnTopicRule.SnsActionProperty(
                            role_arn="roleArn",
                            target_arn="targetArn",
            
                            # the properties below are optional
                            message_format="messageFormat"
                        ),
                        sqs=iot.CfnTopicRule.SqsActionProperty(
                            queue_url="queueUrl",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            use_base64=False
                        ),
                        step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                            role_arn="roleArn",
                            state_machine_name="stateMachineName",
            
                            # the properties below are optional
                            execution_name_prefix="executionNamePrefix"
                        ),
                        timestream=iot.CfnTopicRule.TimestreamActionProperty(
                            database_name="databaseName",
                            dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                                name="name",
                                value="value"
                            )],
                            role_arn="roleArn",
                            table_name="tableName",
            
                            # the properties below are optional
                            batch_mode=False,
                            timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                                unit="unit",
                                value="value"
                            )
                        )
                    )],
                    sql="sql",
            
                    # the properties below are optional
                    aws_iot_sql_version="awsIotSqlVersion",
                    description="description",
                    error_action=iot.CfnTopicRule.ActionProperty(
                        cloudwatch_alarm=iot.CfnTopicRule.CloudwatchAlarmActionProperty(
                            alarm_name="alarmName",
                            role_arn="roleArn",
                            state_reason="stateReason",
                            state_value="stateValue"
                        ),
                        cloudwatch_logs=iot.CfnTopicRule.CloudwatchLogsActionProperty(
                            log_group_name="logGroupName",
                            role_arn="roleArn"
                        ),
                        cloudwatch_metric=iot.CfnTopicRule.CloudwatchMetricActionProperty(
                            metric_name="metricName",
                            metric_namespace="metricNamespace",
                            metric_unit="metricUnit",
                            metric_value="metricValue",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            metric_timestamp="metricTimestamp"
                        ),
                        dynamo_db=iot.CfnTopicRule.DynamoDBActionProperty(
                            hash_key_field="hashKeyField",
                            hash_key_value="hashKeyValue",
                            role_arn="roleArn",
                            table_name="tableName",
            
                            # the properties below are optional
                            hash_key_type="hashKeyType",
                            payload_field="payloadField",
                            range_key_field="rangeKeyField",
                            range_key_type="rangeKeyType",
                            range_key_value="rangeKeyValue"
                        ),
                        dynamo_dBv2=iot.CfnTopicRule.DynamoDBv2ActionProperty(
                            put_item=iot.CfnTopicRule.PutItemInputProperty(
                                table_name="tableName"
                            ),
                            role_arn="roleArn"
                        ),
                        elasticsearch=iot.CfnTopicRule.ElasticsearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        firehose=iot.CfnTopicRule.FirehoseActionProperty(
                            delivery_stream_name="deliveryStreamName",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            batch_mode=False,
                            separator="separator"
                        ),
                        http=iot.CfnTopicRule.HttpActionProperty(
                            url="url",
            
                            # the properties below are optional
                            auth=iot.CfnTopicRule.HttpAuthorizationProperty(
                                sigv4=iot.CfnTopicRule.SigV4AuthorizationProperty(
                                    role_arn="roleArn",
                                    service_name="serviceName",
                                    signing_region="signingRegion"
                                )
                            ),
                            confirmation_url="confirmationUrl",
                            headers=[iot.CfnTopicRule.HttpActionHeaderProperty(
                                key="key",
                                value="value"
                            )]
                        ),
                        iot_analytics=iot.CfnTopicRule.IotAnalyticsActionProperty(
                            channel_name="channelName",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            batch_mode=False
                        ),
                        iot_events=iot.CfnTopicRule.IotEventsActionProperty(
                            input_name="inputName",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            batch_mode=False,
                            message_id="messageId"
                        ),
                        iot_site_wise=iot.CfnTopicRule.IotSiteWiseActionProperty(
                            put_asset_property_value_entries=[iot.CfnTopicRule.PutAssetPropertyValueEntryProperty(
                                property_values=[iot.CfnTopicRule.AssetPropertyValueProperty(
                                    timestamp=iot.CfnTopicRule.AssetPropertyTimestampProperty(
                                        time_in_seconds="timeInSeconds",
            
                                        # the properties below are optional
                                        offset_in_nanos="offsetInNanos"
                                    ),
                                    value=iot.CfnTopicRule.AssetPropertyVariantProperty(
                                        boolean_value="booleanValue",
                                        double_value="doubleValue",
                                        integer_value="integerValue",
                                        string_value="stringValue"
                                    ),
            
                                    # the properties below are optional
                                    quality="quality"
                                )],
            
                                # the properties below are optional
                                asset_id="assetId",
                                entry_id="entryId",
                                property_alias="propertyAlias",
                                property_id="propertyId"
                            )],
                            role_arn="roleArn"
                        ),
                        kafka=iot.CfnTopicRule.KafkaActionProperty(
                            client_properties={
                                "client_properties_key": "clientProperties"
                            },
                            destination_arn="destinationArn",
                            topic="topic",
            
                            # the properties below are optional
                            key="key",
                            partition="partition"
                        ),
                        kinesis=iot.CfnTopicRule.KinesisActionProperty(
                            role_arn="roleArn",
                            stream_name="streamName",
            
                            # the properties below are optional
                            partition_key="partitionKey"
                        ),
                        lambda_=iot.CfnTopicRule.LambdaActionProperty(
                            function_arn="functionArn"
                        ),
                        open_search=iot.CfnTopicRule.OpenSearchActionProperty(
                            endpoint="endpoint",
                            id="id",
                            index="index",
                            role_arn="roleArn",
                            type="type"
                        ),
                        republish=iot.CfnTopicRule.RepublishActionProperty(
                            role_arn="roleArn",
                            topic="topic",
            
                            # the properties below are optional
                            qos=123
                        ),
                        s3=iot.CfnTopicRule.S3ActionProperty(
                            bucket_name="bucketName",
                            key="key",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            canned_acl="cannedAcl"
                        ),
                        sns=iot.CfnTopicRule.SnsActionProperty(
                            role_arn="roleArn",
                            target_arn="targetArn",
            
                            # the properties below are optional
                            message_format="messageFormat"
                        ),
                        sqs=iot.CfnTopicRule.SqsActionProperty(
                            queue_url="queueUrl",
                            role_arn="roleArn",
            
                            # the properties below are optional
                            use_base64=False
                        ),
                        step_functions=iot.CfnTopicRule.StepFunctionsActionProperty(
                            role_arn="roleArn",
                            state_machine_name="stateMachineName",
            
                            # the properties below are optional
                            execution_name_prefix="executionNamePrefix"
                        ),
                        timestream=iot.CfnTopicRule.TimestreamActionProperty(
                            database_name="databaseName",
                            dimensions=[iot.CfnTopicRule.TimestreamDimensionProperty(
                                name="name",
                                value="value"
                            )],
                            role_arn="roleArn",
                            table_name="tableName",
            
                            # the properties below are optional
                            batch_mode=False,
                            timestamp=iot.CfnTopicRule.TimestreamTimestampProperty(
                                unit="unit",
                                value="value"
                            )
                        )
                    ),
                    rule_disabled=False
                ),
            
                # the properties below are optional
                rule_name="ruleName",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "topic_rule_payload": topic_rule_payload,
        }
        if rule_name is not None:
            self._values["rule_name"] = rule_name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def rule_name(self) -> typing.Optional[builtins.str]:
        '''``AWS::IoT::TopicRule.RuleName``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-rulename
        '''
        result = self._values.get("rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::IoT::TopicRule.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def topic_rule_payload(
        self,
    ) -> typing.Union[CfnTopicRule.TopicRulePayloadProperty, _IResolvable_da3f097b]:
        '''``AWS::IoT::TopicRule.TopicRulePayload``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iot-topicrule.html#cfn-iot-topicrule-topicrulepayload
        '''
        result = self._values.get("topic_rule_payload")
        assert result is not None, "Required property 'topic_rule_payload' is missing"
        return typing.cast(typing.Union[CfnTopicRule.TopicRulePayloadProperty, _IResolvable_da3f097b], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnTopicRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnAccountAuditConfiguration",
    "CfnAccountAuditConfigurationProps",
    "CfnAuthorizer",
    "CfnAuthorizerProps",
    "CfnCertificate",
    "CfnCertificateProps",
    "CfnCustomMetric",
    "CfnCustomMetricProps",
    "CfnDimension",
    "CfnDimensionProps",
    "CfnDomainConfiguration",
    "CfnDomainConfigurationProps",
    "CfnFleetMetric",
    "CfnFleetMetricProps",
    "CfnJobTemplate",
    "CfnJobTemplateProps",
    "CfnLogging",
    "CfnLoggingProps",
    "CfnMitigationAction",
    "CfnMitigationActionProps",
    "CfnPolicy",
    "CfnPolicyPrincipalAttachment",
    "CfnPolicyPrincipalAttachmentProps",
    "CfnPolicyProps",
    "CfnProvisioningTemplate",
    "CfnProvisioningTemplateProps",
    "CfnResourceSpecificLogging",
    "CfnResourceSpecificLoggingProps",
    "CfnScheduledAudit",
    "CfnScheduledAuditProps",
    "CfnSecurityProfile",
    "CfnSecurityProfileProps",
    "CfnThing",
    "CfnThingPrincipalAttachment",
    "CfnThingPrincipalAttachmentProps",
    "CfnThingProps",
    "CfnTopicRule",
    "CfnTopicRuleDestination",
    "CfnTopicRuleDestinationProps",
    "CfnTopicRuleProps",
]

publication.publish()
