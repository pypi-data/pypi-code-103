'''
# Deployer CDK Construct

This is a CDK construct library for deploying artifacts via CodeDeploy.

This library currently supports NodeJS and Python.

## Installation

Install with npm

```bash
$ npm install cdk-deployer
```

Install with pip

```bash
$ pip install cdk-deployer
```

## Usage/Examples

### TypeScript:

With `codeDeploy.ServerDeploymentGroup`:

```javascript
import * as cdk from '@aws-cdk/core';
import * as autoscaling from '@aws-cdk/aws-autoscaling';
import * as codedeploy from '@aws-cdk/aws-codedeploy';
import { Ec2Deployer, Code } from 'cdk-deployer';

const asg = new autoscaling.AutoScalingGroup(this, 'Asg', {
    ...
});
const deploymentGroup = new codedeploy.ServerDeploymentGroup(this, 'DeploymentGroup', {
    autoScalingGroups: [asg]
});

const deployer = new Ec2Deployer(this, 'Deployer', {
    code: Code.fromAsset('path/to/code/directory'),
    deploymentGroup,
});
```

With `codeDeploy.IServerDeploymentGroup`, also need to specify `instanceRoles`:

```javascript
import * as cdk from '@aws-cdk/core';
import * as codedeploy from '@aws-cdk/aws-codedeploy';
import * as iam from '@aws-cdk/aws-iam';
import { Ec2Deployer, Code } from 'cdk-deployer';

const deploymentGroup = codedeploy.ServerDeploymentGroup.fromServerDeploymentGroupAttributes(this, 'DeploymentGroup', {
    ...
});

const instanceRole = iam.Role.fromRoleArn(this, 'Role', cdk.Arn.format({
    service: 'iam',
    resource: 'role',
    resourceName: 'instance-role-name' // role assigned to target instances associated with deployment group
}, cdk.Stack.of(this)));

const deployer = new Ec2Deployer(this, 'Deployer', {
    code: Code.fromAsset('path/to/code/directory'),
    deploymentGroup,
    instanceRoles: [instanceRole]
});
```

### Python:

With `codeDeploy.ServerDeploymentGroup`:

```python
from aws_cdk import (
    core as cdk,
    aws_codedeploy as codedeploy,
    aws_autoscaling as autoscaling,
)
from cdk_deployer import (
    Ec2Deployer,
    Code
)

asg = autoscaling.AutoScalingGroup(self, 'Asg',
    ...)
deployment_group = codedeploy.ServerDeploymentGroup(self, 'DeploymentGroup',
    auto_scaling_groups=[asg])

deployment = Ec2Deployer(self, 'Deployment',
    code=Code.from_asset('path/to/code/directory'),
    deployment_group=deployment_group)
```

With `codeDeploy.IServerDeploymentGroup`, also need to specify `instance_roles`:

```python
from aws_cdk import (
    core as cdk,
    aws_autoscaling as autoscaling,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
)
from cdk_deployer import (
    Ec2Deployer,
    Code
)

deployment_group = codedeploy.ServerDeploymentGroup.from_server_deployment_group_attributes(self, 'DeploymentGroup',
    ...)

instance_role = iam.Role.from_role_arn(self, 'Role', cdk.Arn.format(
    components=cdk.ArnComponents(
        service='iam',
        resource='role',
        resource_name='instance-role-name'),
    stack=cdk.Stack.of(self)
))

deployment = Ec2Deployer(self, 'Deployment',
    code=Code.from_asset('app'),
    deployment_group=deployment_group,
    instance_roles=[instance_role])
```

See [example folder](./example) for a more complete example.

## Contributing

Contributions of all kinds are welcome and celebrated. Raise an issue, submit a PR, do the right thing.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contributing guidelines.

## License

[Apache 2.0](./LICENSE)
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

import aws_cdk.assets
import aws_cdk.aws_codedeploy
import aws_cdk.aws_iam
import aws_cdk.aws_s3
import aws_cdk.aws_s3_assets
import aws_cdk.core


class Code(metaclass=jsii.JSIIAbstractClass, jsii_type="cdk-deployer.Code"):
    '''Represents the Application Code.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset") # type: ignore[misc]
    @builtins.classmethod
    def from_asset(
        cls,
        path: builtins.str,
        *,
        readers: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IGrantable]] = None,
        source_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[aws_cdk.assets.FollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.core.IgnoreMode] = None,
        follow_symlinks: typing.Optional[aws_cdk.core.SymlinkFollowMode] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.core.AssetHashType] = None,
        bundling: typing.Optional[aws_cdk.core.BundlingOptions] = None,
    ) -> "AssetCode":
        '''Loads the application code from a local disk path.

        :param path: Either a directory with the application code bundle or a .zip file.
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_hash: (deprecated) Custom hash to use when identifying the specific version of the asset. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the source hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the source hash, you will need to make sure it is updated every time the source changes, or otherwise it is possible that some deployments will not be invalidated. Default: - automatically calculate source hash based on the contents of the source file or directory.
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        '''
        options = aws_cdk.aws_s3_assets.AssetOptions(
            readers=readers,
            source_hash=source_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
        )

        return typing.cast("AssetCode", jsii.sinvoke(cls, "fromAsset", [path, options]))

    @jsii.member(jsii_name="fromBucket") # type: ignore[misc]
    @builtins.classmethod
    def from_bucket(
        cls,
        bucket: aws_cdk.aws_s3.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> "S3Code":
        '''Application code as an S3 object.

        :param bucket: The S3 bucket.
        :param key: The object key.
        :param object_version: Optional S3 object version.
        '''
        return typing.cast("S3Code", jsii.sinvoke(cls, "fromBucket", [bucket, key, object_version]))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self, scope: aws_cdk.core.Construct) -> "CodeConfig":
        '''Called when the deployment object is initialized to allow this object to bind to the stack, add resources and have fun.

        :param scope: The binding scope. Don't be smart about trying to down-cast or assume it's initialized. You may just use it as a construct scope.
        '''
        ...


