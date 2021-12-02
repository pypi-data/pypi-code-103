'''
# AWS CodePipeline Construct Library

## Pipeline

To construct an empty Pipeline:

```python
# Construct an empty Pipeline
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline")
```

To give the Pipeline a nice, human-readable name:

```python
# Give the Pipeline a nice, human-readable name
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    pipeline_name="MyPipeline"
)
```

Be aware that in the default configuration, the `Pipeline` construct creates
an AWS Key Management Service (AWS KMS) Customer Master Key (CMK) for you to
encrypt the artifacts in the artifact bucket, which incurs a cost of
**$1/month**. This default configuration is necessary to allow cross-account
actions.

If you do not intend to perform cross-account deployments, you can disable
the creation of the Customer Master Keys by passing `crossAccountKeys: false`
when defining the Pipeline:

```python
# Don't create Customer Master Keys
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    cross_account_keys=False
)
```

If you want to enable key rotation for the generated KMS keys,
you can configure it by passing `enableKeyRotation: true` when creating the pipeline.
Note that key rotation will incur an additional cost of **$1/month**.

```python
# Enable key rotation for the generated KMS key
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    # ...
    enable_key_rotation=True
)
```

## Stages

You can provide Stages when creating the Pipeline:

```python
# Provide a Stage when creating a pipeline
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    stages=[codepipeline.StageProps(
        stage_name="Source",
        actions=[]
    )
    ]
)
```

Or append a Stage to an existing Pipeline:

```python
# Append a Stage to an existing Pipeline
# pipeline is of type Pipeline

source_stage = pipeline.add_stage(
    stage_name="Source",
    actions=[]
)
```

You can insert the new Stage at an arbitrary point in the Pipeline:

```python
# Insert a new Stage at an arbitrary point
# pipeline is of type Pipeline
# another_stage is of type IStage
# yet_another_stage is of type IStage


some_stage = pipeline.add_stage(
    stage_name="SomeStage",
    placement=codepipeline.StagePlacement(
        # note: you can only specify one of the below properties
        right_before=another_stage,
        just_after=yet_another_stage
    )
)
```

## Actions

Actions live in a separate package, `@aws-cdk/aws-codepipeline-actions`.

To add an Action to a Stage, you can provide it when creating the Stage,
in the `actions` property,
or you can use the `IStage.addAction()` method to mutate an existing Stage:

```python
# Use the `IStage.addAction()` method to mutate an existing Stage.
# source_stage is of type IStage
# some_action is of type Action

source_stage.add_action(some_action)
```

## Custom Action Registration

To make your own custom CodePipeline Action requires registering the action provider. Look to the `JenkinsProvider` in `@aws-cdk/aws-codepipeline-actions` for an implementation example.

```python
# Make a custom CodePipeline Action
codepipeline.CustomActionRegistration(self, "GenericGitSourceProviderResource",
    category=codepipeline.ActionCategory.SOURCE,
    artifact_bounds=codepipeline.ActionArtifactBounds(min_inputs=0, max_inputs=0, min_outputs=1, max_outputs=1),
    provider="GenericGitSource",
    version="1",
    entity_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
    execution_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
    action_properties=[codepipeline.CustomActionProperty(
        name="Branch",
        required=True,
        key=False,
        secret=False,
        queryable=False,
        description="Git branch to pull",
        type="String"
    ), codepipeline.CustomActionProperty(
        name="GitUrl",
        required=True,
        key=False,
        secret=False,
        queryable=False,
        description="SSH git clone URL",
        type="String"
    )
    ]
)
```

## Cross-account CodePipelines

> Cross-account Pipeline actions require that the Pipeline has *not* been
> created with `crossAccountKeys: false`.

Most pipeline Actions accept an AWS resource object to operate on. For example:

* `S3DeployAction` accepts an `s3.IBucket`.
* `CodeBuildAction` accepts a `codebuild.IProject`.
* etc.

These resources can be either newly defined (`new s3.Bucket(...)`) or imported
(`s3.Bucket.fromBucketAttributes(...)`) and identify the resource that should
be changed.

These resources can be in different accounts than the pipeline itself. For
example, the following action deploys to an imported S3 bucket from a
different account:

```python
# Deploy an imported S3 bucket from a different account
# stage is of type IStage
# input is of type Artifact

stage.add_action(codepipeline_actions.S3DeployAction(
    bucket=s3.Bucket.from_bucket_attributes(self, "Bucket",
        account="123456789012"
    ),
    input=input,
    action_name="s3-deploy-action"
))
```

Actions that don't accept a resource object accept an explicit `account` parameter:

```python
# Actions that don't accept a resource objet accept an explicit `account` parameter
# stage is of type IStage
# template_path is of type ArtifactPath

stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
    account="123456789012",
    template_path=template_path,
    admin_permissions=False,
    stack_name=Stack.of(self).stack_name,
    action_name="cloudformation-create-update"
))
```

The `Pipeline` construct automatically defines an **IAM Role** for you in the
target account which the pipeline will assume to perform that action. This
Role will be defined in a **support stack** named
`<PipelineStackName>-support-<account>`, that will automatically be deployed
before the stack containing the pipeline.

If you do not want to use the generated role, you can also explicitly pass a
`role` when creating the action. In that case, the action will operate in the
account the role belongs to:

```python
# Explicitly pass in a `role` when creating an action.
# stage is of type IStage
# template_path is of type ArtifactPath

stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
    template_path=template_path,
    admin_permissions=False,
    stack_name=Stack.of(self).stack_name,
    action_name="cloudformation-create-update",
    # ...
    role=iam.Role.from_role_arn(self, "ActionRole", "...")
))
```

## Cross-region CodePipelines

Similar to how you set up a cross-account Action, the AWS resource object you
pass to actions can also be in different *Regions*. For example, the
following Action deploys to an imported S3 bucket from a different Region:

```python
# Deploy to an imported S3 bucket from a different Region.
# stage is of type IStage
# input is of type Artifact

stage.add_action(codepipeline_actions.S3DeployAction(
    bucket=s3.Bucket.from_bucket_attributes(self, "Bucket",
        region="us-west-1"
    ),
    input=input,
    action_name="s3-deploy-action"
))
```

Actions that don't take an AWS resource will accept an explicit `region`
parameter:

```python
# Actions that don't take an AWS resource will accept an explicit `region` parameter.
# stage is of type IStage
# template_path is of type ArtifactPath

stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
    template_path=template_path,
    admin_permissions=False,
    stack_name=Stack.of(self).stack_name,
    action_name="cloudformation-create-update",
    # ...
    region="us-west-1"
))
```

The `Pipeline` construct automatically defines a **replication bucket** for
you in the target region, which the pipeline will replicate artifacts to and
from. This Bucket will be defined in a **support stack** named
`<PipelineStackName>-support-<region>`, that will automatically be deployed
before the stack containing the pipeline.

If you don't want to use these support stacks, and already have buckets in
place to serve as replication buckets, you can supply these at Pipeline definition
time using the `crossRegionReplicationBuckets` parameter. Example:

```python
# Supply replication buckets for the Pipeline instead of using the generated support stack
pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
    # ...

    cross_region_replication_buckets={
        # note that a physical name of the replication Bucket must be known at synthesis time
        "us-west-1": s3.Bucket.from_bucket_attributes(self, "UsWest1ReplicationBucket",
            bucket_name="my-us-west-1-replication-bucket",
            # optional KMS key
            encryption_key=kms.Key.from_key_arn(self, "UsWest1ReplicationKey", "arn:aws:kms:us-west-1:123456789012:key/1234-5678-9012")
        )
    }
)
```

See [the AWS docs here](https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-cross-region.html)
for more information on cross-region CodePipelines.

### Creating an encrypted replication bucket

If you're passing a replication bucket created in a different stack,
like this:

```python
# Passing a replication bucket created in a different stack.
app = App()
replication_stack = Stack(app, "ReplicationStack",
    env=Environment(
        region="us-west-1"
    )
)
key = kms.Key(replication_stack, "ReplicationKey")
replication_bucket = s3.Bucket(replication_stack, "ReplicationBucket",
    # like was said above - replication buckets need a set physical name
    bucket_name=PhysicalName.GENERATE_IF_NEEDED,
    encryption_key=key
)

# later...
codepipeline.Pipeline(replication_stack, "Pipeline",
    cross_region_replication_buckets={
        "us-west-1": replication_bucket
    }
)
```

When trying to encrypt it
(and note that if any of the cross-region actions happen to be cross-account as well,
the bucket *has to* be encrypted - otherwise the pipeline will fail at runtime),
you cannot use a key directly - KMS keys don't have physical names,
and so you can't reference them across environments.

In this case, you need to use an alias in place of the key when creating the bucket:

```python
# Passing an encrypted replication bucket created in a different stack.
app = App()
replication_stack = Stack(app, "ReplicationStack",
    env=Environment(
        region="us-west-1"
    )
)
key = kms.Key(replication_stack, "ReplicationKey")
alias = kms.Alias(replication_stack, "ReplicationAlias",
    # aliasName is required
    alias_name=PhysicalName.GENERATE_IF_NEEDED,
    target_key=key
)
replication_bucket = s3.Bucket(replication_stack, "ReplicationBucket",
    bucket_name=PhysicalName.GENERATE_IF_NEEDED,
    encryption_key=alias
)
```

## Variables

The library supports the CodePipeline Variables feature.
Each action class that emits variables has a separate variables interface,
accessed as a property of the action instance called `variables`.
You instantiate the action class and assign it to a local variable;
when you want to use a variable in the configuration of a different action,
you access the appropriate property of the interface returned from `variables`,
which represents a single variable.
Example:

```python
# MyAction is some action type that produces variables, like EcrSourceAction
my_action = MyAction(
    # ...
    action_name="myAction"
)
OtherAction(
    # ...
    config=my_action.variables.my_variable,
    action_name="otherAction"
)
```

The namespace name that will be used will be automatically generated by the pipeline construct,
based on the stage and action name;
you can pass a custom name when creating the action instance:

```python
# MyAction is some action type that produces variables, like EcrSourceAction
my_action = MyAction(
    # ...
    variables_namespace="MyNamespace",
    action_name="myAction"
)
```

There are also global variables available,
not tied to any action;
these are accessed through static properties of the `GlobalVariables` class:

```python
# OtherAction is some action type that produces variables, like EcrSourceAction
OtherAction(
    # ...
    config=codepipeline.GlobalVariables.execution_id,
    action_name="otherAction"
)
```

Check the documentation of the `@aws-cdk/aws-codepipeline-actions`
for details on how to use the variables for each action class.

See the [CodePipeline documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-variables.html)
for more details on how to use the variables feature.

## Events

### Using a pipeline as an event target

A pipeline can be used as a target for a CloudWatch event rule:

```python
# A pipeline being used as a target for a CloudWatch event rule.
import aws_cdk.aws_events_targets as targets
import aws_cdk.aws_events as events

# pipeline is of type Pipeline


# kick off the pipeline every day
rule = events.Rule(self, "Daily",
    schedule=events.Schedule.rate(Duration.days(1))
)
rule.add_target(targets.CodePipeline(pipeline))
```

When a pipeline is used as an event target, the
"codepipeline:StartPipelineExecution" permission is granted to the AWS
CloudWatch Events service.

### Event sources

Pipelines emit CloudWatch events. To define event rules for events emitted by
the pipeline, stages or action, use the `onXxx` methods on the respective
construct:

```python
# Define event rules for events emitted by the pipeline
import aws_cdk.aws_events as events

# my_pipeline is of type Pipeline
# my_stage is of type IStage
# my_action is of type Action
# target is of type IRuleTarget

my_pipeline.on_state_change("MyPipelineStateChange", target=target)
my_stage.on_state_change("MyStageStateChange", target)
my_action.on_state_change("MyActionStateChange", target)
```

## CodeStar Notifications

To define CodeStar Notification rules for Pipelines, use one of the `notifyOnXxx()` methods.
They are very similar to `onXxx()` methods for CloudWatch events:

```python
# Define CodeStar Notification rules for Pipelines
import aws_cdk.aws_chatbot as chatbot

# pipeline is of type Pipeline

target = chatbot.SlackChannelConfiguration(self, "MySlackChannel",
    slack_channel_configuration_name="YOUR_CHANNEL_NAME",
    slack_workspace_id="YOUR_SLACK_WORKSPACE_ID",
    slack_channel_id="YOUR_SLACK_CHANNEL_ID"
)
rule = pipeline.notify_on_execution_state_change("NotifyOnExecutionStateChange", target)
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
    IResource as _IResource_c80c4260,
    Resource as _Resource_45bc6135,
    Stack as _Stack_2866e57f,
    TagManager as _TagManager_0a598cb3,
    TreeInspector as _TreeInspector_488e0dd5,
)
from ..aws_codestarnotifications import (
    DetailType as _DetailType_cf8135e7,
    INotificationRule as _INotificationRule_71939426,
    INotificationRuleSource as _INotificationRuleSource_10482823,
    INotificationRuleTarget as _INotificationRuleTarget_faa3b79b,
    NotificationRuleOptions as _NotificationRuleOptions_dff73281,
    NotificationRuleSourceConfig as _NotificationRuleSourceConfig_20189a3e,
)
from ..aws_events import (
    EventPattern as _EventPattern_fe557901,
    IEventBus as _IEventBus_88d13111,
    IRuleTarget as _IRuleTarget_7a91f454,
    OnEventOptions as _OnEventOptions_8711b8b3,
    Rule as _Rule_334ed2b5,
    RuleProps as _RuleProps_11ecd19e,
    Schedule as _Schedule_c151d01f,
)
from ..aws_iam import (
    IRole as _IRole_235f5d8e, PolicyStatement as _PolicyStatement_0fe33853
)
from ..aws_s3 import IBucket as _IBucket_42e086fd, Location as _Location_0948fa7f


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.ActionArtifactBounds",
    jsii_struct_bases=[],
    name_mapping={
        "max_inputs": "maxInputs",
        "max_outputs": "maxOutputs",
        "min_inputs": "minInputs",
        "min_outputs": "minOutputs",
    },
)
class ActionArtifactBounds:
    def __init__(
        self,
        *,
        max_inputs: jsii.Number,
        max_outputs: jsii.Number,
        min_inputs: jsii.Number,
        min_outputs: jsii.Number,
    ) -> None:
        '''Specifies the constraints on the number of input and output artifacts an action can have.

        The constraints for each action type are documented on the
        {@link https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html Pipeline Structure Reference} page.

        :param max_inputs: 
        :param max_outputs: 
        :param min_inputs: 
        :param min_outputs: 

        Example::

            # MyAction is some action type that produces variables, like EcrSourceAction
            my_action = MyAction(
                # ...
                action_name="myAction"
            )
            OtherAction(
                # ...
                config=my_action.variables.my_variable,
                action_name="otherAction"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max_inputs": max_inputs,
            "max_outputs": max_outputs,
            "min_inputs": min_inputs,
            "min_outputs": min_outputs,
        }

    @builtins.property
    def max_inputs(self) -> jsii.Number:
        result = self._values.get("max_inputs")
        assert result is not None, "Required property 'max_inputs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def max_outputs(self) -> jsii.Number:
        result = self._values.get("max_outputs")
        assert result is not None, "Required property 'max_outputs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_inputs(self) -> jsii.Number:
        result = self._values.get("min_inputs")
        assert result is not None, "Required property 'min_inputs' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_outputs(self) -> jsii.Number:
        result = self._values.get("min_outputs")
        assert result is not None, "Required property 'min_outputs' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionArtifactBounds(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.ActionBindOptions",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "role": "role"},
)
class ActionBindOptions:
    def __init__(self, *, bucket: _IBucket_42e086fd, role: _IRole_235f5d8e) -> None:
        '''
        :param bucket: 
        :param role: 

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            from aws_cdk import aws_iam as iam
            from aws_cdk import aws_s3 as s3
            
            # bucket is of type Bucket
            # role is of type Role
            
            action_bind_options = codepipeline.ActionBindOptions(
                bucket=bucket,
                role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
            "role": role,
        }

    @builtins.property
    def bucket(self) -> _IBucket_42e086fd:
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_IBucket_42e086fd, result)

    @builtins.property
    def role(self) -> _IRole_235f5d8e:
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(_IRole_235f5d8e, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="aws-cdk-lib.aws_codepipeline.ActionCategory")
class ActionCategory(enum.Enum):
    '''
    Example::

        # MyAction is some action type that produces variables, like EcrSourceAction
        my_action = MyAction(
            # ...
            action_name="myAction"
        )
        OtherAction(
            # ...
            config=my_action.variables.my_variable,
            action_name="otherAction"
        )
    '''

    APPROVAL = "APPROVAL"
    BUILD = "BUILD"
    DEPLOY = "DEPLOY"
    INVOKE = "INVOKE"
    SOURCE = "SOURCE"
    TEST = "TEST"


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.ActionConfig",
    jsii_struct_bases=[],
    name_mapping={"configuration": "configuration"},
)
class ActionConfig:
    def __init__(self, *, configuration: typing.Any = None) -> None:
        '''
        :param configuration: 

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            # configuration is of type object
            
            action_config = codepipeline.ActionConfig(
                configuration=configuration
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if configuration is not None:
            self._values["configuration"] = configuration

    @builtins.property
    def configuration(self) -> typing.Any:
        result = self._values.get("configuration")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.ActionProperties",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "action_name": "actionName",
        "artifact_bounds": "artifactBounds",
        "category": "category",
        "inputs": "inputs",
        "outputs": "outputs",
        "owner": "owner",
        "provider": "provider",
        "region": "region",
        "resource": "resource",
        "role": "role",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "version": "version",
    },
)
class ActionProperties:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        action_name: builtins.str,
        artifact_bounds: ActionArtifactBounds,
        category: ActionCategory,
        inputs: typing.Optional[typing.Sequence["Artifact"]] = None,
        outputs: typing.Optional[typing.Sequence["Artifact"]] = None,
        owner: typing.Optional[builtins.str] = None,
        provider: builtins.str,
        region: typing.Optional[builtins.str] = None,
        resource: typing.Optional[_IResource_c80c4260] = None,
        role: typing.Optional[_IRole_235f5d8e] = None,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: The account the Action is supposed to live in. For Actions backed by resources, this is inferred from the Stack {@link resource} is part of. However, some Actions, like the CloudFormation ones, are not backed by any resource, and they still might want to be cross-account. In general, a concrete Action class should specify either {@link resource}, or {@link account} - but not both.
        :param action_name: 
        :param artifact_bounds: 
        :param category: The category of the action. The category defines which action type the owner (the entity that performs the action) performs.
        :param inputs: 
        :param outputs: 
        :param owner: 
        :param provider: The service provider that the action calls.
        :param region: The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param resource: The optional resource that is backing this Action. This is used for automatically handling Actions backed by resources from a different account and/or region.
        :param role: 
        :param run_order: The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide. https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names
        :param version: 

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk as cdk
            from aws_cdk import aws_codepipeline as codepipeline
            from aws_cdk import aws_iam as iam
            
            # artifact is of type Artifact
            # resource is of type Resource
            # role is of type Role
            
            action_properties = codepipeline.ActionProperties(
                action_name="actionName",
                artifact_bounds=codepipeline.ActionArtifactBounds(
                    max_inputs=123,
                    max_outputs=123,
                    min_inputs=123,
                    min_outputs=123
                ),
                category=codepipeline.ActionCategory.SOURCE,
                provider="provider",
            
                # the properties below are optional
                account="account",
                inputs=[artifact],
                outputs=[artifact],
                owner="owner",
                region="region",
                resource=resource,
                role=role,
                run_order=123,
                variables_namespace="variablesNamespace",
                version="version"
            )
        '''
        if isinstance(artifact_bounds, dict):
            artifact_bounds = ActionArtifactBounds(**artifact_bounds)
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "artifact_bounds": artifact_bounds,
            "category": category,
            "provider": provider,
        }
        if account is not None:
            self._values["account"] = account
        if inputs is not None:
            self._values["inputs"] = inputs
        if outputs is not None:
            self._values["outputs"] = outputs
        if owner is not None:
            self._values["owner"] = owner
        if region is not None:
            self._values["region"] = region
        if resource is not None:
            self._values["resource"] = resource
        if role is not None:
            self._values["role"] = role
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''The account the Action is supposed to live in.

        For Actions backed by resources,
        this is inferred from the Stack {@link resource} is part of.
        However, some Actions, like the CloudFormation ones,
        are not backed by any resource, and they still might want to be cross-account.
        In general, a concrete Action class should specify either {@link resource},
        or {@link account} - but not both.
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def action_name(self) -> builtins.str:
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifact_bounds(self) -> ActionArtifactBounds:
        result = self._values.get("artifact_bounds")
        assert result is not None, "Required property 'artifact_bounds' is missing"
        return typing.cast(ActionArtifactBounds, result)

    @builtins.property
    def category(self) -> ActionCategory:
        '''The category of the action.

        The category defines which action type the owner
        (the entity that performs the action) performs.
        '''
        result = self._values.get("category")
        assert result is not None, "Required property 'category' is missing"
        return typing.cast(ActionCategory, result)

    @builtins.property
    def inputs(self) -> typing.Optional[typing.List["Artifact"]]:
        result = self._values.get("inputs")
        return typing.cast(typing.Optional[typing.List["Artifact"]], result)

    @builtins.property
    def outputs(self) -> typing.Optional[typing.List["Artifact"]]:
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.List["Artifact"]], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''The service provider that the action calls.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region the given Action resides in.

        Note that a cross-region Pipeline requires replication buckets to function correctly.
        You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property.
        If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets,
        that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        :default: the Action resides in the same region as the Pipeline
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource(self) -> typing.Optional[_IResource_c80c4260]:
        '''The optional resource that is backing this Action.

        This is used for automatically handling Actions backed by
        resources from a different account and/or region.
        '''
        result = self._values.get("resource")
        return typing.cast(typing.Optional[_IResource_c80c4260], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_235f5d8e]:
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_235f5d8e], result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide.

        https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default: - a name will be generated, based on the stage and action names
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ActionProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Artifact(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.Artifact",
):
    '''An output artifact of an action.

    Artifacts can be used as input by some actions.

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_ecs as ecs
        
        # service is of type FargateService
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        build_output = codepipeline.Artifact()
        deploy_stage = pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.EcsDeployAction(
                    action_name="DeployAction",
                    service=service,
                    # if your file is called imagedefinitions.json,
                    # use the `input` property,
                    # and leave out the `imageFile` property
                    input=build_output,
                    # if your file name is _not_ imagedefinitions.json,
                    # use the `imageFile` property,
                    # and leave out the `input` property
                    image_file=build_output.at_path("imageDef.json"),
                    deployment_timeout=Duration.minutes(60)
                )
            ]
        )
    '''

    def __init__(self, artifact_name: typing.Optional[builtins.str] = None) -> None:
        '''
        :param artifact_name: -
        '''
        jsii.create(self.__class__, self, [artifact_name])

    @jsii.member(jsii_name="artifact") # type: ignore[misc]
    @builtins.classmethod
    def artifact(cls, name: builtins.str) -> "Artifact":
        '''A static factory method used to create instances of the Artifact class.

        Mainly meant to be used from ``decdk``.

        :param name: the (required) name of the Artifact.
        '''
        return typing.cast("Artifact", jsii.sinvoke(cls, "artifact", [name]))

    @jsii.member(jsii_name="atPath")
    def at_path(self, file_name: builtins.str) -> "ArtifactPath":
        '''Returns an ArtifactPath for a file within this artifact.

        CfnOutput is in the form "::"

        :param file_name: The name of the file.
        '''
        return typing.cast("ArtifactPath", jsii.invoke(self, "atPath", [file_name]))

    @jsii.member(jsii_name="getMetadata")
    def get_metadata(self, key: builtins.str) -> typing.Any:
        '''Retrieve the metadata stored in this artifact under the given key.

        If there is no metadata stored under the given key,
        null will be returned.

        :param key: -
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "getMetadata", [key]))

    @jsii.member(jsii_name="getParam")
    def get_param(
        self,
        json_file: builtins.str,
        key_name: builtins.str,
    ) -> builtins.str:
        '''Returns a token for a value inside a JSON file within this artifact.

        :param json_file: The JSON file name.
        :param key_name: The hash key.
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "getParam", [json_file, key_name]))

    @jsii.member(jsii_name="setMetadata")
    def set_metadata(self, key: builtins.str, value: typing.Any) -> None:
        '''Add arbitrary extra payload to the artifact under a given key.

        This can be used by CodePipeline actions to communicate data between themselves.
        If metadata was already present under the given key,
        it will be overwritten with the new value.

        :param key: -
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "setMetadata", [key, value]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactName")
    def artifact_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        '''The artifact attribute for the name of the S3 bucket where the artifact is stored.'''
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="objectKey")
    def object_key(self) -> builtins.str:
        '''The artifact attribute for The name of the .zip file that contains the artifact that is generated by AWS CodePipeline, such as 1ABCyZZ.zip.'''
        return typing.cast(builtins.str, jsii.get(self, "objectKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Location")
    def s3_location(self) -> _Location_0948fa7f:
        '''Returns the location of the .zip file in S3 that this Artifact represents. Used by Lambda's ``CfnParametersCode`` when being deployed in a CodePipeline.'''
        return typing.cast(_Location_0948fa7f, jsii.get(self, "s3Location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''The artifact attribute of the Amazon Simple Storage Service (Amazon S3) URL of the artifact, such as https://s3-us-west-2.amazonaws.com/artifactstorebucket-yivczw8jma0c/test/TemplateSo/1ABCyZZ.zip.'''
        return typing.cast(builtins.str, jsii.get(self, "url"))


class ArtifactPath(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.ArtifactPath",
):
    '''A specific file within an output artifact.

    The most common use case for this is specifying the template file
    for a CloudFormation action.

    Example::

        # Explicitly pass in a `role` when creating an action.
        # stage is of type IStage
        # template_path is of type ArtifactPath
        
        stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
            template_path=template_path,
            admin_permissions=False,
            stack_name=Stack.of(self).stack_name,
            action_name="cloudformation-create-update",
            # ...
            role=iam.Role.from_role_arn(self, "ActionRole", "...")
        ))
    '''

    def __init__(self, artifact: Artifact, file_name: builtins.str) -> None:
        '''
        :param artifact: -
        :param file_name: -
        '''
        jsii.create(self.__class__, self, [artifact, file_name])

    @jsii.member(jsii_name="artifactPath") # type: ignore[misc]
    @builtins.classmethod
    def artifact_path(
        cls,
        artifact_name: builtins.str,
        file_name: builtins.str,
    ) -> "ArtifactPath":
        '''
        :param artifact_name: -
        :param file_name: -
        '''
        return typing.cast("ArtifactPath", jsii.sinvoke(cls, "artifactPath", [artifact_name, file_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifact")
    def artifact(self) -> Artifact:
        return typing.cast(Artifact, jsii.get(self, "artifact"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))


@jsii.implements(_IInspectable_c2943556)
class CfnCustomActionType(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.CfnCustomActionType",
):
    '''A CloudFormation ``AWS::CodePipeline::CustomActionType``.

    :cloudformationResource: AWS::CodePipeline::CustomActionType
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_codepipeline as codepipeline
        
        cfn_custom_action_type = codepipeline.CfnCustomActionType(self, "MyCfnCustomActionType",
            category="category",
            input_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                maximum_count=123,
                minimum_count=123
            ),
            output_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                maximum_count=123,
                minimum_count=123
            ),
            provider="provider",
            version="version",
        
            # the properties below are optional
            configuration_properties=[codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty(
                key=False,
                name="name",
                required=False,
                secret=False,
        
                # the properties below are optional
                description="description",
                queryable=False,
                type="type"
            )],
            settings=codepipeline.CfnCustomActionType.SettingsProperty(
                entity_url_template="entityUrlTemplate",
                execution_url_template="executionUrlTemplate",
                revision_url_template="revisionUrlTemplate",
                third_party_configuration_url="thirdPartyConfigurationUrl"
            ),
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
        category: builtins.str,
        configuration_properties: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnCustomActionType.ConfigurationPropertiesProperty", _IResolvable_da3f097b]]]] = None,
        input_artifact_details: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b],
        output_artifact_details: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b],
        provider: builtins.str,
        settings: typing.Optional[typing.Union["CfnCustomActionType.SettingsProperty", _IResolvable_da3f097b]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        version: builtins.str,
    ) -> None:
        '''Create a new ``AWS::CodePipeline::CustomActionType``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param category: ``AWS::CodePipeline::CustomActionType.Category``.
        :param configuration_properties: ``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.
        :param input_artifact_details: ``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.
        :param output_artifact_details: ``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.
        :param provider: ``AWS::CodePipeline::CustomActionType.Provider``.
        :param settings: ``AWS::CodePipeline::CustomActionType.Settings``.
        :param tags: ``AWS::CodePipeline::CustomActionType.Tags``.
        :param version: ``AWS::CodePipeline::CustomActionType.Version``.
        '''
        props = CfnCustomActionTypeProps(
            category=category,
            configuration_properties=configuration_properties,
            input_artifact_details=input_artifact_details,
            output_artifact_details=output_artifact_details,
            provider=provider,
            settings=settings,
            tags=tags,
            version=version,
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
    @jsii.member(jsii_name="category")
    def category(self) -> builtins.str:
        '''``AWS::CodePipeline::CustomActionType.Category``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
        '''
        return typing.cast(builtins.str, jsii.get(self, "category"))

    @category.setter
    def category(self, value: builtins.str) -> None:
        jsii.set(self, "category", value)

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
    @jsii.member(jsii_name="configurationProperties")
    def configuration_properties(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCustomActionType.ConfigurationPropertiesProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCustomActionType.ConfigurationPropertiesProperty", _IResolvable_da3f097b]]]], jsii.get(self, "configurationProperties"))

    @configuration_properties.setter
    def configuration_properties(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnCustomActionType.ConfigurationPropertiesProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "configurationProperties", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputArtifactDetails")
    def input_artifact_details(
        self,
    ) -> typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b]:
        '''``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
        '''
        return typing.cast(typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b], jsii.get(self, "inputArtifactDetails"))

    @input_artifact_details.setter
    def input_artifact_details(
        self,
        value: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "inputArtifactDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputArtifactDetails")
    def output_artifact_details(
        self,
    ) -> typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b]:
        '''``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
        '''
        return typing.cast(typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b], jsii.get(self, "outputArtifactDetails"))

    @output_artifact_details.setter
    def output_artifact_details(
        self,
        value: typing.Union["CfnCustomActionType.ArtifactDetailsProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "outputArtifactDetails", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        '''``AWS::CodePipeline::CustomActionType.Provider``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
        '''
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        jsii.set(self, "provider", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="settings")
    def settings(
        self,
    ) -> typing.Optional[typing.Union["CfnCustomActionType.SettingsProperty", _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::CustomActionType.Settings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
        '''
        return typing.cast(typing.Optional[typing.Union["CfnCustomActionType.SettingsProperty", _IResolvable_da3f097b]], jsii.get(self, "settings"))

    @settings.setter
    def settings(
        self,
        value: typing.Optional[typing.Union["CfnCustomActionType.SettingsProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "settings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::CodePipeline::CustomActionType.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''``AWS::CodePipeline::CustomActionType.Version``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnCustomActionType.ArtifactDetailsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "maximum_count": "maximumCount",
            "minimum_count": "minimumCount",
        },
    )
    class ArtifactDetailsProperty:
        def __init__(
            self,
            *,
            maximum_count: jsii.Number,
            minimum_count: jsii.Number,
        ) -> None:
            '''
            :param maximum_count: ``CfnCustomActionType.ArtifactDetailsProperty.MaximumCount``.
            :param minimum_count: ``CfnCustomActionType.ArtifactDetailsProperty.MinimumCount``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                artifact_details_property = codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                    maximum_count=123,
                    minimum_count=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "maximum_count": maximum_count,
                "minimum_count": minimum_count,
            }

        @builtins.property
        def maximum_count(self) -> jsii.Number:
            '''``CfnCustomActionType.ArtifactDetailsProperty.MaximumCount``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-maximumcount
            '''
            result = self._values.get("maximum_count")
            assert result is not None, "Required property 'maximum_count' is missing"
            return typing.cast(jsii.Number, result)

        @builtins.property
        def minimum_count(self) -> jsii.Number:
            '''``CfnCustomActionType.ArtifactDetailsProperty.MinimumCount``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-artifactdetails.html#cfn-codepipeline-customactiontype-artifactdetails-minimumcount
            '''
            result = self._values.get("minimum_count")
            assert result is not None, "Required property 'minimum_count' is missing"
            return typing.cast(jsii.Number, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactDetailsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={
            "description": "description",
            "key": "key",
            "name": "name",
            "queryable": "queryable",
            "required": "required",
            "secret": "secret",
            "type": "type",
        },
    )
    class ConfigurationPropertiesProperty:
        def __init__(
            self,
            *,
            description: typing.Optional[builtins.str] = None,
            key: typing.Union[builtins.bool, _IResolvable_da3f097b],
            name: builtins.str,
            queryable: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
            required: typing.Union[builtins.bool, _IResolvable_da3f097b],
            secret: typing.Union[builtins.bool, _IResolvable_da3f097b],
            type: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param description: ``CfnCustomActionType.ConfigurationPropertiesProperty.Description``.
            :param key: ``CfnCustomActionType.ConfigurationPropertiesProperty.Key``.
            :param name: ``CfnCustomActionType.ConfigurationPropertiesProperty.Name``.
            :param queryable: ``CfnCustomActionType.ConfigurationPropertiesProperty.Queryable``.
            :param required: ``CfnCustomActionType.ConfigurationPropertiesProperty.Required``.
            :param secret: ``CfnCustomActionType.ConfigurationPropertiesProperty.Secret``.
            :param type: ``CfnCustomActionType.ConfigurationPropertiesProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                configuration_properties_property = codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty(
                    key=False,
                    name="name",
                    required=False,
                    secret=False,
                
                    # the properties below are optional
                    description="description",
                    queryable=False,
                    type="type"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "key": key,
                "name": name,
                "required": required,
                "secret": secret,
            }
            if description is not None:
                self._values["description"] = description
            if queryable is not None:
                self._values["queryable"] = queryable
            if type is not None:
                self._values["type"] = type

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Description``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-description
            '''
            result = self._values.get("description")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def key(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Key``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-key
            '''
            result = self._values.get("key")
            assert result is not None, "Required property 'key' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def queryable(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Queryable``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-queryable
            '''
            result = self._values.get("queryable")
            return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

        @builtins.property
        def required(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Required``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-required
            '''
            result = self._values.get("required")
            assert result is not None, "Required property 'required' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def secret(self) -> typing.Union[builtins.bool, _IResolvable_da3f097b]:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Secret``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-secret
            '''
            result = self._values.get("secret")
            assert result is not None, "Required property 'secret' is missing"
            return typing.cast(typing.Union[builtins.bool, _IResolvable_da3f097b], result)

        @builtins.property
        def type(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomActionType.ConfigurationPropertiesProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-type
            '''
            result = self._values.get("type")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConfigurationPropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnCustomActionType.SettingsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "entity_url_template": "entityUrlTemplate",
            "execution_url_template": "executionUrlTemplate",
            "revision_url_template": "revisionUrlTemplate",
            "third_party_configuration_url": "thirdPartyConfigurationUrl",
        },
    )
    class SettingsProperty:
        def __init__(
            self,
            *,
            entity_url_template: typing.Optional[builtins.str] = None,
            execution_url_template: typing.Optional[builtins.str] = None,
            revision_url_template: typing.Optional[builtins.str] = None,
            third_party_configuration_url: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param entity_url_template: ``CfnCustomActionType.SettingsProperty.EntityUrlTemplate``.
            :param execution_url_template: ``CfnCustomActionType.SettingsProperty.ExecutionUrlTemplate``.
            :param revision_url_template: ``CfnCustomActionType.SettingsProperty.RevisionUrlTemplate``.
            :param third_party_configuration_url: ``CfnCustomActionType.SettingsProperty.ThirdPartyConfigurationUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                settings_property = codepipeline.CfnCustomActionType.SettingsProperty(
                    entity_url_template="entityUrlTemplate",
                    execution_url_template="executionUrlTemplate",
                    revision_url_template="revisionUrlTemplate",
                    third_party_configuration_url="thirdPartyConfigurationUrl"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if entity_url_template is not None:
                self._values["entity_url_template"] = entity_url_template
            if execution_url_template is not None:
                self._values["execution_url_template"] = execution_url_template
            if revision_url_template is not None:
                self._values["revision_url_template"] = revision_url_template
            if third_party_configuration_url is not None:
                self._values["third_party_configuration_url"] = third_party_configuration_url

        @builtins.property
        def entity_url_template(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomActionType.SettingsProperty.EntityUrlTemplate``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-entityurltemplate
            '''
            result = self._values.get("entity_url_template")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def execution_url_template(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomActionType.SettingsProperty.ExecutionUrlTemplate``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-executionurltemplate
            '''
            result = self._values.get("execution_url_template")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def revision_url_template(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomActionType.SettingsProperty.RevisionUrlTemplate``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-revisionurltemplate
            '''
            result = self._values.get("revision_url_template")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def third_party_configuration_url(self) -> typing.Optional[builtins.str]:
            '''``CfnCustomActionType.SettingsProperty.ThirdPartyConfigurationUrl``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-customactiontype-settings.html#cfn-codepipeline-customactiontype-settings-thirdpartyconfigurationurl
            '''
            result = self._values.get("third_party_configuration_url")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SettingsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CfnCustomActionTypeProps",
    jsii_struct_bases=[],
    name_mapping={
        "category": "category",
        "configuration_properties": "configurationProperties",
        "input_artifact_details": "inputArtifactDetails",
        "output_artifact_details": "outputArtifactDetails",
        "provider": "provider",
        "settings": "settings",
        "tags": "tags",
        "version": "version",
    },
)
class CfnCustomActionTypeProps:
    def __init__(
        self,
        *,
        category: builtins.str,
        configuration_properties: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnCustomActionType.ConfigurationPropertiesProperty, _IResolvable_da3f097b]]]] = None,
        input_artifact_details: typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _IResolvable_da3f097b],
        output_artifact_details: typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _IResolvable_da3f097b],
        provider: builtins.str,
        settings: typing.Optional[typing.Union[CfnCustomActionType.SettingsProperty, _IResolvable_da3f097b]] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
        version: builtins.str,
    ) -> None:
        '''Properties for defining a ``AWS::CodePipeline::CustomActionType``.

        :param category: ``AWS::CodePipeline::CustomActionType.Category``.
        :param configuration_properties: ``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.
        :param input_artifact_details: ``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.
        :param output_artifact_details: ``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.
        :param provider: ``AWS::CodePipeline::CustomActionType.Provider``.
        :param settings: ``AWS::CodePipeline::CustomActionType.Settings``.
        :param tags: ``AWS::CodePipeline::CustomActionType.Tags``.
        :param version: ``AWS::CodePipeline::CustomActionType.Version``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            cfn_custom_action_type_props = codepipeline.CfnCustomActionTypeProps(
                category="category",
                input_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                    maximum_count=123,
                    minimum_count=123
                ),
                output_artifact_details=codepipeline.CfnCustomActionType.ArtifactDetailsProperty(
                    maximum_count=123,
                    minimum_count=123
                ),
                provider="provider",
                version="version",
            
                # the properties below are optional
                configuration_properties=[codepipeline.CfnCustomActionType.ConfigurationPropertiesProperty(
                    key=False,
                    name="name",
                    required=False,
                    secret=False,
            
                    # the properties below are optional
                    description="description",
                    queryable=False,
                    type="type"
                )],
                settings=codepipeline.CfnCustomActionType.SettingsProperty(
                    entity_url_template="entityUrlTemplate",
                    execution_url_template="executionUrlTemplate",
                    revision_url_template="revisionUrlTemplate",
                    third_party_configuration_url="thirdPartyConfigurationUrl"
                ),
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "category": category,
            "input_artifact_details": input_artifact_details,
            "output_artifact_details": output_artifact_details,
            "provider": provider,
            "version": version,
        }
        if configuration_properties is not None:
            self._values["configuration_properties"] = configuration_properties
        if settings is not None:
            self._values["settings"] = settings
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def category(self) -> builtins.str:
        '''``AWS::CodePipeline::CustomActionType.Category``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-category
        '''
        result = self._values.get("category")
        assert result is not None, "Required property 'category' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def configuration_properties(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnCustomActionType.ConfigurationPropertiesProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::CodePipeline::CustomActionType.ConfigurationProperties``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-configurationproperties
        '''
        result = self._values.get("configuration_properties")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnCustomActionType.ConfigurationPropertiesProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def input_artifact_details(
        self,
    ) -> typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _IResolvable_da3f097b]:
        '''``AWS::CodePipeline::CustomActionType.InputArtifactDetails``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-inputartifactdetails
        '''
        result = self._values.get("input_artifact_details")
        assert result is not None, "Required property 'input_artifact_details' is missing"
        return typing.cast(typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def output_artifact_details(
        self,
    ) -> typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _IResolvable_da3f097b]:
        '''``AWS::CodePipeline::CustomActionType.OutputArtifactDetails``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-outputartifactdetails
        '''
        result = self._values.get("output_artifact_details")
        assert result is not None, "Required property 'output_artifact_details' is missing"
        return typing.cast(typing.Union[CfnCustomActionType.ArtifactDetailsProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''``AWS::CodePipeline::CustomActionType.Provider``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-provider
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def settings(
        self,
    ) -> typing.Optional[typing.Union[CfnCustomActionType.SettingsProperty, _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::CustomActionType.Settings``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-settings
        '''
        result = self._values.get("settings")
        return typing.cast(typing.Optional[typing.Union[CfnCustomActionType.SettingsProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::CodePipeline::CustomActionType.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    @builtins.property
    def version(self) -> builtins.str:
        '''``AWS::CodePipeline::CustomActionType.Version``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype.html#cfn-codepipeline-customactiontype-version
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnCustomActionTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnPipeline(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline",
):
    '''A CloudFormation ``AWS::CodePipeline::Pipeline``.

    :cloudformationResource: AWS::CodePipeline::Pipeline
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_codepipeline as codepipeline
        
        # configuration is of type object
        
        cfn_pipeline = codepipeline.CfnPipeline(self, "MyCfnPipeline",
            role_arn="roleArn",
            stages=[codepipeline.CfnPipeline.StageDeclarationProperty(
                actions=[codepipeline.CfnPipeline.ActionDeclarationProperty(
                    action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                        category="category",
                        owner="owner",
                        provider="provider",
                        version="version"
                    ),
                    name="name",
        
                    # the properties below are optional
                    configuration=configuration,
                    input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                        name="name"
                    )],
                    namespace="namespace",
                    output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                        name="name"
                    )],
                    region="region",
                    role_arn="roleArn",
                    run_order=123
                )],
                name="name",
        
                # the properties below are optional
                blockers=[codepipeline.CfnPipeline.BlockerDeclarationProperty(
                    name="name",
                    type="type"
                )]
            )],
        
            # the properties below are optional
            artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                location="location",
                type="type",
        
                # the properties below are optional
                encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                    id="id",
                    type="type"
                )
            ),
            artifact_stores=[codepipeline.CfnPipeline.ArtifactStoreMapProperty(
                artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                    location="location",
                    type="type",
        
                    # the properties below are optional
                    encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                        id="id",
                        type="type"
                    )
                ),
                region="region"
            )],
            disable_inbound_stage_transitions=[codepipeline.CfnPipeline.StageTransitionProperty(
                reason="reason",
                stage_name="stageName"
            )],
            name="name",
            restart_execution_on_update=False,
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
        artifact_store: typing.Optional[typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b]] = None,
        artifact_stores: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.ArtifactStoreMapProperty", _IResolvable_da3f097b]]]] = None,
        disable_inbound_stage_transitions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.StageTransitionProperty", _IResolvable_da3f097b]]]] = None,
        name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        role_arn: builtins.str,
        stages: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.StageDeclarationProperty", _IResolvable_da3f097b]]],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Create a new ``AWS::CodePipeline::Pipeline``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param artifact_store: ``AWS::CodePipeline::Pipeline.ArtifactStore``.
        :param artifact_stores: ``AWS::CodePipeline::Pipeline.ArtifactStores``.
        :param disable_inbound_stage_transitions: ``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.
        :param name: ``AWS::CodePipeline::Pipeline.Name``.
        :param restart_execution_on_update: ``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.
        :param role_arn: ``AWS::CodePipeline::Pipeline.RoleArn``.
        :param stages: ``AWS::CodePipeline::Pipeline.Stages``.
        :param tags: ``AWS::CodePipeline::Pipeline.Tags``.
        '''
        props = CfnPipelineProps(
            artifact_store=artifact_store,
            artifact_stores=artifact_stores,
            disable_inbound_stage_transitions=disable_inbound_stage_transitions,
            name=name,
            restart_execution_on_update=restart_execution_on_update,
            role_arn=role_arn,
            stages=stages,
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
    @jsii.member(jsii_name="artifactStore")
    def artifact_store(
        self,
    ) -> typing.Optional[typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::Pipeline.ArtifactStore``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
        '''
        return typing.cast(typing.Optional[typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b]], jsii.get(self, "artifactStore"))

    @artifact_store.setter
    def artifact_store(
        self,
        value: typing.Optional[typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "artifactStore", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactStores")
    def artifact_stores(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.ArtifactStoreMapProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::CodePipeline::Pipeline.ArtifactStores``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.ArtifactStoreMapProperty", _IResolvable_da3f097b]]]], jsii.get(self, "artifactStores"))

    @artifact_stores.setter
    def artifact_stores(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.ArtifactStoreMapProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "artifactStores", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrVersion")
    def attr_version(self) -> builtins.str:
        '''
        :cloudformationAttribute: Version
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrVersion"))

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
    @jsii.member(jsii_name="disableInboundStageTransitions")
    def disable_inbound_stage_transitions(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.StageTransitionProperty", _IResolvable_da3f097b]]]]:
        '''``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.StageTransitionProperty", _IResolvable_da3f097b]]]], jsii.get(self, "disableInboundStageTransitions"))

    @disable_inbound_stage_transitions.setter
    def disable_inbound_stage_transitions(
        self,
        value: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.StageTransitionProperty", _IResolvable_da3f097b]]]],
    ) -> None:
        jsii.set(self, "disableInboundStageTransitions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodePipeline::Pipeline.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartExecutionOnUpdate")
    def restart_execution_on_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "restartExecutionOnUpdate"))

    @restart_execution_on_update.setter
    def restart_execution_on_update(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "restartExecutionOnUpdate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''``AWS::CodePipeline::Pipeline.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stages")
    def stages(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.StageDeclarationProperty", _IResolvable_da3f097b]]]:
        '''``AWS::CodePipeline::Pipeline.Stages``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.StageDeclarationProperty", _IResolvable_da3f097b]]], jsii.get(self, "stages"))

    @stages.setter
    def stages(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.StageDeclarationProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "stages", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0a598cb3:
        '''``AWS::CodePipeline::Pipeline.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-tags
        '''
        return typing.cast(_TagManager_0a598cb3, jsii.get(self, "tags"))

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.ActionDeclarationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "action_type_id": "actionTypeId",
            "configuration": "configuration",
            "input_artifacts": "inputArtifacts",
            "name": "name",
            "namespace": "namespace",
            "output_artifacts": "outputArtifacts",
            "region": "region",
            "role_arn": "roleArn",
            "run_order": "runOrder",
        },
    )
    class ActionDeclarationProperty:
        def __init__(
            self,
            *,
            action_type_id: typing.Union["CfnPipeline.ActionTypeIdProperty", _IResolvable_da3f097b],
            configuration: typing.Any = None,
            input_artifacts: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.InputArtifactProperty", _IResolvable_da3f097b]]]] = None,
            name: builtins.str,
            namespace: typing.Optional[builtins.str] = None,
            output_artifacts: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.OutputArtifactProperty", _IResolvable_da3f097b]]]] = None,
            region: typing.Optional[builtins.str] = None,
            role_arn: typing.Optional[builtins.str] = None,
            run_order: typing.Optional[jsii.Number] = None,
        ) -> None:
            '''
            :param action_type_id: ``CfnPipeline.ActionDeclarationProperty.ActionTypeId``.
            :param configuration: ``CfnPipeline.ActionDeclarationProperty.Configuration``.
            :param input_artifacts: ``CfnPipeline.ActionDeclarationProperty.InputArtifacts``.
            :param name: ``CfnPipeline.ActionDeclarationProperty.Name``.
            :param namespace: ``CfnPipeline.ActionDeclarationProperty.Namespace``.
            :param output_artifacts: ``CfnPipeline.ActionDeclarationProperty.OutputArtifacts``.
            :param region: ``CfnPipeline.ActionDeclarationProperty.Region``.
            :param role_arn: ``CfnPipeline.ActionDeclarationProperty.RoleArn``.
            :param run_order: ``CfnPipeline.ActionDeclarationProperty.RunOrder``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                # configuration is of type object
                
                action_declaration_property = codepipeline.CfnPipeline.ActionDeclarationProperty(
                    action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                        category="category",
                        owner="owner",
                        provider="provider",
                        version="version"
                    ),
                    name="name",
                
                    # the properties below are optional
                    configuration=configuration,
                    input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                        name="name"
                    )],
                    namespace="namespace",
                    output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                        name="name"
                    )],
                    region="region",
                    role_arn="roleArn",
                    run_order=123
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "action_type_id": action_type_id,
                "name": name,
            }
            if configuration is not None:
                self._values["configuration"] = configuration
            if input_artifacts is not None:
                self._values["input_artifacts"] = input_artifacts
            if namespace is not None:
                self._values["namespace"] = namespace
            if output_artifacts is not None:
                self._values["output_artifacts"] = output_artifacts
            if region is not None:
                self._values["region"] = region
            if role_arn is not None:
                self._values["role_arn"] = role_arn
            if run_order is not None:
                self._values["run_order"] = run_order

        @builtins.property
        def action_type_id(
            self,
        ) -> typing.Union["CfnPipeline.ActionTypeIdProperty", _IResolvable_da3f097b]:
            '''``CfnPipeline.ActionDeclarationProperty.ActionTypeId``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid
            '''
            result = self._values.get("action_type_id")
            assert result is not None, "Required property 'action_type_id' is missing"
            return typing.cast(typing.Union["CfnPipeline.ActionTypeIdProperty", _IResolvable_da3f097b], result)

        @builtins.property
        def configuration(self) -> typing.Any:
            '''``CfnPipeline.ActionDeclarationProperty.Configuration``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-configuration
            '''
            result = self._values.get("configuration")
            return typing.cast(typing.Any, result)

        @builtins.property
        def input_artifacts(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.InputArtifactProperty", _IResolvable_da3f097b]]]]:
            '''``CfnPipeline.ActionDeclarationProperty.InputArtifacts``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts
            '''
            result = self._values.get("input_artifacts")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.InputArtifactProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnPipeline.ActionDeclarationProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def namespace(self) -> typing.Optional[builtins.str]:
            '''``CfnPipeline.ActionDeclarationProperty.Namespace``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-actiondeclaration-namespace
            '''
            result = self._values.get("namespace")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def output_artifacts(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.OutputArtifactProperty", _IResolvable_da3f097b]]]]:
            '''``CfnPipeline.ActionDeclarationProperty.OutputArtifacts``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts
            '''
            result = self._values.get("output_artifacts")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.OutputArtifactProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def region(self) -> typing.Optional[builtins.str]:
            '''``CfnPipeline.ActionDeclarationProperty.Region``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-region
            '''
            result = self._values.get("region")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def role_arn(self) -> typing.Optional[builtins.str]:
            '''``CfnPipeline.ActionDeclarationProperty.RoleArn``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-rolearn
            '''
            result = self._values.get("role_arn")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def run_order(self) -> typing.Optional[jsii.Number]:
            '''``CfnPipeline.ActionDeclarationProperty.RunOrder``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html#cfn-codepipeline-pipeline-stages-actions-runorder
            '''
            result = self._values.get("run_order")
            return typing.cast(typing.Optional[jsii.Number], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionDeclarationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.ActionTypeIdProperty",
        jsii_struct_bases=[],
        name_mapping={
            "category": "category",
            "owner": "owner",
            "provider": "provider",
            "version": "version",
        },
    )
    class ActionTypeIdProperty:
        def __init__(
            self,
            *,
            category: builtins.str,
            owner: builtins.str,
            provider: builtins.str,
            version: builtins.str,
        ) -> None:
            '''
            :param category: ``CfnPipeline.ActionTypeIdProperty.Category``.
            :param owner: ``CfnPipeline.ActionTypeIdProperty.Owner``.
            :param provider: ``CfnPipeline.ActionTypeIdProperty.Provider``.
            :param version: ``CfnPipeline.ActionTypeIdProperty.Version``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                action_type_id_property = codepipeline.CfnPipeline.ActionTypeIdProperty(
                    category="category",
                    owner="owner",
                    provider="provider",
                    version="version"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "category": category,
                "owner": owner,
                "provider": provider,
                "version": version,
            }

        @builtins.property
        def category(self) -> builtins.str:
            '''``CfnPipeline.ActionTypeIdProperty.Category``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-category
            '''
            result = self._values.get("category")
            assert result is not None, "Required property 'category' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def owner(self) -> builtins.str:
            '''``CfnPipeline.ActionTypeIdProperty.Owner``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-owner
            '''
            result = self._values.get("owner")
            assert result is not None, "Required property 'owner' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def provider(self) -> builtins.str:
            '''``CfnPipeline.ActionTypeIdProperty.Provider``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-provider
            '''
            result = self._values.get("provider")
            assert result is not None, "Required property 'provider' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def version(self) -> builtins.str:
            '''``CfnPipeline.ActionTypeIdProperty.Version``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-actiontypeid.html#cfn-codepipeline-pipeline-stages-actions-actiontypeid-version
            '''
            result = self._values.get("version")
            assert result is not None, "Required property 'version' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ActionTypeIdProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.ArtifactStoreMapProperty",
        jsii_struct_bases=[],
        name_mapping={"artifact_store": "artifactStore", "region": "region"},
    )
    class ArtifactStoreMapProperty:
        def __init__(
            self,
            *,
            artifact_store: typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b],
            region: builtins.str,
        ) -> None:
            '''
            :param artifact_store: ``CfnPipeline.ArtifactStoreMapProperty.ArtifactStore``.
            :param region: ``CfnPipeline.ArtifactStoreMapProperty.Region``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                artifact_store_map_property = codepipeline.CfnPipeline.ArtifactStoreMapProperty(
                    artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                        location="location",
                        type="type",
                
                        # the properties below are optional
                        encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                            id="id",
                            type="type"
                        )
                    ),
                    region="region"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "artifact_store": artifact_store,
                "region": region,
            }

        @builtins.property
        def artifact_store(
            self,
        ) -> typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b]:
            '''``CfnPipeline.ArtifactStoreMapProperty.ArtifactStore``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-artifactstore
            '''
            result = self._values.get("artifact_store")
            assert result is not None, "Required property 'artifact_store' is missing"
            return typing.cast(typing.Union["CfnPipeline.ArtifactStoreProperty", _IResolvable_da3f097b], result)

        @builtins.property
        def region(self) -> builtins.str:
            '''``CfnPipeline.ArtifactStoreMapProperty.Region``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstoremap.html#cfn-codepipeline-pipeline-artifactstoremap-region
            '''
            result = self._values.get("region")
            assert result is not None, "Required property 'region' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactStoreMapProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.ArtifactStoreProperty",
        jsii_struct_bases=[],
        name_mapping={
            "encryption_key": "encryptionKey",
            "location": "location",
            "type": "type",
        },
    )
    class ArtifactStoreProperty:
        def __init__(
            self,
            *,
            encryption_key: typing.Optional[typing.Union["CfnPipeline.EncryptionKeyProperty", _IResolvable_da3f097b]] = None,
            location: builtins.str,
            type: builtins.str,
        ) -> None:
            '''
            :param encryption_key: ``CfnPipeline.ArtifactStoreProperty.EncryptionKey``.
            :param location: ``CfnPipeline.ArtifactStoreProperty.Location``.
            :param type: ``CfnPipeline.ArtifactStoreProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                artifact_store_property = codepipeline.CfnPipeline.ArtifactStoreProperty(
                    location="location",
                    type="type",
                
                    # the properties below are optional
                    encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                        id="id",
                        type="type"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "location": location,
                "type": type,
            }
            if encryption_key is not None:
                self._values["encryption_key"] = encryption_key

        @builtins.property
        def encryption_key(
            self,
        ) -> typing.Optional[typing.Union["CfnPipeline.EncryptionKeyProperty", _IResolvable_da3f097b]]:
            '''``CfnPipeline.ArtifactStoreProperty.EncryptionKey``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey
            '''
            result = self._values.get("encryption_key")
            return typing.cast(typing.Optional[typing.Union["CfnPipeline.EncryptionKeyProperty", _IResolvable_da3f097b]], result)

        @builtins.property
        def location(self) -> builtins.str:
            '''``CfnPipeline.ArtifactStoreProperty.Location``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-location
            '''
            result = self._values.get("location")
            assert result is not None, "Required property 'location' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnPipeline.ArtifactStoreProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore.html#cfn-codepipeline-pipeline-artifactstore-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ArtifactStoreProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.BlockerDeclarationProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name", "type": "type"},
    )
    class BlockerDeclarationProperty:
        def __init__(self, *, name: builtins.str, type: builtins.str) -> None:
            '''
            :param name: ``CfnPipeline.BlockerDeclarationProperty.Name``.
            :param type: ``CfnPipeline.BlockerDeclarationProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                blocker_declaration_property = codepipeline.CfnPipeline.BlockerDeclarationProperty(
                    name="name",
                    type="type"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
                "type": type,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnPipeline.BlockerDeclarationProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnPipeline.BlockerDeclarationProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-blockers.html#cfn-codepipeline-pipeline-stages-blockers-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "BlockerDeclarationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.EncryptionKeyProperty",
        jsii_struct_bases=[],
        name_mapping={"id": "id", "type": "type"},
    )
    class EncryptionKeyProperty:
        def __init__(self, *, id: builtins.str, type: builtins.str) -> None:
            '''
            :param id: ``CfnPipeline.EncryptionKeyProperty.Id``.
            :param type: ``CfnPipeline.EncryptionKeyProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                encryption_key_property = codepipeline.CfnPipeline.EncryptionKeyProperty(
                    id="id",
                    type="type"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "id": id,
                "type": type,
            }

        @builtins.property
        def id(self) -> builtins.str:
            '''``CfnPipeline.EncryptionKeyProperty.Id``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-id
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def type(self) -> builtins.str:
            '''``CfnPipeline.EncryptionKeyProperty.Type``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-artifactstore-encryptionkey.html#cfn-codepipeline-pipeline-artifactstore-encryptionkey-type
            '''
            result = self._values.get("type")
            assert result is not None, "Required property 'type' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "EncryptionKeyProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.InputArtifactProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name"},
    )
    class InputArtifactProperty:
        def __init__(self, *, name: builtins.str) -> None:
            '''
            :param name: ``CfnPipeline.InputArtifactProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                input_artifact_property = codepipeline.CfnPipeline.InputArtifactProperty(
                    name="name"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnPipeline.InputArtifactProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-inputartifacts.html#cfn-codepipeline-pipeline-stages-actions-inputartifacts-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "InputArtifactProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.OutputArtifactProperty",
        jsii_struct_bases=[],
        name_mapping={"name": "name"},
    )
    class OutputArtifactProperty:
        def __init__(self, *, name: builtins.str) -> None:
            '''
            :param name: ``CfnPipeline.OutputArtifactProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                output_artifact_property = codepipeline.CfnPipeline.OutputArtifactProperty(
                    name="name"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "name": name,
            }

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnPipeline.OutputArtifactProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions-outputartifacts.html#cfn-codepipeline-pipeline-stages-actions-outputartifacts-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OutputArtifactProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.StageDeclarationProperty",
        jsii_struct_bases=[],
        name_mapping={"actions": "actions", "blockers": "blockers", "name": "name"},
    )
    class StageDeclarationProperty:
        def __init__(
            self,
            *,
            actions: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.ActionDeclarationProperty", _IResolvable_da3f097b]]],
            blockers: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnPipeline.BlockerDeclarationProperty", _IResolvable_da3f097b]]]] = None,
            name: builtins.str,
        ) -> None:
            '''
            :param actions: ``CfnPipeline.StageDeclarationProperty.Actions``.
            :param blockers: ``CfnPipeline.StageDeclarationProperty.Blockers``.
            :param name: ``CfnPipeline.StageDeclarationProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                # configuration is of type object
                
                stage_declaration_property = codepipeline.CfnPipeline.StageDeclarationProperty(
                    actions=[codepipeline.CfnPipeline.ActionDeclarationProperty(
                        action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                            category="category",
                            owner="owner",
                            provider="provider",
                            version="version"
                        ),
                        name="name",
                
                        # the properties below are optional
                        configuration=configuration,
                        input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                            name="name"
                        )],
                        namespace="namespace",
                        output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                            name="name"
                        )],
                        region="region",
                        role_arn="roleArn",
                        run_order=123
                    )],
                    name="name",
                
                    # the properties below are optional
                    blockers=[codepipeline.CfnPipeline.BlockerDeclarationProperty(
                        name="name",
                        type="type"
                    )]
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "actions": actions,
                "name": name,
            }
            if blockers is not None:
                self._values["blockers"] = blockers

        @builtins.property
        def actions(
            self,
        ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.ActionDeclarationProperty", _IResolvable_da3f097b]]]:
            '''``CfnPipeline.StageDeclarationProperty.Actions``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-actions
            '''
            result = self._values.get("actions")
            assert result is not None, "Required property 'actions' is missing"
            return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.ActionDeclarationProperty", _IResolvable_da3f097b]]], result)

        @builtins.property
        def blockers(
            self,
        ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.BlockerDeclarationProperty", _IResolvable_da3f097b]]]]:
            '''``CfnPipeline.StageDeclarationProperty.Blockers``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-blockers
            '''
            result = self._values.get("blockers")
            return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnPipeline.BlockerDeclarationProperty", _IResolvable_da3f097b]]]], result)

        @builtins.property
        def name(self) -> builtins.str:
            '''``CfnPipeline.StageDeclarationProperty.Name``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html#cfn-codepipeline-pipeline-stages-name
            '''
            result = self._values.get("name")
            assert result is not None, "Required property 'name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StageDeclarationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipeline.StageTransitionProperty",
        jsii_struct_bases=[],
        name_mapping={"reason": "reason", "stage_name": "stageName"},
    )
    class StageTransitionProperty:
        def __init__(self, *, reason: builtins.str, stage_name: builtins.str) -> None:
            '''
            :param reason: ``CfnPipeline.StageTransitionProperty.Reason``.
            :param stage_name: ``CfnPipeline.StageTransitionProperty.StageName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                stage_transition_property = codepipeline.CfnPipeline.StageTransitionProperty(
                    reason="reason",
                    stage_name="stageName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "reason": reason,
                "stage_name": stage_name,
            }

        @builtins.property
        def reason(self) -> builtins.str:
            '''``CfnPipeline.StageTransitionProperty.Reason``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-reason
            '''
            result = self._values.get("reason")
            assert result is not None, "Required property 'reason' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def stage_name(self) -> builtins.str:
            '''``CfnPipeline.StageTransitionProperty.StageName``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-disableinboundstagetransitions.html#cfn-codepipeline-pipeline-disableinboundstagetransitions-stagename
            '''
            result = self._values.get("stage_name")
            assert result is not None, "Required property 'stage_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StageTransitionProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CfnPipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_store": "artifactStore",
        "artifact_stores": "artifactStores",
        "disable_inbound_stage_transitions": "disableInboundStageTransitions",
        "name": "name",
        "restart_execution_on_update": "restartExecutionOnUpdate",
        "role_arn": "roleArn",
        "stages": "stages",
        "tags": "tags",
    },
)
class CfnPipelineProps:
    def __init__(
        self,
        *,
        artifact_store: typing.Optional[typing.Union[CfnPipeline.ArtifactStoreProperty, _IResolvable_da3f097b]] = None,
        artifact_stores: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnPipeline.ArtifactStoreMapProperty, _IResolvable_da3f097b]]]] = None,
        disable_inbound_stage_transitions: typing.Optional[typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnPipeline.StageTransitionProperty, _IResolvable_da3f097b]]]] = None,
        name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        role_arn: builtins.str,
        stages: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnPipeline.StageDeclarationProperty, _IResolvable_da3f097b]]],
        tags: typing.Optional[typing.Sequence[_CfnTag_f6864754]] = None,
    ) -> None:
        '''Properties for defining a ``AWS::CodePipeline::Pipeline``.

        :param artifact_store: ``AWS::CodePipeline::Pipeline.ArtifactStore``.
        :param artifact_stores: ``AWS::CodePipeline::Pipeline.ArtifactStores``.
        :param disable_inbound_stage_transitions: ``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.
        :param name: ``AWS::CodePipeline::Pipeline.Name``.
        :param restart_execution_on_update: ``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.
        :param role_arn: ``AWS::CodePipeline::Pipeline.RoleArn``.
        :param stages: ``AWS::CodePipeline::Pipeline.Stages``.
        :param tags: ``AWS::CodePipeline::Pipeline.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            # configuration is of type object
            
            cfn_pipeline_props = codepipeline.CfnPipelineProps(
                role_arn="roleArn",
                stages=[codepipeline.CfnPipeline.StageDeclarationProperty(
                    actions=[codepipeline.CfnPipeline.ActionDeclarationProperty(
                        action_type_id=codepipeline.CfnPipeline.ActionTypeIdProperty(
                            category="category",
                            owner="owner",
                            provider="provider",
                            version="version"
                        ),
                        name="name",
            
                        # the properties below are optional
                        configuration=configuration,
                        input_artifacts=[codepipeline.CfnPipeline.InputArtifactProperty(
                            name="name"
                        )],
                        namespace="namespace",
                        output_artifacts=[codepipeline.CfnPipeline.OutputArtifactProperty(
                            name="name"
                        )],
                        region="region",
                        role_arn="roleArn",
                        run_order=123
                    )],
                    name="name",
            
                    # the properties below are optional
                    blockers=[codepipeline.CfnPipeline.BlockerDeclarationProperty(
                        name="name",
                        type="type"
                    )]
                )],
            
                # the properties below are optional
                artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                    location="location",
                    type="type",
            
                    # the properties below are optional
                    encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                        id="id",
                        type="type"
                    )
                ),
                artifact_stores=[codepipeline.CfnPipeline.ArtifactStoreMapProperty(
                    artifact_store=codepipeline.CfnPipeline.ArtifactStoreProperty(
                        location="location",
                        type="type",
            
                        # the properties below are optional
                        encryption_key=codepipeline.CfnPipeline.EncryptionKeyProperty(
                            id="id",
                            type="type"
                        )
                    ),
                    region="region"
                )],
                disable_inbound_stage_transitions=[codepipeline.CfnPipeline.StageTransitionProperty(
                    reason="reason",
                    stage_name="stageName"
                )],
                name="name",
                restart_execution_on_update=False,
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "stages": stages,
        }
        if artifact_store is not None:
            self._values["artifact_store"] = artifact_store
        if artifact_stores is not None:
            self._values["artifact_stores"] = artifact_stores
        if disable_inbound_stage_transitions is not None:
            self._values["disable_inbound_stage_transitions"] = disable_inbound_stage_transitions
        if name is not None:
            self._values["name"] = name
        if restart_execution_on_update is not None:
            self._values["restart_execution_on_update"] = restart_execution_on_update
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def artifact_store(
        self,
    ) -> typing.Optional[typing.Union[CfnPipeline.ArtifactStoreProperty, _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::Pipeline.ArtifactStore``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstore
        '''
        result = self._values.get("artifact_store")
        return typing.cast(typing.Optional[typing.Union[CfnPipeline.ArtifactStoreProperty, _IResolvable_da3f097b]], result)

    @builtins.property
    def artifact_stores(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnPipeline.ArtifactStoreMapProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::CodePipeline::Pipeline.ArtifactStores``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-artifactstores
        '''
        result = self._values.get("artifact_stores")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnPipeline.ArtifactStoreMapProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def disable_inbound_stage_transitions(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnPipeline.StageTransitionProperty, _IResolvable_da3f097b]]]]:
        '''``AWS::CodePipeline::Pipeline.DisableInboundStageTransitions``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-disableinboundstagetransitions
        '''
        result = self._values.get("disable_inbound_stage_transitions")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnPipeline.StageTransitionProperty, _IResolvable_da3f097b]]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodePipeline::Pipeline.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restart_execution_on_update(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::Pipeline.RestartExecutionOnUpdate``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-restartexecutiononupdate
        '''
        result = self._values.get("restart_execution_on_update")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''``AWS::CodePipeline::Pipeline.RoleArn``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stages(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnPipeline.StageDeclarationProperty, _IResolvable_da3f097b]]]:
        '''``AWS::CodePipeline::Pipeline.Stages``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-stages
        '''
        result = self._values.get("stages")
        assert result is not None, "Required property 'stages' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnPipeline.StageDeclarationProperty, _IResolvable_da3f097b]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_f6864754]]:
        '''``AWS::CodePipeline::Pipeline.Tags``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html#cfn-codepipeline-pipeline-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_f6864754]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IInspectable_c2943556)
class CfnWebhook(
    _CfnResource_9df397a6,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.CfnWebhook",
):
    '''A CloudFormation ``AWS::CodePipeline::Webhook``.

    :cloudformationResource: AWS::CodePipeline::Webhook
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from aws_cdk import aws_codepipeline as codepipeline
        
        cfn_webhook = codepipeline.CfnWebhook(self, "MyCfnWebhook",
            authentication="authentication",
            authentication_configuration=codepipeline.CfnWebhook.WebhookAuthConfigurationProperty(
                allowed_ip_range="allowedIpRange",
                secret_token="secretToken"
            ),
            filters=[codepipeline.CfnWebhook.WebhookFilterRuleProperty(
                json_path="jsonPath",
        
                # the properties below are optional
                match_equals="matchEquals"
            )],
            target_action="targetAction",
            target_pipeline="targetPipeline",
            target_pipeline_version=123,
        
            # the properties below are optional
            name="name",
            register_with_third_party=False
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authentication: builtins.str,
        authentication_configuration: typing.Union["CfnWebhook.WebhookAuthConfigurationProperty", _IResolvable_da3f097b],
        filters: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union["CfnWebhook.WebhookFilterRuleProperty", _IResolvable_da3f097b]]],
        name: typing.Optional[builtins.str] = None,
        register_with_third_party: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        target_action: builtins.str,
        target_pipeline: builtins.str,
        target_pipeline_version: jsii.Number,
    ) -> None:
        '''Create a new ``AWS::CodePipeline::Webhook``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authentication: ``AWS::CodePipeline::Webhook.Authentication``.
        :param authentication_configuration: ``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.
        :param filters: ``AWS::CodePipeline::Webhook.Filters``.
        :param name: ``AWS::CodePipeline::Webhook.Name``.
        :param register_with_third_party: ``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.
        :param target_action: ``AWS::CodePipeline::Webhook.TargetAction``.
        :param target_pipeline: ``AWS::CodePipeline::Webhook.TargetPipeline``.
        :param target_pipeline_version: ``AWS::CodePipeline::Webhook.TargetPipelineVersion``.
        '''
        props = CfnWebhookProps(
            authentication=authentication,
            authentication_configuration=authentication_configuration,
            filters=filters,
            name=name,
            register_with_third_party=register_with_third_party,
            target_action=target_action,
            target_pipeline=target_pipeline,
            target_pipeline_version=target_pipeline_version,
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
    @jsii.member(jsii_name="attrUrl")
    def attr_url(self) -> builtins.str:
        '''
        :cloudformationAttribute: Url
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> builtins.str:
        '''``AWS::CodePipeline::Webhook.Authentication``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
        '''
        return typing.cast(builtins.str, jsii.get(self, "authentication"))

    @authentication.setter
    def authentication(self, value: builtins.str) -> None:
        jsii.set(self, "authentication", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationConfiguration")
    def authentication_configuration(
        self,
    ) -> typing.Union["CfnWebhook.WebhookAuthConfigurationProperty", _IResolvable_da3f097b]:
        '''``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
        '''
        return typing.cast(typing.Union["CfnWebhook.WebhookAuthConfigurationProperty", _IResolvable_da3f097b], jsii.get(self, "authenticationConfiguration"))

    @authentication_configuration.setter
    def authentication_configuration(
        self,
        value: typing.Union["CfnWebhook.WebhookAuthConfigurationProperty", _IResolvable_da3f097b],
    ) -> None:
        jsii.set(self, "authenticationConfiguration", value)

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
    @jsii.member(jsii_name="filters")
    def filters(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnWebhook.WebhookFilterRuleProperty", _IResolvable_da3f097b]]]:
        '''``AWS::CodePipeline::Webhook.Filters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
        '''
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnWebhook.WebhookFilterRuleProperty", _IResolvable_da3f097b]]], jsii.get(self, "filters"))

    @filters.setter
    def filters(
        self,
        value: typing.Union[_IResolvable_da3f097b, typing.List[typing.Union["CfnWebhook.WebhookFilterRuleProperty", _IResolvable_da3f097b]]],
    ) -> None:
        jsii.set(self, "filters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodePipeline::Webhook.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registerWithThirdParty")
    def register_with_third_party(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], jsii.get(self, "registerWithThirdParty"))

    @register_with_third_party.setter
    def register_with_third_party(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]],
    ) -> None:
        jsii.set(self, "registerWithThirdParty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetAction")
    def target_action(self) -> builtins.str:
        '''``AWS::CodePipeline::Webhook.TargetAction``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetAction"))

    @target_action.setter
    def target_action(self, value: builtins.str) -> None:
        jsii.set(self, "targetAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetPipeline")
    def target_pipeline(self) -> builtins.str:
        '''``AWS::CodePipeline::Webhook.TargetPipeline``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
        '''
        return typing.cast(builtins.str, jsii.get(self, "targetPipeline"))

    @target_pipeline.setter
    def target_pipeline(self, value: builtins.str) -> None:
        jsii.set(self, "targetPipeline", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetPipelineVersion")
    def target_pipeline_version(self) -> jsii.Number:
        '''``AWS::CodePipeline::Webhook.TargetPipelineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
        '''
        return typing.cast(jsii.Number, jsii.get(self, "targetPipelineVersion"))

    @target_pipeline_version.setter
    def target_pipeline_version(self, value: jsii.Number) -> None:
        jsii.set(self, "targetPipelineVersion", value)

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnWebhook.WebhookAuthConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={
            "allowed_ip_range": "allowedIpRange",
            "secret_token": "secretToken",
        },
    )
    class WebhookAuthConfigurationProperty:
        def __init__(
            self,
            *,
            allowed_ip_range: typing.Optional[builtins.str] = None,
            secret_token: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param allowed_ip_range: ``CfnWebhook.WebhookAuthConfigurationProperty.AllowedIPRange``.
            :param secret_token: ``CfnWebhook.WebhookAuthConfigurationProperty.SecretToken``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                webhook_auth_configuration_property = codepipeline.CfnWebhook.WebhookAuthConfigurationProperty(
                    allowed_ip_range="allowedIpRange",
                    secret_token="secretToken"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {}
            if allowed_ip_range is not None:
                self._values["allowed_ip_range"] = allowed_ip_range
            if secret_token is not None:
                self._values["secret_token"] = secret_token

        @builtins.property
        def allowed_ip_range(self) -> typing.Optional[builtins.str]:
            '''``CfnWebhook.WebhookAuthConfigurationProperty.AllowedIPRange``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-allowediprange
            '''
            result = self._values.get("allowed_ip_range")
            return typing.cast(typing.Optional[builtins.str], result)

        @builtins.property
        def secret_token(self) -> typing.Optional[builtins.str]:
            '''``CfnWebhook.WebhookAuthConfigurationProperty.SecretToken``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookauthconfiguration.html#cfn-codepipeline-webhook-webhookauthconfiguration-secrettoken
            '''
            result = self._values.get("secret_token")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WebhookAuthConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="aws-cdk-lib.aws_codepipeline.CfnWebhook.WebhookFilterRuleProperty",
        jsii_struct_bases=[],
        name_mapping={"json_path": "jsonPath", "match_equals": "matchEquals"},
    )
    class WebhookFilterRuleProperty:
        def __init__(
            self,
            *,
            json_path: builtins.str,
            match_equals: typing.Optional[builtins.str] = None,
        ) -> None:
            '''
            :param json_path: ``CfnWebhook.WebhookFilterRuleProperty.JsonPath``.
            :param match_equals: ``CfnWebhook.WebhookFilterRuleProperty.MatchEquals``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from aws_cdk import aws_codepipeline as codepipeline
                
                webhook_filter_rule_property = codepipeline.CfnWebhook.WebhookFilterRuleProperty(
                    json_path="jsonPath",
                
                    # the properties below are optional
                    match_equals="matchEquals"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "json_path": json_path,
            }
            if match_equals is not None:
                self._values["match_equals"] = match_equals

        @builtins.property
        def json_path(self) -> builtins.str:
            '''``CfnWebhook.WebhookFilterRuleProperty.JsonPath``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-jsonpath
            '''
            result = self._values.get("json_path")
            assert result is not None, "Required property 'json_path' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def match_equals(self) -> typing.Optional[builtins.str]:
            '''``CfnWebhook.WebhookFilterRuleProperty.MatchEquals``.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-webhook-webhookfilterrule.html#cfn-codepipeline-webhook-webhookfilterrule-matchequals
            '''
            result = self._values.get("match_equals")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "WebhookFilterRuleProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CfnWebhookProps",
    jsii_struct_bases=[],
    name_mapping={
        "authentication": "authentication",
        "authentication_configuration": "authenticationConfiguration",
        "filters": "filters",
        "name": "name",
        "register_with_third_party": "registerWithThirdParty",
        "target_action": "targetAction",
        "target_pipeline": "targetPipeline",
        "target_pipeline_version": "targetPipelineVersion",
    },
)
class CfnWebhookProps:
    def __init__(
        self,
        *,
        authentication: builtins.str,
        authentication_configuration: typing.Union[CfnWebhook.WebhookAuthConfigurationProperty, _IResolvable_da3f097b],
        filters: typing.Union[_IResolvable_da3f097b, typing.Sequence[typing.Union[CfnWebhook.WebhookFilterRuleProperty, _IResolvable_da3f097b]]],
        name: typing.Optional[builtins.str] = None,
        register_with_third_party: typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]] = None,
        target_action: builtins.str,
        target_pipeline: builtins.str,
        target_pipeline_version: jsii.Number,
    ) -> None:
        '''Properties for defining a ``AWS::CodePipeline::Webhook``.

        :param authentication: ``AWS::CodePipeline::Webhook.Authentication``.
        :param authentication_configuration: ``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.
        :param filters: ``AWS::CodePipeline::Webhook.Filters``.
        :param name: ``AWS::CodePipeline::Webhook.Name``.
        :param register_with_third_party: ``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.
        :param target_action: ``AWS::CodePipeline::Webhook.TargetAction``.
        :param target_pipeline: ``AWS::CodePipeline::Webhook.TargetPipeline``.
        :param target_pipeline_version: ``AWS::CodePipeline::Webhook.TargetPipelineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            cfn_webhook_props = codepipeline.CfnWebhookProps(
                authentication="authentication",
                authentication_configuration=codepipeline.CfnWebhook.WebhookAuthConfigurationProperty(
                    allowed_ip_range="allowedIpRange",
                    secret_token="secretToken"
                ),
                filters=[codepipeline.CfnWebhook.WebhookFilterRuleProperty(
                    json_path="jsonPath",
            
                    # the properties below are optional
                    match_equals="matchEquals"
                )],
                target_action="targetAction",
                target_pipeline="targetPipeline",
                target_pipeline_version=123,
            
                # the properties below are optional
                name="name",
                register_with_third_party=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authentication": authentication,
            "authentication_configuration": authentication_configuration,
            "filters": filters,
            "target_action": target_action,
            "target_pipeline": target_pipeline,
            "target_pipeline_version": target_pipeline_version,
        }
        if name is not None:
            self._values["name"] = name
        if register_with_third_party is not None:
            self._values["register_with_third_party"] = register_with_third_party

    @builtins.property
    def authentication(self) -> builtins.str:
        '''``AWS::CodePipeline::Webhook.Authentication``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authentication
        '''
        result = self._values.get("authentication")
        assert result is not None, "Required property 'authentication' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_configuration(
        self,
    ) -> typing.Union[CfnWebhook.WebhookAuthConfigurationProperty, _IResolvable_da3f097b]:
        '''``AWS::CodePipeline::Webhook.AuthenticationConfiguration``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-authenticationconfiguration
        '''
        result = self._values.get("authentication_configuration")
        assert result is not None, "Required property 'authentication_configuration' is missing"
        return typing.cast(typing.Union[CfnWebhook.WebhookAuthConfigurationProperty, _IResolvable_da3f097b], result)

    @builtins.property
    def filters(
        self,
    ) -> typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnWebhook.WebhookFilterRuleProperty, _IResolvable_da3f097b]]]:
        '''``AWS::CodePipeline::Webhook.Filters``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-filters
        '''
        result = self._values.get("filters")
        assert result is not None, "Required property 'filters' is missing"
        return typing.cast(typing.Union[_IResolvable_da3f097b, typing.List[typing.Union[CfnWebhook.WebhookFilterRuleProperty, _IResolvable_da3f097b]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''``AWS::CodePipeline::Webhook.Name``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def register_with_third_party(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]]:
        '''``AWS::CodePipeline::Webhook.RegisterWithThirdParty``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-registerwiththirdparty
        '''
        result = self._values.get("register_with_third_party")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _IResolvable_da3f097b]], result)

    @builtins.property
    def target_action(self) -> builtins.str:
        '''``AWS::CodePipeline::Webhook.TargetAction``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetaction
        '''
        result = self._values.get("target_action")
        assert result is not None, "Required property 'target_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_pipeline(self) -> builtins.str:
        '''``AWS::CodePipeline::Webhook.TargetPipeline``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipeline
        '''
        result = self._values.get("target_pipeline")
        assert result is not None, "Required property 'target_pipeline' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_pipeline_version(self) -> jsii.Number:
        '''``AWS::CodePipeline::Webhook.TargetPipelineVersion``.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-webhook.html#cfn-codepipeline-webhook-targetpipelineversion
        '''
        result = self._values.get("target_pipeline_version")
        assert result is not None, "Required property 'target_pipeline_version' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnWebhookProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CommonActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
    },
)
class CommonActionProps:
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Common properties shared by all Actions.

        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            common_action_props = codepipeline.CommonActionProps(
                action_name="actionName",
            
                # the properties below are optional
                run_order=123,
                variables_namespace="variablesNamespace"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CommonAwsActionProps",
    jsii_struct_bases=[CommonActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
    },
)
class CommonAwsActionProps(CommonActionProps):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_235f5d8e] = None,
    ) -> None:
        '''Common properties shared by all Actions whose {@link ActionProperties.owner} field is 'AWS' (or unset, as 'AWS' is the default).

        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            from aws_cdk import aws_iam as iam
            
            # role is of type Role
            
            common_aws_action_props = codepipeline.CommonAwsActionProps(
                action_name="actionName",
            
                # the properties below are optional
                role=role,
                run_order=123,
                variables_namespace="variablesNamespace"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_235f5d8e]:
        '''The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_235f5d8e], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonAwsActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CrossRegionSupport",
    jsii_struct_bases=[],
    name_mapping={"replication_bucket": "replicationBucket", "stack": "stack"},
)
class CrossRegionSupport:
    def __init__(
        self,
        *,
        replication_bucket: _IBucket_42e086fd,
        stack: _Stack_2866e57f,
    ) -> None:
        '''An interface representing resources generated in order to support the cross-region capabilities of CodePipeline.

        You get instances of this interface from the {@link Pipeline#crossRegionSupport} property.

        :param replication_bucket: The replication Bucket used by CodePipeline to operate in this region. Belongs to {@link stack}.
        :param stack: The Stack that has been created to house the replication Bucket required for this region.

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk as cdk
            from aws_cdk import aws_codepipeline as codepipeline
            from aws_cdk import aws_s3 as s3
            
            # bucket is of type Bucket
            # stack is of type Stack
            
            cross_region_support = codepipeline.CrossRegionSupport(
                replication_bucket=bucket,
                stack=stack
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "replication_bucket": replication_bucket,
            "stack": stack,
        }

    @builtins.property
    def replication_bucket(self) -> _IBucket_42e086fd:
        '''The replication Bucket used by CodePipeline to operate in this region.

        Belongs to {@link stack}.
        '''
        result = self._values.get("replication_bucket")
        assert result is not None, "Required property 'replication_bucket' is missing"
        return typing.cast(_IBucket_42e086fd, result)

    @builtins.property
    def stack(self) -> _Stack_2866e57f:
        '''The Stack that has been created to house the replication Bucket required for this  region.'''
        result = self._values.get("stack")
        assert result is not None, "Required property 'stack' is missing"
        return typing.cast(_Stack_2866e57f, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossRegionSupport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CustomActionProperty",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "key": "key",
        "name": "name",
        "queryable": "queryable",
        "required": "required",
        "secret": "secret",
        "type": "type",
    },
)
class CustomActionProperty:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.bool] = None,
        name: builtins.str,
        queryable: typing.Optional[builtins.bool] = None,
        required: builtins.bool,
        secret: typing.Optional[builtins.bool] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The creation attributes used for defining a configuration property of a custom Action.

        :param description: The description of the property. Default: the description will be empty
        :param key: Whether this property is a key. Default: false
        :param name: The name of the property. You use this name in the ``configuration`` attribute when defining your custom Action class.
        :param queryable: Whether this property is queryable. Note that only a single property of a custom Action can be queryable. Default: false
        :param required: Whether this property is required.
        :param secret: Whether this property is secret, like a password, or access key. Default: false
        :param type: The type of the property, like 'String', 'Number', or 'Boolean'. Default: 'String'

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            custom_action_property = codepipeline.CustomActionProperty(
                name="name",
                required=False,
            
                # the properties below are optional
                description="description",
                key=False,
                queryable=False,
                secret=False,
                type="type"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "required": required,
        }
        if description is not None:
            self._values["description"] = description
        if key is not None:
            self._values["key"] = key
        if queryable is not None:
            self._values["queryable"] = queryable
        if secret is not None:
            self._values["secret"] = secret
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the property.

        :default: the description will be empty
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.bool]:
        '''Whether this property is a key.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-key
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the property.

        You use this name in the ``configuration`` attribute when defining your custom Action class.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def queryable(self) -> typing.Optional[builtins.bool]:
        '''Whether this property is queryable.

        Note that only a single property of a custom Action can be queryable.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-customactiontype-configurationproperties.html#cfn-codepipeline-customactiontype-configurationproperties-queryable
        '''
        result = self._values.get("queryable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def required(self) -> builtins.bool:
        '''Whether this property is required.'''
        result = self._values.get("required")
        assert result is not None, "Required property 'required' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.bool]:
        '''Whether this property is secret, like a password, or access key.

        :default: false
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The type of the property, like 'String', 'Number', or 'Boolean'.

        :default: 'String'
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomActionProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomActionRegistration(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.CustomActionRegistration",
):
    '''The resource representing registering a custom Action with CodePipeline.

    For the Action to be usable, it has to be registered for every region and every account it's used in.
    In addition to this class, you should most likely also provide your clients a class
    representing your custom Action, extending the Action class,
    and taking the ``actionProperties`` as properly typed, construction properties.

    Example::

        # Make a custom CodePipeline Action
        codepipeline.CustomActionRegistration(self, "GenericGitSourceProviderResource",
            category=codepipeline.ActionCategory.SOURCE,
            artifact_bounds=codepipeline.ActionArtifactBounds(min_inputs=0, max_inputs=0, min_outputs=1, max_outputs=1),
            provider="GenericGitSource",
            version="1",
            entity_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
            execution_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
            action_properties=[codepipeline.CustomActionProperty(
                name="Branch",
                required=True,
                key=False,
                secret=False,
                queryable=False,
                description="Git branch to pull",
                type="String"
            ), codepipeline.CustomActionProperty(
                name="GitUrl",
                required=True,
                key=False,
                secret=False,
                queryable=False,
                description="SSH git clone URL",
                type="String"
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        artifact_bounds: ActionArtifactBounds,
        category: ActionCategory,
        provider: builtins.str,
        action_properties: typing.Optional[typing.Sequence[CustomActionProperty]] = None,
        entity_url: typing.Optional[builtins.str] = None,
        execution_url: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param artifact_bounds: The artifact bounds of the Action.
        :param category: The category of the Action.
        :param provider: The provider of the Action. For example, ``'MyCustomActionProvider'``
        :param action_properties: The properties used for customizing the instance of your Action. Default: []
        :param entity_url: The URL shown for the entire Action in the Pipeline UI. Default: none
        :param execution_url: The URL shown for a particular execution of an Action in the Pipeline UI. Default: none
        :param version: The version of your Action. Default: '1'
        '''
        props = CustomActionRegistrationProps(
            artifact_bounds=artifact_bounds,
            category=category,
            provider=provider,
            action_properties=action_properties,
            entity_url=entity_url,
            execution_url=execution_url,
            version=version,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.CustomActionRegistrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_bounds": "artifactBounds",
        "category": "category",
        "provider": "provider",
        "action_properties": "actionProperties",
        "entity_url": "entityUrl",
        "execution_url": "executionUrl",
        "version": "version",
    },
)
class CustomActionRegistrationProps:
    def __init__(
        self,
        *,
        artifact_bounds: ActionArtifactBounds,
        category: ActionCategory,
        provider: builtins.str,
        action_properties: typing.Optional[typing.Sequence[CustomActionProperty]] = None,
        entity_url: typing.Optional[builtins.str] = None,
        execution_url: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties of registering a custom Action.

        :param artifact_bounds: The artifact bounds of the Action.
        :param category: The category of the Action.
        :param provider: The provider of the Action. For example, ``'MyCustomActionProvider'``
        :param action_properties: The properties used for customizing the instance of your Action. Default: []
        :param entity_url: The URL shown for the entire Action in the Pipeline UI. Default: none
        :param execution_url: The URL shown for a particular execution of an Action in the Pipeline UI. Default: none
        :param version: The version of your Action. Default: '1'

        Example::

            # Make a custom CodePipeline Action
            codepipeline.CustomActionRegistration(self, "GenericGitSourceProviderResource",
                category=codepipeline.ActionCategory.SOURCE,
                artifact_bounds=codepipeline.ActionArtifactBounds(min_inputs=0, max_inputs=0, min_outputs=1, max_outputs=1),
                provider="GenericGitSource",
                version="1",
                entity_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
                execution_url="https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-create-custom-action.html",
                action_properties=[codepipeline.CustomActionProperty(
                    name="Branch",
                    required=True,
                    key=False,
                    secret=False,
                    queryable=False,
                    description="Git branch to pull",
                    type="String"
                ), codepipeline.CustomActionProperty(
                    name="GitUrl",
                    required=True,
                    key=False,
                    secret=False,
                    queryable=False,
                    description="SSH git clone URL",
                    type="String"
                )
                ]
            )
        '''
        if isinstance(artifact_bounds, dict):
            artifact_bounds = ActionArtifactBounds(**artifact_bounds)
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_bounds": artifact_bounds,
            "category": category,
            "provider": provider,
        }
        if action_properties is not None:
            self._values["action_properties"] = action_properties
        if entity_url is not None:
            self._values["entity_url"] = entity_url
        if execution_url is not None:
            self._values["execution_url"] = execution_url
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def artifact_bounds(self) -> ActionArtifactBounds:
        '''The artifact bounds of the Action.'''
        result = self._values.get("artifact_bounds")
        assert result is not None, "Required property 'artifact_bounds' is missing"
        return typing.cast(ActionArtifactBounds, result)

    @builtins.property
    def category(self) -> ActionCategory:
        '''The category of the Action.'''
        result = self._values.get("category")
        assert result is not None, "Required property 'category' is missing"
        return typing.cast(ActionCategory, result)

    @builtins.property
    def provider(self) -> builtins.str:
        '''The provider of the Action.

        For example, ``'MyCustomActionProvider'``
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_properties(self) -> typing.Optional[typing.List[CustomActionProperty]]:
        '''The properties used for customizing the instance of your Action.

        :default: []
        '''
        result = self._values.get("action_properties")
        return typing.cast(typing.Optional[typing.List[CustomActionProperty]], result)

    @builtins.property
    def entity_url(self) -> typing.Optional[builtins.str]:
        '''The URL shown for the entire Action in the Pipeline UI.

        :default: none
        '''
        result = self._values.get("entity_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_url(self) -> typing.Optional[builtins.str]:
        '''The URL shown for a particular execution of an Action in the Pipeline UI.

        :default: none
        '''
        result = self._values.get("execution_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''The version of your Action.

        :default: '1'
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomActionRegistrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GlobalVariables(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.GlobalVariables",
):
    '''The CodePipeline variables that are global, not bound to a specific action.

    This class defines a bunch of static fields that represent the different variables.
    These can be used can be used in any action configuration.

    Example::

        # OtherAction is some action type that produces variables, like EcrSourceAction
        OtherAction(
            # ...
            config=codepipeline.GlobalVariables.execution_id,
            action_name="otherAction"
        )
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="executionId")
    def EXECUTION_ID(cls) -> builtins.str:
        '''The identifier of the current pipeline execution.'''
        return typing.cast(builtins.str, jsii.sget(cls, "executionId"))


@jsii.interface(jsii_type="aws-cdk-lib.aws_codepipeline.IAction")
class IAction(typing_extensions.Protocol):
    '''A Pipeline Action.

    If you want to implement this interface,
    consider extending the {@link Action} class,
    which contains some common logic.
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> ActionProperties:
        '''The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.
        '''
        ...

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        stage: "IStage",
        *,
        bucket: _IBucket_42e086fd,
        role: _IRole_235f5d8e,
    ) -> ActionConfig:
        '''The callback invoked when this Action is added to a Pipeline.

        :param scope: the Construct tree scope the Action can use if it needs to create any resources.
        :param stage: the {@link IStage} this Action is being added to.
        :param bucket: 
        :param role: 
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_IEventBus_88d13111] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_Schedule_c151d01f] = None,
        targets: typing.Optional[typing.Sequence[_IRuleTarget_7a91f454]] = None,
    ) -> _Rule_334ed2b5:
        '''Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: the name to use for the new Event.
        :param target: the optional target for the Event.
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        ...


class _IActionProxy:
    '''A Pipeline Action.

    If you want to implement this interface,
    consider extending the {@link Action} class,
    which contains some common logic.
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.aws_codepipeline.IAction"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> ActionProperties:
        '''The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.
        '''
        return typing.cast(ActionProperties, jsii.get(self, "actionProperties"))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        stage: "IStage",
        *,
        bucket: _IBucket_42e086fd,
        role: _IRole_235f5d8e,
    ) -> ActionConfig:
        '''The callback invoked when this Action is added to a Pipeline.

        :param scope: the Construct tree scope the Action can use if it needs to create any resources.
        :param stage: the {@link IStage} this Action is being added to.
        :param bucket: 
        :param role: 
        '''
        options = ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bind", [scope, stage, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_IEventBus_88d13111] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_Schedule_c151d01f] = None,
        targets: typing.Optional[typing.Sequence[_IRuleTarget_7a91f454]] = None,
    ) -> _Rule_334ed2b5:
        '''Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: the name to use for the new Event.
        :param target: the optional target for the Event.
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        options = _RuleProps_11ecd19e(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onStateChange", [name, target, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAction).__jsii_proxy_class__ = lambda : _IActionProxy


@jsii.interface(jsii_type="aws-cdk-lib.aws_codepipeline.IPipeline")
class IPipeline(
    _IResource_c80c4260,
    _INotificationRuleSource_10482823,
    typing_extensions.Protocol,
):
    '''The abstract view of an AWS CodePipeline as required and used by Actions.

    It extends {@link events.IRuleTarget},
    so this interface can be used as a Target for CloudWatch Events.
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> builtins.str:
        '''The ARN of the Pipeline.

        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        '''The name of the Pipeline.

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        events: typing.Sequence["PipelineNotificationEvents"],
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Defines a CodeStar notification rule triggered when the pipeline events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnExecutionStateChange``, ``notifyOnAnyStageStateChange``,
        ``notifyOnAnyActionStateChange`` and ``notifyOnAnyManualApprovalStateChange``
        to define rules for these specific event emitted.

        :param id: The id of the CodeStar notification rule.
        :param target: The target to register for the CodeStar Notifications destination.
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar notification rule associated with this build project.
        '''
        ...

    @jsii.member(jsii_name="notifyOnAnyActionStateChange")
    def notify_on_any_action_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Action execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="notifyOnAnyManualApprovalStateChange")
    def notify_on_any_manual_approval_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Manual approval" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="notifyOnAnyStageStateChange")
    def notify_on_any_stage_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Stage execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="notifyOnExecutionStateChange")
    def notify_on_execution_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Pipeline execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
    ) -> _Rule_334ed2b5:
        '''Define an event rule triggered by this CodePipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
    ) -> _Rule_334ed2b5:
        '''Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        ...


