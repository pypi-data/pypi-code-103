'''
[![NPM version](https://badge.fury.io/js/@ikala-cloud%2Faws-waf-solution.svg)](https://badge.fury.io/js/@ikala-cloud%2Faws-waf-solution)
[![PyPI version](https://badge.fury.io/py/ikala-cloud.aws-waf-solution.svg)](https://badge.fury.io/py/ikala-cloud.aws-waf-solution)
[![release](https://github.com/iKala-Cloud/aws-waf-solution/actions/workflows/release.yml/badge.svg)](https://github.com/iKala-Cloud/aws-waf-solution/actions/workflows/release.yml)

# AWS WAF Solution

This CDK Construct modify and rebuild from [Cloudfront with Automated WAF](https://github.com/awslabs/aws-cloudfront-extensions/tree/main/templates/aws-cloudfront-waf).

The solution use CDK construct to automatically deploy a set of AWS WAF rules design to filter common web-based attacks.Users can select from preconfigured protective features that define the rules included in an AWS WAF web access control list (web ACL). After the solution deploys, AWS WAF begins inspecting web requests to the user’s existing Amazon CloudFront distributions、Application Load Balancers、API Gateway, and blocks them when applicable.

## What is difference

* The project is CDK Construct which is handy to integrate into your existing CDK project.
* Support count mode for testing WAF rule, see [API.md](https://github.com/iKala-Cloud/aws-waf-solution/blob/main/API.md#countmodeoptional-).
* Support Application Load Balancers and API Gateway (The origin repository doesn't support ALB any more in next release, see [issue](https://github.com/awslabs/aws-cloudfront-extensions/issues/164) )
* AWS Shield Advance is optional (The origin repository enforce to enable it)

## Construct Props

Ref [API Reference](API.md)

## CloudFront Usage

```python
# Example automatically generated from non-compiling source. May contain errors.
env_uSEast1 = {
    "region": "us-east-1",
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

stack_test1 = cdk.Stack(app, "TestStackAutomatedWafForCloudFront", env=env_uSEast1)

AutomatedWaf(stack_test1, "AutomatedWaf",
    waf2_scope=Waf2ScopeOption.CLOUDFRONT,
    resource_naming_prefix="CloudFront_ApiGW",
    error_threshold=55,
    request_threshold=300,
    block_period=60,
    log_level=LogLevel.DEBUG
)
```

Notice the WAF region must be `us-east-1` for CloudFront.

After deploying, it need to do two things on AWS Management Console.

***1. Attach Cloudfront to WAF.***

Click `add AWS Resources`

![CloudFront-3](https://user-images.githubusercontent.com/7465652/136758293-bd1b7d86-2775-456f-a176-ff508fb91fd1.jpg)

Select existing CloudFront Distribution.

![CloudFront-4](https://user-images.githubusercontent.com/7465652/136758304-582141ab-6bb7-4aa5-b236-4b656ef53e1f.jpg)

***2. Set S3 bucket on CloudFront standand logging***

Find S3 bucket name on CloudFormation output

![CloudFront-1](https://user-images.githubusercontent.com/7465652/136758257-9dd42b8d-163e-4775-aba4-da33358d9497.jpg)

Set CloudFront standard logging on CloudFront Settings

![CloudFront-2](https://user-images.githubusercontent.com/7465652/136758273-95ae32c3-091a-4bef-a9de-57406ceee3b6.jpg)

:warning: Log Prefix must be `AWSLogs/`

## Application Load Balancers Usage

```python
# Example automatically generated from non-compiling source. May contain errors.
env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

stack_test2 = cdk.Stack(app, "TestStackAutomatedWafForALB", env=env)

alb_arn = f"arn:aws:elasticloadbalancing:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:loadbalancer/app/ApiNe-Alb16-2VIC9075YQEZ/db92cdc88d2e7c9d"

AutomatedWaf(stack_test2, "AutomatedWaf",
    waf2_scope=Waf2ScopeOption.REGIONAL,
    associated_resource_arn=alb_arn,
    resource_naming_prefix="Alb_Api",
    error_threshold=50,
    request_threshold=300,
    block_period=60,
    log_level=LogLevel.DEBUG
)
```

After deploying, follow these steps on AWS Management Console. See below:

Find S3 bucket name on CloudFormation output

![CloudFront-1](https://user-images.githubusercontent.com/7465652/136758257-9dd42b8d-163e-4775-aba4-da33358d9497.jpg)

Click `Edit Attributes` on Basic Configuration of Load Balancers

![ALB-1](https://user-images.githubusercontent.com/7465652/136764403-4a02a436-c799-4cb4-85b9-c221696a1f9e.jpg)

Enable Access logs and input S3 bucket

![ALB-2](https://user-images.githubusercontent.com/7465652/136764407-985d48ed-323c-4aad-b210-72ae09648845.jpg)

## API Gateway Usage

```python
# Example automatically generated from non-compiling source. May contain errors.
env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

stack_test3 = cdk.Stack(app, "TestStackAutomatedWafForApiGW", env=env)

#
# Ref Stage arn in https://docs.aws.amazon.com/apigateway/latest/developerguide/arn-format-reference.html
#
rest_api_arn = f"arn:aws:apigateway:{cdk.Aws.REGION}::/restapis/0j90w09yf9/stages/prod"

AutomatedWaf(stack_test3, "AutomatedWaf",
    waf2_scope=Waf2ScopeOption.REGIONAL,
    associated_resource_arn=rest_api_arn,
    resource_naming_prefix="ApiGW",
    error_threshold=50,
    request_threshold=300,
    block_period=60,
    log_level=LogLevel.DEBUG
)
```

## Troubleshooting

If deployment error, the cloudFormation Error event like this

```
Received response status [FAILED] from custom resource. Message returned: 'HttpFloodLambdaLogParser' (RequestId: b4e08ea2-fe0a-46f8-98aa-6f96d4558579)
```

If any custom resource deploy error like above, delete the stack and redeploy it that will pass.
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

import aws_cdk.core


class AutomatedWaf(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@ikala-cloud/aws-waf-solution.AutomatedWaf",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        waf2_scope: "Waf2ScopeOption",
        app_access_log_bucket_name: typing.Optional[builtins.str] = None,
        associated_resource_arn: typing.Optional[builtins.str] = None,
        block_period: typing.Optional[jsii.Number] = None,
        count_mode: typing.Optional[builtins.bool] = None,
        enable_shield_advanced_lambda: typing.Optional[builtins.bool] = None,
        error_threshold: typing.Optional[jsii.Number] = None,
        log_level: typing.Optional["LogLevel"] = None,
        request_threshold: typing.Optional[jsii.Number] = None,
        resource_naming_prefix: typing.Optional[builtins.str] = None,
        waf_log_bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param waf2_scope: (experimental) CLOUDFRONT or REGIONAL. If use REGIONAL, it support ALB、API Gateway
        :param app_access_log_bucket_name: 
        :param associated_resource_arn: (experimental) Only support ALB arn or API Gateway arn when waf2Scope is Regional. This property doesn't support CloudFront arn because it is restricted by CloudFormation ``AWS::WAFv2::WebACLAssociation`` , see more details: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafv2-webaclassociation.html#cfn-wafv2-webaclassociation-resourcearndetails:
        :param block_period: (experimental) The period (in minutes) to block applicable IP addresses.
        :param count_mode: (experimental) Test your WAF rules, see more details: `AWS WAF rule action <https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-action.html>`_. Default is false
        :param enable_shield_advanced_lambda: (experimental) Enable or disable AWS Shield Advance (:warning: it need `$3000 Monthly Fee <https://aws.amazon.com/shield/pricing/?nc1=h_ls>`_). Default is false
        :param error_threshold: (experimental) The maximum acceptable bad requests per minute per IP. :warning: The property map WAF ``Scanners and Probes`` Rule which support only CloudFront and ALB. Default is 200
        :param log_level: (experimental) Valid value is 'INFO', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
        :param request_threshold: (experimental) The maximum acceptable requests per FIVE-minute period per IP address. Default is 1000
        :param resource_naming_prefix: (experimental) If the construct need to deploy more than one times, specify the property to prevent AWS resource name conflict. (The property only allow alphanumeric and "_" symbol because glue database naming is needed)
        :param waf_log_bucket_name: 

        :stability: experimental
        '''
        props = AutomatedWafProps(
            waf2_scope=waf2_scope,
            app_access_log_bucket_name=app_access_log_bucket_name,
            associated_resource_arn=associated_resource_arn,
            block_period=block_period,
            count_mode=count_mode,
            enable_shield_advanced_lambda=enable_shield_advanced_lambda,
            error_threshold=error_threshold,
            log_level=log_level,
            request_threshold=request_threshold,
            resource_naming_prefix=resource_naming_prefix,
            waf_log_bucket_name=waf_log_bucket_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="validateResourceNamingPrefix")
    def validate_resource_naming_prefix(
        self,
        resource_naming_prefix: builtins.str,
    ) -> builtins.bool:
        '''
        :param resource_naming_prefix: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "validateResourceNamingPrefix", [resource_naming_prefix]))


@jsii.data_type(
    jsii_type="@ikala-cloud/aws-waf-solution.AutomatedWafProps",
    jsii_struct_bases=[],
    name_mapping={
        "waf2_scope": "waf2Scope",
        "app_access_log_bucket_name": "appAccessLogBucketName",
        "associated_resource_arn": "associatedResourceArn",
        "block_period": "blockPeriod",
        "count_mode": "countMode",
        "enable_shield_advanced_lambda": "enableShieldAdvancedLambda",
        "error_threshold": "errorThreshold",
        "log_level": "logLevel",
        "request_threshold": "requestThreshold",
        "resource_naming_prefix": "resourceNamingPrefix",
        "waf_log_bucket_name": "wafLogBucketName",
    },
)
class AutomatedWafProps:
    def __init__(
        self,
        *,
        waf2_scope: "Waf2ScopeOption",
        app_access_log_bucket_name: typing.Optional[builtins.str] = None,
        associated_resource_arn: typing.Optional[builtins.str] = None,
        block_period: typing.Optional[jsii.Number] = None,
        count_mode: typing.Optional[builtins.bool] = None,
        enable_shield_advanced_lambda: typing.Optional[builtins.bool] = None,
        error_threshold: typing.Optional[jsii.Number] = None,
        log_level: typing.Optional["LogLevel"] = None,
        request_threshold: typing.Optional[jsii.Number] = None,
        resource_naming_prefix: typing.Optional[builtins.str] = None,
        waf_log_bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param waf2_scope: (experimental) CLOUDFRONT or REGIONAL. If use REGIONAL, it support ALB、API Gateway
        :param app_access_log_bucket_name: 
        :param associated_resource_arn: (experimental) Only support ALB arn or API Gateway arn when waf2Scope is Regional. This property doesn't support CloudFront arn because it is restricted by CloudFormation ``AWS::WAFv2::WebACLAssociation`` , see more details: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafv2-webaclassociation.html#cfn-wafv2-webaclassociation-resourcearndetails:
        :param block_period: (experimental) The period (in minutes) to block applicable IP addresses.
        :param count_mode: (experimental) Test your WAF rules, see more details: `AWS WAF rule action <https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-action.html>`_. Default is false
        :param enable_shield_advanced_lambda: (experimental) Enable or disable AWS Shield Advance (:warning: it need `$3000 Monthly Fee <https://aws.amazon.com/shield/pricing/?nc1=h_ls>`_). Default is false
        :param error_threshold: (experimental) The maximum acceptable bad requests per minute per IP. :warning: The property map WAF ``Scanners and Probes`` Rule which support only CloudFront and ALB. Default is 200
        :param log_level: (experimental) Valid value is 'INFO', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
        :param request_threshold: (experimental) The maximum acceptable requests per FIVE-minute period per IP address. Default is 1000
        :param resource_naming_prefix: (experimental) If the construct need to deploy more than one times, specify the property to prevent AWS resource name conflict. (The property only allow alphanumeric and "_" symbol because glue database naming is needed)
        :param waf_log_bucket_name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "waf2_scope": waf2_scope,
        }
        if app_access_log_bucket_name is not None:
            self._values["app_access_log_bucket_name"] = app_access_log_bucket_name
        if associated_resource_arn is not None:
            self._values["associated_resource_arn"] = associated_resource_arn
        if block_period is not None:
            self._values["block_period"] = block_period
        if count_mode is not None:
            self._values["count_mode"] = count_mode
        if enable_shield_advanced_lambda is not None:
            self._values["enable_shield_advanced_lambda"] = enable_shield_advanced_lambda
        if error_threshold is not None:
            self._values["error_threshold"] = error_threshold
        if log_level is not None:
            self._values["log_level"] = log_level
        if request_threshold is not None:
            self._values["request_threshold"] = request_threshold
        if resource_naming_prefix is not None:
            self._values["resource_naming_prefix"] = resource_naming_prefix
        if waf_log_bucket_name is not None:
            self._values["waf_log_bucket_name"] = waf_log_bucket_name

    @builtins.property
    def waf2_scope(self) -> "Waf2ScopeOption":
        '''(experimental) CLOUDFRONT or REGIONAL.

        If use REGIONAL, it support ALB、API Gateway

        :stability: experimental
        '''
        result = self._values.get("waf2_scope")
        assert result is not None, "Required property 'waf2_scope' is missing"
        return typing.cast("Waf2ScopeOption", result)

    @builtins.property
    def app_access_log_bucket_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("app_access_log_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def associated_resource_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Only support ALB arn or API Gateway arn when waf2Scope is Regional.

        This property doesn't support CloudFront arn because it is restricted by CloudFormation ``AWS::WAFv2::WebACLAssociation`` , see more details: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-wafv2-webaclassociation.html#cfn-wafv2-webaclassociation-resourcearndetails:

        :stability: experimental
        '''
        result = self._values.get("associated_resource_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_period(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The period (in minutes) to block applicable IP addresses.

        :stability: experimental
        '''
        result = self._values.get("block_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def count_mode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Test your WAF rules, see more details: `AWS WAF rule action <https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-action.html>`_.

        Default is false

        :stability: experimental
        '''
        result = self._values.get("count_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_shield_advanced_lambda(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable or disable AWS Shield Advance (:warning: it need `$3000 Monthly Fee <https://aws.amazon.com/shield/pricing/?nc1=h_ls>`_).

        Default is false

        :stability: experimental
        '''
        result = self._values.get("enable_shield_advanced_lambda")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def error_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum acceptable bad requests per minute per IP.

        :warning: The property map WAF ``Scanners and Probes`` Rule which support only CloudFront and ALB.

        Default is 200

        :stability: experimental
        '''
        result = self._values.get("error_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_level(self) -> typing.Optional["LogLevel"]:
        '''(experimental) Valid value is 'INFO', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.

        :stability: experimental
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional["LogLevel"], result)

    @builtins.property
    def request_threshold(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum acceptable requests per FIVE-minute period per IP address.

        Default is 1000

        :stability: experimental
        '''
        result = self._values.get("request_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resource_naming_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the construct need to deploy more than one times, specify the property to prevent AWS resource name conflict.

        (The property only allow alphanumeric and "_" symbol because glue database naming is needed)

        :stability: experimental
        '''
        result = self._values.get("resource_naming_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def waf_log_bucket_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("waf_log_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutomatedWafProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@ikala-cloud/aws-waf-solution.LogLevel")
class LogLevel(enum.Enum):
    '''
    :stability: experimental
    '''

    DEBUG = "DEBUG"
    '''
    :stability: experimental
    '''
    INFO = "INFO"
    '''
    :stability: experimental
    '''
    WARNING = "WARNING"
    '''
    :stability: experimental
    '''
    ERROR = "ERROR"
    '''
    :stability: experimental
    '''
    CRITICAL = "CRITICAL"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@ikala-cloud/aws-waf-solution.Waf2ScopeOption")
class Waf2ScopeOption(enum.Enum):
    '''
    :stability: experimental
    '''

    CLOUDFRONT = "CLOUDFRONT"
    '''
    :stability: experimental
    '''
    REGIONAL = "REGIONAL"
    '''
    :stability: experimental
    '''


__all__ = [
    "AutomatedWaf",
    "AutomatedWafProps",
    "LogLevel",
    "Waf2ScopeOption",
]

publication.publish()