class _CodeProxy(Code):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct) -> "CodeConfig":
        '''Called when the deployment object is initialized to allow this object to bind to the stack, add resources and have fun.

        :param scope: The binding scope. Don't be smart about trying to down-cast or assume it's initialized. You may just use it as a construct scope.
        '''
        return typing.cast("CodeConfig", jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Code).__jsii_proxy_class__ = lambda : _CodeProxy


@jsii.data_type(
    jsii_type="cdk-deployer.CodeConfig",
    jsii_struct_bases=[],
    name_mapping={"s3_location": "s3Location"},
)
class CodeConfig:
    def __init__(self, *, s3_location: aws_cdk.aws_s3.Location) -> None:
        '''Result of binding ``Code`` into a ``Ec2Deployer``.

        :param s3_location: The location of the code in S3. Default: - code is an s3 location
        '''
        if isinstance(s3_location, dict):
            s3_location = aws_cdk.aws_s3.Location(**s3_location)
        self._values: typing.Dict[str, typing.Any] = {
            "s3_location": s3_location,
        }

    @builtins.property
    def s3_location(self) -> aws_cdk.aws_s3.Location:
        '''The location of the code in S3.

        :default: - code is an s3 location
        '''
        result = self._values.get("s3_location")
        assert result is not None, "Required property 's3_location' is missing"
        return typing.cast(aws_cdk.aws_s3.Location, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2Deployer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-deployer.Ec2Deployer",
):
    '''Represents a Deployer resource for deploying an artifact to EC2 using CodeDeploy.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        code: Code,
        deployment_group: aws_cdk.aws_codedeploy.IServerDeploymentGroup,
        deployment_timeout: typing.Optional[aws_cdk.core.Duration] = None,
        instance_roles: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IRole]] = None,
        wait_to_complete: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: The source code to be deployed.
        :param deployment_group: The deployment group to deploy the artifact to.
        :param deployment_timeout: Amount of time the stack will wait for the deployment operation to complete, for a maximum of 2 hours. Has no effect if waitToComplete = false. Default: - 5 minutes
        :param instance_roles: The IAM roles associated with the target instances to be deployed to. This is used to ensure the target instances have the appropriate permissions to download the deployment artifact from S3. This prop is only required when the instance roles cannot be dynamically pulled from the supplied deploymentGroup's autoScalingGroups property, for example when deploymentGroup is of type IServerDeploymentGroup or if the deploymentGroup is not associated with an ASG. Default: - gets the instance roles from serverDeploymentGroup.autoScalingGroups[].role
        :param wait_to_complete: Whether the enclosing stack should wait for the deployment to complete. Default: - true
        '''
        props = Ec2DeployerProps(
            code=code,
            deployment_group=deployment_group,
            deployment_timeout=deployment_timeout,
            instance_roles=instance_roles,
            wait_to_complete=wait_to_complete,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MAX_DEPLOYMENT_TIMEOUT")
    def MAX_DEPLOYMENT_TIMEOUT(cls) -> aws_cdk.core.Duration:
        '''Maximum allowed value for deploymentTimeout prop.'''
        return typing.cast(aws_cdk.core.Duration, jsii.sget(cls, "MAX_DEPLOYMENT_TIMEOUT"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="code")
    def code(self) -> CodeConfig:
        '''The source code to be deployed.'''
        return typing.cast(CodeConfig, jsii.get(self, "code"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentGroup")
    def deployment_group(self) -> aws_cdk.aws_codedeploy.IServerDeploymentGroup:
        '''The deployment group being deployed to.'''
        return typing.cast(aws_cdk.aws_codedeploy.IServerDeploymentGroup, jsii.get(self, "deploymentGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitToComplete")
    def wait_to_complete(self) -> builtins.bool:
        '''Whether the enclosing stack will wait for the deployment to complete.'''
        return typing.cast(builtins.bool, jsii.get(self, "waitToComplete"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentTimeout")
    def deployment_timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''Amount of time the stack will wait for the deployment operation to complete.'''
        return typing.cast(typing.Optional[aws_cdk.core.Duration], jsii.get(self, "deploymentTimeout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRoles")
    def instance_roles(self) -> typing.Optional[typing.List[aws_cdk.aws_iam.IRole]]:
        '''The IAM roles associated with the target instances to be deployed to.

        This is used to ensure the target instances have the appropriate permissions to download the deployment artifact from S3.
        This prop is only required when the instance roles cannot be dynamically pulled from the supplied deploymentGroup's autoScalingGroups property,
        for example when deploymentGroup is of type IServerDeploymentGroup or if the deploymentGroup is not associated with an ASG.
        '''
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.IRole]], jsii.get(self, "instanceRoles"))


@jsii.data_type(
    jsii_type="cdk-deployer.Ec2DeployerProps",
    jsii_struct_bases=[],
    name_mapping={
        "code": "code",
        "deployment_group": "deploymentGroup",
        "deployment_timeout": "deploymentTimeout",
        "instance_roles": "instanceRoles",
        "wait_to_complete": "waitToComplete",
    },
)
class Ec2DeployerProps:
    def __init__(
        self,
        *,
        code: Code,
        deployment_group: aws_cdk.aws_codedeploy.IServerDeploymentGroup,
        deployment_timeout: typing.Optional[aws_cdk.core.Duration] = None,
        instance_roles: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IRole]] = None,
        wait_to_complete: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Construction properties for the Ec2Deployer object.

        :param code: The source code to be deployed.
        :param deployment_group: The deployment group to deploy the artifact to.
        :param deployment_timeout: Amount of time the stack will wait for the deployment operation to complete, for a maximum of 2 hours. Has no effect if waitToComplete = false. Default: - 5 minutes
        :param instance_roles: The IAM roles associated with the target instances to be deployed to. This is used to ensure the target instances have the appropriate permissions to download the deployment artifact from S3. This prop is only required when the instance roles cannot be dynamically pulled from the supplied deploymentGroup's autoScalingGroups property, for example when deploymentGroup is of type IServerDeploymentGroup or if the deploymentGroup is not associated with an ASG. Default: - gets the instance roles from serverDeploymentGroup.autoScalingGroups[].role
        :param wait_to_complete: Whether the enclosing stack should wait for the deployment to complete. Default: - true
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "deployment_group": deployment_group,
        }
        if deployment_timeout is not None:
            self._values["deployment_timeout"] = deployment_timeout
        if instance_roles is not None:
            self._values["instance_roles"] = instance_roles
        if wait_to_complete is not None:
            self._values["wait_to_complete"] = wait_to_complete

    @builtins.property
    def code(self) -> Code:
        '''The source code to be deployed.'''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(Code, result)

    @builtins.property
    def deployment_group(self) -> aws_cdk.aws_codedeploy.IServerDeploymentGroup:
        '''The deployment group to deploy the artifact to.'''
        result = self._values.get("deployment_group")
        assert result is not None, "Required property 'deployment_group' is missing"
        return typing.cast(aws_cdk.aws_codedeploy.IServerDeploymentGroup, result)

    @builtins.property
    def deployment_timeout(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''Amount of time the stack will wait for the deployment operation to complete, for a maximum of 2 hours.

        Has no effect if waitToComplete = false.

        :default: - 5 minutes
        '''
        result = self._values.get("deployment_timeout")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def instance_roles(self) -> typing.Optional[typing.List[aws_cdk.aws_iam.IRole]]:
        '''The IAM roles associated with the target instances to be deployed to.

        This is used to ensure the target instances have the appropriate permissions to download the deployment artifact from S3.
        This prop is only required when the instance roles cannot be dynamically pulled from the supplied deploymentGroup's autoScalingGroups property,
        for example when deploymentGroup is of type IServerDeploymentGroup or if the deploymentGroup is not associated with an ASG.

        :default: - gets the instance roles from serverDeploymentGroup.autoScalingGroups[].role
        '''
        result = self._values.get("instance_roles")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.IRole]], result)

    @builtins.property
    def wait_to_complete(self) -> typing.Optional[builtins.bool]:
        '''Whether the enclosing stack should wait for the deployment to complete.

        :default: - true
        '''
        result = self._values.get("wait_to_complete")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2DeployerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-deployer.ResourceBindOptions",
    jsii_struct_bases=[],
    name_mapping={"resource_property": "resourceProperty"},
)
class ResourceBindOptions:
    def __init__(
        self,
        *,
        resource_property: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param resource_property: The name of the CloudFormation property to annotate with asset metadata. Default: Code
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if resource_property is not None:
            self._values["resource_property"] = resource_property

    @builtins.property
    def resource_property(self) -> typing.Optional[builtins.str]:
        '''The name of the CloudFormation property to annotate with asset metadata.

        :default: Code

        :see: https://github.com/aws/aws-cdk/issues/1432
        '''
        result = self._values.get("resource_property")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3Code(Code, metaclass=jsii.JSIIMeta, jsii_type="cdk-deployer.S3Code"):
    '''Application code from an S3 archive.'''

    def __init__(
        self,
        bucket: aws_cdk.aws_s3.IBucket,
        key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: -
        :param key: -
        :param object_version: -
        '''
        jsii.create(self.__class__, self, [bucket, key, object_version])

    @jsii.member(jsii_name="bind")
    def bind(self, _scope: aws_cdk.core.Construct) -> CodeConfig:
        '''Called when the deployment object is initialized to allow this object to bind to the stack, add resources and have fun.

        :param _scope: -
        '''
        return typing.cast(CodeConfig, jsii.invoke(self, "bind", [_scope]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isInline")
    def is_inline(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "isInline"))


class AssetCode(Code, metaclass=jsii.JSIIMeta, jsii_type="cdk-deployer.AssetCode"):
    '''Application code from a local directory.'''

    def __init__(
        self,
        path: builtins.str,
        *,
        readers: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IGrantable]] = None,
        source_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow: typing.Optional[aws_cdk.assets.FollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.core.IgnoreMode] = None,
        follow_symlinks: typing.Optional[aws_cdk.core.SymlinkFollowMode] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.core.AssetHashType] = None,
        bundling: typing.Optional[aws_cdk.core.BundlingOptions] = None,
    ) -> None:
        '''
        :param path: The path to the asset file or directory.
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param source_hash: (deprecated) Custom hash to use when identifying the specific version of the asset. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the source hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the source hash, you will need to make sure it is updated every time the source changes, or otherwise it is possible that some deployments will not be invalidated. Default: - automatically calculate source hash based on the contents of the source file or directory.
        :param exclude: (deprecated) Glob patterns to exclude from the copy. Default: nothing is excluded
        :param follow: (deprecated) A strategy for how to handle symlinks. Default: Never
        :param ignore_mode: (deprecated) The ignore behavior to use for exclude patterns. Default: - GLOB for file assets, DOCKER or GLOB for docker assets depending on whether the '
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        '''
        options = aws_cdk.aws_s3_assets.AssetOptions(
            readers=readers,
            source_hash=source_hash,
            exclude=exclude,
            follow=follow,
            ignore_mode=ignore_mode,
            follow_symlinks=follow_symlinks,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
        )

        jsii.create(self.__class__, self, [path, options])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: aws_cdk.core.Construct) -> CodeConfig:
        '''Called when the deployment object is initialized to allow this object to bind to the stack, add resources and have fun.

        :param scope: -
        '''
        return typing.cast(CodeConfig, jsii.invoke(self, "bind", [scope]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''The path to the asset file or directory.'''
        return typing.cast(builtins.str, jsii.get(self, "path"))


__all__ = [
    "AssetCode",
    "Code",
    "CodeConfig",
    "Ec2Deployer",
    "Ec2DeployerProps",
    "ResourceBindOptions",
    "S3Code",
]

publication.publish()