class _IPipelineProxy(
    jsii.proxy_for(_IResource_c80c4260), # type: ignore[misc]
    jsii.proxy_for(_INotificationRuleSource_10482823), # type: ignore[misc]
):
    '''The abstract view of an AWS CodePipeline as required and used by Actions.

    It extends {@link events.IRuleTarget},
    so this interface can be used as a Target for CloudWatch Events.
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.aws_codepipeline.IPipeline"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> builtins.str:
        '''The ARN of the Pipeline.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "pipelineArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        '''The name of the Pipeline.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "pipelineName"))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        events: typing.Sequence["PipelineNotificationEvents"],
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Defines a CodeStar notification rule triggered when the pipeline events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnExecutionStateChange``, ``notifyOnAnyStageStateChange``,
        ``notifyOnAnyActionStateChange`` and ``notifyOnAnyManualApprovalStateChange``
        to define rules for these specific event emitted.

        :param id: The id of the CodeStar notification rule.
        :param target: The target to register for the CodeStar Notifications destination.
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :return: CodeStar notification rule associated with this build project.
        '''
        options = PipelineNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyActionStateChange")
    def notify_on_any_action_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Action execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnAnyActionStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyManualApprovalStateChange")
    def notify_on_any_manual_approval_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Manual approval" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnAnyManualApprovalStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyStageStateChange")
    def notify_on_any_stage_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Stage execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnAnyStageStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnExecutionStateChange")
    def notify_on_execution_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Pipeline execution" events emitted from this pipeline.

        :param id: Identifier for this notification handler.
        :param target: The target to register for the CodeStar Notifications destination.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnExecutionStateChange", [id, target, options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
    ) -> _Rule_334ed2b5:
        '''Define an event rule triggered by this CodePipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = _OnEventOptions_8711b8b3(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
    ) -> _Rule_334ed2b5:
        '''Define an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = _OnEventOptions_8711b8b3(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onStateChange", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPipeline).__jsii_proxy_class__ = lambda : _IPipelineProxy


@jsii.interface(jsii_type="aws-cdk-lib.aws_codepipeline.IStage")
class IStage(typing_extensions.Protocol):
    '''The abstract interface of a Pipeline Stage that is used by Actions.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[IAction]:
        '''The actions belonging to this stage.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> IPipeline:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name of this Pipeline Stage.'''
        ...

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: IAction) -> None:
        '''
        :param action: -
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_IEventBus_88d13111] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_Schedule_c151d01f] = None,
        targets: typing.Optional[typing.Sequence[_IRuleTarget_7a91f454]] = None,
    ) -> _Rule_334ed2b5:
        '''
        :param name: -
        :param target: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        ...


