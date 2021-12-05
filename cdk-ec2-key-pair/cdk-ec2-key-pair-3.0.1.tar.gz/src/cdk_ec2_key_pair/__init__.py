'''
# CDK EC2 Key Pair

[![Source](https://img.shields.io/badge/Source-GitHub-blue?logo=github)](https://github.com/udondan/cdk-ec2-key-pair)
[![Test](https://github.com/udondan/cdk-ec2-key-pair/workflows/Test/badge.svg)](https://github.com/udondan/cdk-ec2-key-pair/actions?query=workflow%3ATest)
[![GitHub](https://img.shields.io/github/license/udondan/cdk-ec2-key-pair)](https://github.com/udondan/cdk-ec2-key-pair/blob/master/LICENSE)
[![Docs](https://img.shields.io/badge/Construct%20Hub-cdk--ec2--key--pair-orange)](https://constructs.dev/packages/cdk-ec2-key-pair)

[![npm package](https://img.shields.io/npm/v/cdk-ec2-key-pair?color=brightgreen)](https://www.npmjs.com/package/cdk-ec2-key-pair)
[![PyPI package](https://img.shields.io/pypi/v/cdk-ec2-key-pair?color=brightgreen)](https://pypi.org/project/cdk-ec2-key-pair/)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
[![npm](https://img.shields.io/npm/dt/cdk-ec2-key-pair?label=npm&color=blueviolet)](https://www.npmjs.com/package/cdk-ec2-key-pair)
[![PyPI](https://img.shields.io/pypi/dm/cdk-ec2-key-pair?label=pypi&color=blueviolet)](https://pypi.org/project/cdk-ec2-key-pair/)

[AWS CDK](https://aws.amazon.com/cdk/) L3 construct for managing [EC2 Key Pairs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html).

CloudFormation doesn't directly support creation of EC2 Key Pairs. This construct provides an easy interface for creating Key Pairs through a [custom CloudFormation resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html). The private key is stored in [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/).

## Installation

This package has peer dependencies, which need to be installed along in the expected version.

For TypeScript/NodeJS, add these to your `dependencies` in `package.json`. For Python, add these to your `requirements.txt`:

* cdk-ec2-key-pair
* aws-cdk-lib (^2.0.0)
* cdk-iam-floyd (^0.300.0)
* constructs (^10.0.0)

## CDK compatibility

* Version 3.x is compatible with the CDK v2.
* Version 2.x is compatible with the CDK v1. There won't be regular updates for this.

## Usage

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk as cdk
from constructs import Construct
from cdk_ec2_key_pair import KeyPair

# ...

# Create the Key Pair
key = KeyPair(self, "A-Key-Pair",
    name="a-key-pair",
    description="This is a Key Pair",
    store_public_key=True
)

# Grant read access to the private key to a role or user
key.grant_read_on_private_key(some_role)

# Grant read access to the public key to another role or user
key.grant_read_on_public_key(another_role)

# Use Key Pair on an EC2 instance
ec2.Instance(self, "An-Instance",
    key_name=key.key_pair_name
)
```

The private (and optionally the public) key will be stored in AWS Secrets Manager. The secret names by default are prefixed with `ec2-ssh-key/`. The private key is suffixed with `/private`, the public key is suffixed with `/public`. So in this example they will be stored as `ec2-ssh-key/a-key-pair/private` and `ec2-ssh-key/a-key-pair/public`.

To download the private key via AWS cli you can run:

```bash
aws secretsmanager get-secret-value \
  --secret-id ec2-ssh-key/a-key-pair/private \
  --query SecretString \
  --output text
```

### Tag support

The construct supports tagging:

```python
# Example automatically generated from non-compiling source. May contain errors.
cdk.Tags.of(key).add("someTag", "some value")
```

We also use tags to restrict update/delete actions to those, the construct created itself. The Lambda function, which backs the custom CFN resource, is not able to manipulate other keys/secrets. The tag we use for identifying these resources is `CreatedByCfnCustomResource` with value `CFN::Resource::Custom::EC2-Key-Pair`.

### Updates

Since an EC2 KeyPair cannot be updated, you cannot change any property related to the KeyPair. The code has checks in place which will prevent any attempt to do so. If you try, the stack will end in a failed state. In that case you can safely continue the rollback in the AWS console and ignore the key resource.

You can, however, change properties that only relate to the secrets. These are the KMS keys used for encryption, the `secretPrefix`, `description` and `removeKeySecretsAfterDays`.

### Encryption

Secrets in the AWS Secrets Manager by default are encrypted with the key `alias/aws/secretsmanager`.

To use a custom KMS key you can pass it to the Key Pair:

```python
# Example automatically generated from non-compiling source. May contain errors.
kms_key = kms.Key(self, "KMS-key")

key_pair = KeyPair(self, "A-Key-Pair",
    name="a-key-pair",
    kms=kms_key
)
```

This KMS key needs to be created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified.

To use different KMS keys for the private and public key, use the `kmsPrivateKey` and `kmsPublicKey` instead:

```python
# Example automatically generated from non-compiling source. May contain errors.
kms_key_private = kms.Key(self, "KMS-key-private")
kms_key_public = kms.Key(self, "KMS-key-public")

key_pair = KeyPair(self, "A-Key-Pair",
    name="a-key-pair",
    kms_private_key=kms_key_private,
    kms_public_key=kms_key_public
)
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

from ._jsii import *

import aws_cdk
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import constructs


@jsii.implements(aws_cdk.ITaggable)
class KeyPair(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ec2-key-pair.KeyPair",
):
    '''An EC2 Key Pair.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expose_public_key: typing.Optional[builtins.bool] = None,
        kms: typing.Optional[aws_cdk.aws_kms.Key] = None,
        kms_private_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        kms_public_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        remove_key_secrets_after_days: typing.Optional[jsii.Number] = None,
        resource_prefix: typing.Optional[builtins.str] = None,
        secret_prefix: typing.Optional[builtins.str] = None,
        store_public_key: typing.Optional[builtins.bool] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Defines a new EC2 Key Pair.

        The private key will be stored in AWS Secrets Manager

        :param scope: -
        :param id: -
        :param name: Name of the Key Pair. In AWS Secrets Manager the key will be prefixed with ``ec2-ssh-key/``. The name can be up to 255 characters long. Valid characters include _, -, a-z, A-Z, and 0-9.
        :param description: The description for the key in AWS Secrets Manager. Default: - ''
        :param expose_public_key: Expose the public key as property ``publicKeyValue``. Default: - false
        :param kms: The KMS key used to encrypt the Secrets Manager secrets with. This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified. Default: - ``alias/aws/secretsmanager``
        :param kms_private_key: The KMS key to use to encrypt the private key with. This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified. If no value is provided, the property ``kms`` will be used instead. Default: - ``this.kms``
        :param kms_public_key: The KMS key to use to encrypt the public key with. This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified. If no value is provided, the property ``kms`` will be used instead. Default: - ``this.kms``
        :param remove_key_secrets_after_days: When the resource is destroyed, after how many days the private and public key in the AWS Secrets Manager should be deleted. Valid values are 0 and 7 to 30 Default: 0
        :param resource_prefix: A prefix for all resource names. By default all resources are prefixed with the stack name to avoid collisions with other stacks. This might cause problems when you work with long stack names and can be overridden through this parameter. Default: Name of the stack
        :param secret_prefix: Prefix for the secret in AWS Secrets Manager. Default: ``ec2-ssh-key/``
        :param store_public_key: Store the public key as a secret. Default: - false
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = KeyPairProps(
            name=name,
            description=description,
            expose_public_key=expose_public_key,
            kms=kms,
            kms_private_key=kms_private_key,
            kms_public_key=kms_public_key,
            remove_key_secrets_after_days=remove_key_secrets_after_days,
            resource_prefix=resource_prefix,
            secret_prefix=secret_prefix,
            store_public_key=store_public_key,
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantReadOnPrivateKey")
    def grant_read_on_private_key(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''Grants read access to the private key in AWS Secrets Manager.

        :param grantee: -
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantReadOnPrivateKey", [grantee]))

    @jsii.member(jsii_name="grantReadOnPublicKey")
    def grant_read_on_public_key(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''Grants read access to the public key in AWS Secrets Manager.

        :param grantee: -
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantReadOnPublicKey", [grantee]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairID")
    def key_pair_id(self) -> builtins.str:
        '''ID of the Key Pair.'''
        return typing.cast(builtins.str, jsii.get(self, "keyPairID"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairName")
    def key_pair_name(self) -> builtins.str:
        '''Name of the Key Pair.'''
        return typing.cast(builtins.str, jsii.get(self, "keyPairName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambda")
    def lambda_(self) -> aws_cdk.aws_lambda.IFunction:
        '''The lambda function that is created.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "lambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyArn")
    def private_key_arn(self) -> builtins.str:
        '''ARN of the private key in AWS Secrets Manager.'''
        return typing.cast(builtins.str, jsii.get(self, "privateKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyArn")
    def public_key_arn(self) -> builtins.str:
        '''ARN of the public key in AWS Secrets Manager.'''
        return typing.cast(builtins.str, jsii.get(self, "publicKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyValue")
    def public_key_value(self) -> builtins.str:
        '''The public key.

        Only filled, when ``exposePublicKey = true``
        '''
        return typing.cast(builtins.str, jsii.get(self, "publicKeyValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''Resource tags.'''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="cdk-ec2-key-pair.KeyPairProps",
    jsii_struct_bases=[aws_cdk.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "name": "name",
        "description": "description",
        "expose_public_key": "exposePublicKey",
        "kms": "kms",
        "kms_private_key": "kmsPrivateKey",
        "kms_public_key": "kmsPublicKey",
        "remove_key_secrets_after_days": "removeKeySecretsAfterDays",
        "resource_prefix": "resourcePrefix",
        "secret_prefix": "secretPrefix",
        "store_public_key": "storePublicKey",
    },
)
class KeyPairProps(aws_cdk.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expose_public_key: typing.Optional[builtins.bool] = None,
        kms: typing.Optional[aws_cdk.aws_kms.Key] = None,
        kms_private_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        kms_public_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        remove_key_secrets_after_days: typing.Optional[jsii.Number] = None,
        resource_prefix: typing.Optional[builtins.str] = None,
        secret_prefix: typing.Optional[builtins.str] = None,
        store_public_key: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Definition of EC2 Key Pair.

        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param name: Name of the Key Pair. In AWS Secrets Manager the key will be prefixed with ``ec2-ssh-key/``. The name can be up to 255 characters long. Valid characters include _, -, a-z, A-Z, and 0-9.
        :param description: The description for the key in AWS Secrets Manager. Default: - ''
        :param expose_public_key: Expose the public key as property ``publicKeyValue``. Default: - false
        :param kms: The KMS key used to encrypt the Secrets Manager secrets with. This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified. Default: - ``alias/aws/secretsmanager``
        :param kms_private_key: The KMS key to use to encrypt the private key with. This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified. If no value is provided, the property ``kms`` will be used instead. Default: - ``this.kms``
        :param kms_public_key: The KMS key to use to encrypt the public key with. This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified. If no value is provided, the property ``kms`` will be used instead. Default: - ``this.kms``
        :param remove_key_secrets_after_days: When the resource is destroyed, after how many days the private and public key in the AWS Secrets Manager should be deleted. Valid values are 0 and 7 to 30 Default: 0
        :param resource_prefix: A prefix for all resource names. By default all resources are prefixed with the stack name to avoid collisions with other stacks. This might cause problems when you work with long stack names and can be overridden through this parameter. Default: Name of the stack
        :param secret_prefix: Prefix for the secret in AWS Secrets Manager. Default: ``ec2-ssh-key/``
        :param store_public_key: Store the public key as a secret. Default: - false
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if account is not None:
            self._values["account"] = account
        if environment_from_arn is not None:
            self._values["environment_from_arn"] = environment_from_arn
        if physical_name is not None:
            self._values["physical_name"] = physical_name
        if region is not None:
            self._values["region"] = region
        if description is not None:
            self._values["description"] = description
        if expose_public_key is not None:
            self._values["expose_public_key"] = expose_public_key
        if kms is not None:
            self._values["kms"] = kms
        if kms_private_key is not None:
            self._values["kms_private_key"] = kms_private_key
        if kms_public_key is not None:
            self._values["kms_public_key"] = kms_public_key
        if remove_key_secrets_after_days is not None:
            self._values["remove_key_secrets_after_days"] = remove_key_secrets_after_days
        if resource_prefix is not None:
            self._values["resource_prefix"] = resource_prefix
        if secret_prefix is not None:
            self._values["secret_prefix"] = secret_prefix
        if store_public_key is not None:
            self._values["store_public_key"] = store_public_key

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID this resource belongs to.

        :default: - the resource is in the same account as the stack it belongs to
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_from_arn(self) -> typing.Optional[builtins.str]:
        '''ARN to deduce region and account from.

        The ARN is parsed and the account and region are taken from the ARN.
        This should be used for imported resources.

        Cannot be supplied together with either ``account`` or ``region``.

        :default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        '''
        result = self._values.get("environment_from_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def physical_name(self) -> typing.Optional[builtins.str]:
        '''The value passed in by users to the physical name prop of the resource.

        - ``undefined`` implies that a physical name will be allocated by
          CloudFormation during deployment.
        - a concrete value implies a specific physical name
        - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated
          by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation.

        :default: - The physical name will be allocated by CloudFormation at deployment time
        '''
        result = self._values.get("physical_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region this resource belongs to.

        :default: - the resource is in the same region as the stack it belongs to
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Key Pair.

        In AWS Secrets Manager the key will be prefixed with ``ec2-ssh-key/``.

        The name can be up to 255 characters long. Valid characters include _, -, a-z, A-Z, and 0-9.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description for the key in AWS Secrets Manager.

        :default: - ''
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expose_public_key(self) -> typing.Optional[builtins.bool]:
        '''Expose the public key as property ``publicKeyValue``.

        :default: - false
        '''
        result = self._values.get("expose_public_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def kms(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''The KMS key used to encrypt the Secrets Manager secrets with.

        This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified.

        :default: - ``alias/aws/secretsmanager``
        '''
        result = self._values.get("kms")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], result)

    @builtins.property
    def kms_private_key(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''The KMS key to use to encrypt the private key with.

        This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified.

        If no value is provided, the property ``kms`` will be used instead.

        :default: - ``this.kms``
        '''
        result = self._values.get("kms_private_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], result)

    @builtins.property
    def kms_public_key(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''The KMS key to use to encrypt the public key with.

        This needs to be a key created in the same stack. You cannot use a key imported via ARN, because the keys access policy will need to be modified.

        If no value is provided, the property ``kms`` will be used instead.

        :default: - ``this.kms``
        '''
        result = self._values.get("kms_public_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], result)

    @builtins.property
    def remove_key_secrets_after_days(self) -> typing.Optional[jsii.Number]:
        '''When the resource is destroyed, after how many days the private and public key in the AWS Secrets Manager should be deleted.

        Valid values are 0 and 7 to 30

        :default: 0
        '''
        result = self._values.get("remove_key_secrets_after_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def resource_prefix(self) -> typing.Optional[builtins.str]:
        '''A prefix for all resource names.

        By default all resources are prefixed with the stack name to avoid collisions with other stacks. This might cause problems when you work with long stack names and can be overridden through this parameter.

        :default: Name of the stack
        '''
        result = self._values.get("resource_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_prefix(self) -> typing.Optional[builtins.str]:
        '''Prefix for the secret in AWS Secrets Manager.

        :default: ``ec2-ssh-key/``
        '''
        result = self._values.get("secret_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def store_public_key(self) -> typing.Optional[builtins.bool]:
        '''Store the public key as a secret.

        :default: - false
        '''
        result = self._values.get("store_public_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KeyPairProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KeyPair",
    "KeyPairProps",
]

publication.publish()