class _IStageProxy:
    '''The abstract interface of a Pipeline Stage that is used by Actions.'''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.aws_codepipeline.IStage"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actions")
    def actions(self) -> typing.List[IAction]:
        '''The actions belonging to this stage.'''
        return typing.cast(typing.List[IAction], jsii.get(self, "actions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> IPipeline:
        return typing.cast(IPipeline, jsii.get(self, "pipeline"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageName")
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name of this Pipeline Stage.'''
        return typing.cast(builtins.str, jsii.get(self, "stageName"))

    @jsii.member(jsii_name="addAction")
    def add_action(self, action: IAction) -> None:
        '''
        :param action: -
        '''
        return typing.cast(None, jsii.invoke(self, "addAction", [action]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_IEventBus_88d13111] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_Schedule_c151d01f] = None,
        targets: typing.Optional[typing.Sequence[_IRuleTarget_7a91f454]] = None,
    ) -> _Rule_334ed2b5:
        '''
        :param name: -
        :param target: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        options = _RuleProps_11ecd19e(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onStateChange", [name, target, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStage).__jsii_proxy_class__ = lambda : _IStageProxy


@jsii.implements(IPipeline)
class Pipeline(
    _Resource_45bc6135,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-cdk-lib.aws_codepipeline.Pipeline",
):
    '''An AWS CodePipeline pipeline with its associated IAM role and S3 bucket.

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        # create a pipeline
        import aws_cdk.aws_codecommit as codecommit
        
        # add a source action to the stage
        # repo is of type Repository
        # source_artifact is of type Artifact
        
        
        pipeline = codepipeline.Pipeline(self, "Pipeline")
        
        # add a stage
        source_stage = pipeline.add_stage(stage_name="Source")
        source_stage.add_action(codepipeline_actions.CodeCommitSourceAction(
            action_name="Source",
            output=source_artifact,
            repository=repo
        ))
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        artifact_bucket: typing.Optional[_IBucket_42e086fd] = None,
        cross_account_keys: typing.Optional[builtins.bool] = None,
        cross_region_replication_buckets: typing.Optional[typing.Mapping[builtins.str, _IBucket_42e086fd]] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_IRole_235f5d8e] = None,
        stages: typing.Optional[typing.Sequence["StageProps"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param artifact_bucket: The S3 bucket used by this Pipeline to store artifacts. Default: - A new S3 bucket will be created.
        :param cross_account_keys: Create KMS keys for cross-account deployments. This controls whether the pipeline is enabled for cross-account deployments. By default cross-account deployments are enabled, but this feature requires that KMS Customer Master Keys are created which have a cost of $1/month. If you do not need cross-account deployments, you can set this to ``false`` to not create those keys and save on that cost (the artifact bucket will be encrypted with an AWS-managed key). However, cross-account deployments will no longer be possible. Default: true
        :param cross_region_replication_buckets: A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a Stack containing an S3 Bucket in that region. Default: - None.
        :param enable_key_rotation: Enable KMS key rotation for the generated KMS keys. By default KMS key rotation is disabled, but will add an additional $1/month for each year the key exists when enabled. Default: - false (key rotation is disabled)
        :param pipeline_name: Name of the pipeline. Default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
        :param restart_execution_on_update: Indicates whether to rerun the AWS CodePipeline pipeline after you update it. Default: false
        :param role: The IAM role to be assumed by this Pipeline. Default: a new IAM role will be created.
        :param stages: The list of Stages, in order, to create this Pipeline with. You can always add more Stages later by calling {@link Pipeline#addStage}. Default: - None.
        '''
        props = PipelineProps(
            artifact_bucket=artifact_bucket,
            cross_account_keys=cross_account_keys,
            cross_region_replication_buckets=cross_region_replication_buckets,
            enable_key_rotation=enable_key_rotation,
            pipeline_name=pipeline_name,
            restart_execution_on_update=restart_execution_on_update,
            role=role,
            stages=stages,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addStage")
    def add_stage(
        self,
        *,
        placement: typing.Optional["StagePlacement"] = None,
        actions: typing.Optional[typing.Sequence[IAction]] = None,
        stage_name: builtins.str,
    ) -> IStage:
        '''Creates a new Stage, and adds it to this Pipeline.

        :param placement: 
        :param actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.
        :param stage_name: The physical, human-readable name to assign to this Pipeline Stage.

        :return: the newly created Stage
        '''
        props = StageOptions(
            placement=placement, actions=actions, stage_name=stage_name
        )

        return typing.cast(IStage, jsii.invoke(self, "addStage", [props]))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(self, statement: _PolicyStatement_0fe33853) -> None:
        '''Adds a statement to the pipeline role.

        :param statement: -
        '''
        return typing.cast(None, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="bindAsNotificationRuleSource")
    def bind_as_notification_rule_source(
        self,
        _scope: constructs.Construct,
    ) -> _NotificationRuleSourceConfig_20189a3e:
        '''Returns a source configuration for notification rule.

        :param _scope: -
        '''
        return typing.cast(_NotificationRuleSourceConfig_20189a3e, jsii.invoke(self, "bindAsNotificationRuleSource", [_scope]))

    @jsii.member(jsii_name="fromPipelineArn") # type: ignore[misc]
    @builtins.classmethod
    def from_pipeline_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        pipeline_arn: builtins.str,
    ) -> IPipeline:
        '''Import a pipeline into this app.

        :param scope: the scope into which to import this pipeline.
        :param id: the logical ID of the returned pipeline construct.
        :param pipeline_arn: The ARN of the pipeline (e.g. ``arn:aws:codepipeline:us-east-1:123456789012:MyDemoPipeline``).
        '''
        return typing.cast(IPipeline, jsii.sinvoke(cls, "fromPipelineArn", [scope, id, pipeline_arn]))

    @jsii.member(jsii_name="notifyOn")
    def notify_on(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        events: typing.Sequence["PipelineNotificationEvents"],
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Defines a CodeStar notification rule triggered when the pipeline events emitted by you specified, it very similar to ``onEvent`` API.

        You can also use the methods ``notifyOnExecutionStateChange``, ``notifyOnAnyStageStateChange``,
        ``notifyOnAnyActionStateChange`` and ``notifyOnAnyManualApprovalStateChange``
        to define rules for these specific event emitted.

        :param id: -
        :param target: -
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        options = PipelineNotifyOnOptions(
            events=events,
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOn", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyActionStateChange")
    def notify_on_any_action_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Action execution" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnAnyActionStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyManualApprovalStateChange")
    def notify_on_any_manual_approval_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Manual approval" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnAnyManualApprovalStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnAnyStageStateChange")
    def notify_on_any_stage_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Stage execution" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnAnyStageStateChange", [id, target, options]))

    @jsii.member(jsii_name="notifyOnExecutionStateChange")
    def notify_on_execution_state_change(
        self,
        id: builtins.str,
        target: _INotificationRuleTarget_faa3b79b,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
    ) -> _INotificationRule_71939426:
        '''Define an notification rule triggered by the set of the "Pipeline execution" events emitted from this pipeline.

        :param id: -
        :param target: -
        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        '''
        options = _NotificationRuleOptions_dff73281(
            detail_type=detail_type,
            enabled=enabled,
            notification_rule_name=notification_rule_name,
        )

        return typing.cast(_INotificationRule_71939426, jsii.invoke(self, "notifyOnExecutionStateChange", [id, target, options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
    ) -> _Rule_334ed2b5:
        '''Defines an event rule triggered by this CodePipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = _OnEventOptions_8711b8b3(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
    ) -> _Rule_334ed2b5:
        '''Defines an event rule triggered by the "CodePipeline Pipeline Execution State Change" event emitted from this pipeline.

        :param id: Identifier for this event handler.
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = _OnEventOptions_8711b8b3(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onStateChange", [id, options]))

    @jsii.member(jsii_name="stage")
    def stage(self, stage_name: builtins.str) -> IStage:
        '''Access one of the pipeline's stages by stage name.

        :param stage_name: -
        '''
        return typing.cast(IStage, jsii.invoke(self, "stage", [stage_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(self) -> _IBucket_42e086fd:
        '''Bucket used to store output artifacts.'''
        return typing.cast(_IBucket_42e086fd, jsii.get(self, "artifactBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="crossRegionSupport")
    def cross_region_support(self) -> typing.Mapping[builtins.str, CrossRegionSupport]:
        '''Returns all of the {@link CrossRegionSupportStack}s that were generated automatically when dealing with Actions that reside in a different region than the Pipeline itself.'''
        return typing.cast(typing.Mapping[builtins.str, CrossRegionSupport], jsii.get(self, "crossRegionSupport"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineArn")
    def pipeline_arn(self) -> builtins.str:
        '''ARN of this pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "pipelineArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineName")
    def pipeline_name(self) -> builtins.str:
        '''The name of the pipeline.'''
        return typing.cast(builtins.str, jsii.get(self, "pipelineName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineVersion")
    def pipeline_version(self) -> builtins.str:
        '''The version of the pipeline.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "pipelineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> _IRole_235f5d8e:
        '''The IAM role AWS CodePipeline will use to perform actions or assume roles for actions with a more specific IAM role.'''
        return typing.cast(_IRole_235f5d8e, jsii.get(self, "role"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageCount")
    def stage_count(self) -> jsii.Number:
        '''Get the number of Stages in this Pipeline.'''
        return typing.cast(jsii.Number, jsii.get(self, "stageCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IStage]:
        '''Returns the stages that comprise the pipeline.

        **Note**: the returned array is a defensive copy,
        so adding elements to it has no effect.
        Instead, use the {@link addStage} method if you want to add more stages
        to the pipeline.
        '''
        return typing.cast(typing.List[IStage], jsii.get(self, "stages"))


@jsii.enum(jsii_type="aws-cdk-lib.aws_codepipeline.PipelineNotificationEvents")
class PipelineNotificationEvents(enum.Enum):
    '''The list of event types for AWS Codepipeline Pipeline.

    :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#events-ref-pipeline
    '''

    ACTION_EXECUTION_CANCELED = "ACTION_EXECUTION_CANCELED"
    '''Trigger notification when pipeline action execution canceled.'''
    ACTION_EXECUTION_FAILED = "ACTION_EXECUTION_FAILED"
    '''Trigger notification when pipeline action execution failed.'''
    ACTION_EXECUTION_STARTED = "ACTION_EXECUTION_STARTED"
    '''Trigger notification when pipeline action execution started.'''
    ACTION_EXECUTION_SUCCEEDED = "ACTION_EXECUTION_SUCCEEDED"
    '''Trigger notification when pipeline action execution succeeded.'''
    MANUAL_APPROVAL_FAILED = "MANUAL_APPROVAL_FAILED"
    '''Trigger notification when pipeline manual approval failed.'''
    MANUAL_APPROVAL_NEEDED = "MANUAL_APPROVAL_NEEDED"
    '''Trigger notification when pipeline manual approval needed.'''
    MANUAL_APPROVAL_SUCCEEDED = "MANUAL_APPROVAL_SUCCEEDED"
    '''Trigger notification when pipeline manual approval succeeded.'''
    PIPELINE_EXECUTION_CANCELED = "PIPELINE_EXECUTION_CANCELED"
    '''Trigger notification when pipeline execution canceled.'''
    PIPELINE_EXECUTION_FAILED = "PIPELINE_EXECUTION_FAILED"
    '''Trigger notification when pipeline execution failed.'''
    PIPELINE_EXECUTION_RESUMED = "PIPELINE_EXECUTION_RESUMED"
    '''Trigger notification when pipeline execution resumed.'''
    PIPELINE_EXECUTION_STARTED = "PIPELINE_EXECUTION_STARTED"
    '''Trigger notification when pipeline execution started.'''
    PIPELINE_EXECUTION_SUCCEEDED = "PIPELINE_EXECUTION_SUCCEEDED"
    '''Trigger notification when pipeline execution succeeded.'''
    PIPELINE_EXECUTION_SUPERSEDED = "PIPELINE_EXECUTION_SUPERSEDED"
    '''Trigger notification when pipeline execution superseded.'''
    STAGE_EXECUTION_CANCELED = "STAGE_EXECUTION_CANCELED"
    '''Trigger notification when pipeline stage execution canceled.'''
    STAGE_EXECUTION_FAILED = "STAGE_EXECUTION_FAILED"
    '''Trigger notification when pipeline stage execution failed.'''
    STAGE_EXECUTION_RESUMED = "STAGE_EXECUTION_RESUMED"
    '''Trigger notification when pipeline stage execution resumed.'''
    STAGE_EXECUTION_STARTED = "STAGE_EXECUTION_STARTED"
    '''Trigger notification when pipeline stage execution started.'''
    STAGE_EXECUTION_SUCCEEDED = "STAGE_EXECUTION_SUCCEEDED"
    '''Trigger notification when pipeline stage execution succeeded.'''


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.PipelineNotifyOnOptions",
    jsii_struct_bases=[_NotificationRuleOptions_dff73281],
    name_mapping={
        "detail_type": "detailType",
        "enabled": "enabled",
        "notification_rule_name": "notificationRuleName",
        "events": "events",
    },
)
class PipelineNotifyOnOptions(_NotificationRuleOptions_dff73281):
    def __init__(
        self,
        *,
        detail_type: typing.Optional[_DetailType_cf8135e7] = None,
        enabled: typing.Optional[builtins.bool] = None,
        notification_rule_name: typing.Optional[builtins.str] = None,
        events: typing.Sequence[PipelineNotificationEvents],
    ) -> None:
        '''Additional options to pass to the notification rule.

        :param detail_type: The level of detail to include in the notifications for this resource. BASIC will include only the contents of the event as it would appear in AWS CloudWatch. FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created. Default: DetailType.FULL
        :param enabled: The status of the notification rule. If the enabled is set to DISABLED, notifications aren't sent for the notification rule. Default: true
        :param notification_rule_name: The name for the notification rule. Notification rule names must be unique in your AWS account. Default: - generated from the ``id``
        :param events: A list of event types associated with this notification rule for CodePipeline Pipeline. For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            from aws_cdk import aws_codestarnotifications as codestarnotifications
            
            pipeline_notify_on_options = codepipeline.PipelineNotifyOnOptions(
                events=[codepipeline.PipelineNotificationEvents.PIPELINE_EXECUTION_FAILED],
            
                # the properties below are optional
                detail_type=codestarnotifications.DetailType.BASIC,
                enabled=False,
                notification_rule_name="notificationRuleName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "events": events,
        }
        if detail_type is not None:
            self._values["detail_type"] = detail_type
        if enabled is not None:
            self._values["enabled"] = enabled
        if notification_rule_name is not None:
            self._values["notification_rule_name"] = notification_rule_name

    @builtins.property
    def detail_type(self) -> typing.Optional[_DetailType_cf8135e7]:
        '''The level of detail to include in the notifications for this resource.

        BASIC will include only the contents of the event as it would appear in AWS CloudWatch.
        FULL will include any supplemental information provided by AWS CodeStar Notifications and/or the service for the resource for which the notification is created.

        :default: DetailType.FULL
        '''
        result = self._values.get("detail_type")
        return typing.cast(typing.Optional[_DetailType_cf8135e7], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''The status of the notification rule.

        If the enabled is set to DISABLED, notifications aren't sent for the notification rule.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def notification_rule_name(self) -> typing.Optional[builtins.str]:
        '''The name for the notification rule.

        Notification rule names must be unique in your AWS account.

        :default: - generated from the ``id``
        '''
        result = self._values.get("notification_rule_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def events(self) -> typing.List[PipelineNotificationEvents]:
        '''A list of event types associated with this notification rule for CodePipeline Pipeline.

        For a complete list of event types and IDs, see Notification concepts in the Developer Tools Console User Guide.

        :see: https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api
        '''
        result = self._values.get("events")
        assert result is not None, "Required property 'events' is missing"
        return typing.cast(typing.List[PipelineNotificationEvents], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineNotifyOnOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.PipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_bucket": "artifactBucket",
        "cross_account_keys": "crossAccountKeys",
        "cross_region_replication_buckets": "crossRegionReplicationBuckets",
        "enable_key_rotation": "enableKeyRotation",
        "pipeline_name": "pipelineName",
        "restart_execution_on_update": "restartExecutionOnUpdate",
        "role": "role",
        "stages": "stages",
    },
)
class PipelineProps:
    def __init__(
        self,
        *,
        artifact_bucket: typing.Optional[_IBucket_42e086fd] = None,
        cross_account_keys: typing.Optional[builtins.bool] = None,
        cross_region_replication_buckets: typing.Optional[typing.Mapping[builtins.str, _IBucket_42e086fd]] = None,
        enable_key_rotation: typing.Optional[builtins.bool] = None,
        pipeline_name: typing.Optional[builtins.str] = None,
        restart_execution_on_update: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_IRole_235f5d8e] = None,
        stages: typing.Optional[typing.Sequence["StageProps"]] = None,
    ) -> None:
        '''
        :param artifact_bucket: The S3 bucket used by this Pipeline to store artifacts. Default: - A new S3 bucket will be created.
        :param cross_account_keys: Create KMS keys for cross-account deployments. This controls whether the pipeline is enabled for cross-account deployments. By default cross-account deployments are enabled, but this feature requires that KMS Customer Master Keys are created which have a cost of $1/month. If you do not need cross-account deployments, you can set this to ``false`` to not create those keys and save on that cost (the artifact bucket will be encrypted with an AWS-managed key). However, cross-account deployments will no longer be possible. Default: true
        :param cross_region_replication_buckets: A map of region to S3 bucket name used for cross-region CodePipeline. For every Action that you specify targeting a different region than the Pipeline itself, if you don't provide an explicit Bucket for that region using this property, the construct will automatically create a Stack containing an S3 Bucket in that region. Default: - None.
        :param enable_key_rotation: Enable KMS key rotation for the generated KMS keys. By default KMS key rotation is disabled, but will add an additional $1/month for each year the key exists when enabled. Default: - false (key rotation is disabled)
        :param pipeline_name: Name of the pipeline. Default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
        :param restart_execution_on_update: Indicates whether to rerun the AWS CodePipeline pipeline after you update it. Default: false
        :param role: The IAM role to be assumed by this Pipeline. Default: a new IAM role will be created.
        :param stages: The list of Stages, in order, to create this Pipeline with. You can always add more Stages later by calling {@link Pipeline#addStage}. Default: - None.

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            # deployment_group is of type ServerDeploymentGroup
            pipeline = codepipeline.Pipeline(self, "MyPipeline",
                pipeline_name="MyPipeline"
            )
            
            # add the source and build Stages to the Pipeline...
            build_output = codepipeline.Artifact()
            deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
                action_name="CodeDeploy",
                input=build_output,
                deployment_group=deployment_group
            )
            pipeline.add_stage(
                stage_name="Deploy",
                actions=[deploy_action]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if artifact_bucket is not None:
            self._values["artifact_bucket"] = artifact_bucket
        if cross_account_keys is not None:
            self._values["cross_account_keys"] = cross_account_keys
        if cross_region_replication_buckets is not None:
            self._values["cross_region_replication_buckets"] = cross_region_replication_buckets
        if enable_key_rotation is not None:
            self._values["enable_key_rotation"] = enable_key_rotation
        if pipeline_name is not None:
            self._values["pipeline_name"] = pipeline_name
        if restart_execution_on_update is not None:
            self._values["restart_execution_on_update"] = restart_execution_on_update
        if role is not None:
            self._values["role"] = role
        if stages is not None:
            self._values["stages"] = stages

    @builtins.property
    def artifact_bucket(self) -> typing.Optional[_IBucket_42e086fd]:
        '''The S3 bucket used by this Pipeline to store artifacts.

        :default: - A new S3 bucket will be created.
        '''
        result = self._values.get("artifact_bucket")
        return typing.cast(typing.Optional[_IBucket_42e086fd], result)

    @builtins.property
    def cross_account_keys(self) -> typing.Optional[builtins.bool]:
        '''Create KMS keys for cross-account deployments.

        This controls whether the pipeline is enabled for cross-account deployments.

        By default cross-account deployments are enabled, but this feature requires
        that KMS Customer Master Keys are created which have a cost of $1/month.

        If you do not need cross-account deployments, you can set this to ``false`` to
        not create those keys and save on that cost (the artifact bucket will be
        encrypted with an AWS-managed key). However, cross-account deployments will
        no longer be possible.

        :default: true
        '''
        result = self._values.get("cross_account_keys")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_replication_buckets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _IBucket_42e086fd]]:
        '''A map of region to S3 bucket name used for cross-region CodePipeline.

        For every Action that you specify targeting a different region than the Pipeline itself,
        if you don't provide an explicit Bucket for that region using this property,
        the construct will automatically create a Stack containing an S3 Bucket in that region.

        :default: - None.
        '''
        result = self._values.get("cross_region_replication_buckets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _IBucket_42e086fd]], result)

    @builtins.property
    def enable_key_rotation(self) -> typing.Optional[builtins.bool]:
        '''Enable KMS key rotation for the generated KMS keys.

        By default KMS key rotation is disabled, but will add an additional $1/month
        for each year the key exists when enabled.

        :default: - false (key rotation is disabled)
        '''
        result = self._values.get("enable_key_rotation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pipeline_name(self) -> typing.Optional[builtins.str]:
        '''Name of the pipeline.

        :default: - AWS CloudFormation generates an ID and uses that for the pipeline name.
        '''
        result = self._values.get("pipeline_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restart_execution_on_update(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether to rerun the AWS CodePipeline pipeline after you update it.

        :default: false
        '''
        result = self._values.get("restart_execution_on_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_235f5d8e]:
        '''The IAM role to be assumed by this Pipeline.

        :default: a new IAM role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_235f5d8e], result)

    @builtins.property
    def stages(self) -> typing.Optional[typing.List["StageProps"]]:
        '''The list of Stages, in order, to create this Pipeline with.

        You can always add more Stages later by calling {@link Pipeline#addStage}.

        :default: - None.
        '''
        result = self._values.get("stages")
        return typing.cast(typing.Optional[typing.List["StageProps"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.StagePlacement",
    jsii_struct_bases=[],
    name_mapping={"just_after": "justAfter", "right_before": "rightBefore"},
)
class StagePlacement:
    def __init__(
        self,
        *,
        just_after: typing.Optional[IStage] = None,
        right_before: typing.Optional[IStage] = None,
    ) -> None:
        '''Allows you to control where to place a new Stage when it's added to the Pipeline.

        Note that you can provide only one of the below properties -
        specifying more than one will result in a validation error.

        :param just_after: Inserts the new Stage as a child of the given Stage (changing its current child Stage, if it had one).
        :param right_before: Inserts the new Stage as a parent of the given Stage (changing its current parent Stage, if it had one).

        :see: #justAfter

        Example::

            # Insert a new Stage at an arbitrary point
            # pipeline is of type Pipeline
            # another_stage is of type IStage
            # yet_another_stage is of type IStage
            
            
            some_stage = pipeline.add_stage(
                stage_name="SomeStage",
                placement=codepipeline.StagePlacement(
                    # note: you can only specify one of the below properties
                    right_before=another_stage,
                    just_after=yet_another_stage
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if just_after is not None:
            self._values["just_after"] = just_after
        if right_before is not None:
            self._values["right_before"] = right_before

    @builtins.property
    def just_after(self) -> typing.Optional[IStage]:
        '''Inserts the new Stage as a child of the given Stage (changing its current child Stage, if it had one).'''
        result = self._values.get("just_after")
        return typing.cast(typing.Optional[IStage], result)

    @builtins.property
    def right_before(self) -> typing.Optional[IStage]:
        '''Inserts the new Stage as a parent of the given Stage (changing its current parent Stage, if it had one).'''
        result = self._values.get("right_before")
        return typing.cast(typing.Optional[IStage], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StagePlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.StageProps",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "stage_name": "stageName"},
)
class StageProps:
    def __init__(
        self,
        *,
        actions: typing.Optional[typing.Sequence[IAction]] = None,
        stage_name: builtins.str,
    ) -> None:
        '''Construction properties of a Pipeline Stage.

        :param actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.
        :param stage_name: The physical, human-readable name to assign to this Pipeline Stage.

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk import aws_codepipeline as codepipeline
            
            # action is of type Action
            
            stage_props = codepipeline.StageProps(
                stage_name="stageName",
            
                # the properties below are optional
                actions=[action]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "stage_name": stage_name,
        }
        if actions is not None:
            self._values["actions"] = actions

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[IAction]]:
        '''The list of Actions to create this Stage with.

        You can always add more Actions later by calling {@link IStage#addAction}.
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[IAction]], result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name to assign to this Pipeline Stage.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAction)
class Action(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="aws-cdk-lib.aws_codepipeline.Action",
):
    '''Low-level class for generic CodePipeline Actions implementing the {@link IAction} interface.

    Contains some common logic that can be re-used by all {@link IAction} implementations.
    If you're writing your own Action class,
    feel free to extend this class.
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        stage: IStage,
        *,
        bucket: _IBucket_42e086fd,
        role: _IRole_235f5d8e,
    ) -> ActionConfig:
        '''The callback invoked when this Action is added to a Pipeline.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 
        '''
        options = ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bind", [scope, stage, options]))

    @jsii.member(jsii_name="bound") # type: ignore[misc]
    @abc.abstractmethod
    def _bound(
        self,
        scope: constructs.Construct,
        stage: IStage,
        *,
        bucket: _IBucket_42e086fd,
        role: _IRole_235f5d8e,
    ) -> ActionConfig:
        '''This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 
        '''
        ...

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_IRuleTarget_7a91f454] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_IEventBus_88d13111] = None,
        event_pattern: typing.Optional[_EventPattern_fe557901] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_Schedule_c151d01f] = None,
        targets: typing.Optional[typing.Sequence[_IRuleTarget_7a91f454]] = None,
    ) -> _Rule_334ed2b5:
        '''Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: -
        :param target: -
        :param description: A description of the rule's purpose. Default: - No description.
        :param enabled: Indicates whether the rule is enabled. Default: true
        :param event_bus: The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.
        '''
        options = _RuleProps_11ecd19e(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_Rule_334ed2b5, jsii.invoke(self, "onStateChange", [name, target, options]))

    @jsii.member(jsii_name="variableExpression")
    def _variable_expression(self, variable_name: builtins.str) -> builtins.str:
        '''
        :param variable_name: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "variableExpression", [variable_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> ActionProperties:
        '''The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.
        '''
        return typing.cast(ActionProperties, jsii.get(self, "actionProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providedActionProperties")
    @abc.abstractmethod
    def _provided_action_properties(self) -> ActionProperties:
        '''This is a renamed version of the {@link IAction.actionProperties} property.'''
        ...


class _ActionProxy(Action):
    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: constructs.Construct,
        stage: IStage,
        *,
        bucket: _IBucket_42e086fd,
        role: _IRole_235f5d8e,
    ) -> ActionConfig:
        '''This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 
        '''
        options = ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(ActionConfig, jsii.invoke(self, "bound", [scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providedActionProperties")
    def _provided_action_properties(self) -> ActionProperties:
        '''This is a renamed version of the {@link IAction.actionProperties} property.'''
        return typing.cast(ActionProperties, jsii.get(self, "providedActionProperties"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Action).__jsii_proxy_class__ = lambda : _ActionProxy


@jsii.data_type(
    jsii_type="aws-cdk-lib.aws_codepipeline.StageOptions",
    jsii_struct_bases=[StageProps],
    name_mapping={
        "actions": "actions",
        "stage_name": "stageName",
        "placement": "placement",
    },
)
class StageOptions(StageProps):
    def __init__(
        self,
        *,
        actions: typing.Optional[typing.Sequence[IAction]] = None,
        stage_name: builtins.str,
        placement: typing.Optional[StagePlacement] = None,
    ) -> None:
        '''
        :param actions: The list of Actions to create this Stage with. You can always add more Actions later by calling {@link IStage#addAction}.
        :param stage_name: The physical, human-readable name to assign to this Pipeline Stage.
        :param placement: 

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            # deployment_group is of type ServerDeploymentGroup
            pipeline = codepipeline.Pipeline(self, "MyPipeline",
                pipeline_name="MyPipeline"
            )
            
            # add the source and build Stages to the Pipeline...
            build_output = codepipeline.Artifact()
            deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
                action_name="CodeDeploy",
                input=build_output,
                deployment_group=deployment_group
            )
            pipeline.add_stage(
                stage_name="Deploy",
                actions=[deploy_action]
            )
        '''
        if isinstance(placement, dict):
            placement = StagePlacement(**placement)
        self._values: typing.Dict[str, typing.Any] = {
            "stage_name": stage_name,
        }
        if actions is not None:
            self._values["actions"] = actions
        if placement is not None:
            self._values["placement"] = placement

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[IAction]]:
        '''The list of Actions to create this Stage with.

        You can always add more Actions later by calling {@link IStage#addAction}.
        '''
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[IAction]], result)

    @builtins.property
    def stage_name(self) -> builtins.str:
        '''The physical, human-readable name to assign to this Pipeline Stage.'''
        result = self._values.get("stage_name")
        assert result is not None, "Required property 'stage_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def placement(self) -> typing.Optional[StagePlacement]:
        result = self._values.get("placement")
        return typing.cast(typing.Optional[StagePlacement], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Action",
    "ActionArtifactBounds",
    "ActionBindOptions",
    "ActionCategory",
    "ActionConfig",
    "ActionProperties",
    "Artifact",
    "ArtifactPath",
    "CfnCustomActionType",
    "CfnCustomActionTypeProps",
    "CfnPipeline",
    "CfnPipelineProps",
    "CfnWebhook",
    "CfnWebhookProps",
    "CommonActionProps",
    "CommonAwsActionProps",
    "CrossRegionSupport",
    "CustomActionProperty",
    "CustomActionRegistration",
    "CustomActionRegistrationProps",
    "GlobalVariables",
    "IAction",
    "IPipeline",
    "IStage",
    "Pipeline",
    "PipelineNotificationEvents",
    "PipelineNotifyOnOptions",
    "PipelineProps",
    "StageOptions",
    "StagePlacement",
    "StageProps",
]

publication.publish()
