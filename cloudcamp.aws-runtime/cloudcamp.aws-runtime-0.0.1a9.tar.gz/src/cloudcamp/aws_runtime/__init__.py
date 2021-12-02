'''
# TODO
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

import aws_cdk.aws_certificatemanager
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_ecs_patterns
import aws_cdk.aws_rds
import aws_cdk.aws_route53
import aws_cdk.core
import aws_cdk.cx_api
import aws_cdk.pipelines


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.ARecordProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "target_ip": "targetIP", "ttl": "ttl"},
)
class ARecordProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        target_ip: builtins.str,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: 
        :param target_ip: 
        :param ttl: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "target_ip": target_ip,
        }
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_ip(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("target_ip")
        assert result is not None, "Required property 'target_ip' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ARecordProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.AaaaRecordProps",
    jsii_struct_bases=[ARecordProps],
    name_mapping={"name": "name", "target_ip": "targetIP", "ttl": "ttl"},
)
class AaaaRecordProps(ARecordProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        target_ip: builtins.str,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: 
        :param target_ip: 
        :param ttl: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "target_ip": target_ip,
        }
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_ip(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("target_ip")
        assert result is not None, "Required property 'target_ip' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AaaaRecordProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.AlarmConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "enabled": "enabled",
        "threshold": "threshold",
    },
)
class AlarmConfiguration:
    def __init__(
        self,
        *,
        duration: typing.Optional[jsii.Number] = None,
        enabled: typing.Optional[builtins.bool] = None,
        threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param duration: 
        :param enabled: 
        :param threshold: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration
        if enabled is not None:
            self._values["enabled"] = enabled
        if threshold is not None:
            self._values["threshold"] = threshold

    @builtins.property
    def duration(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class App(
    aws_cdk.core.App,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.App",
):
    '''(experimental) App represents your application running in the cloud․ Every app contains one or more ``{@link Stack | Stacks}``, which you can use to add your own resources, like a ``{@link WebServer | WebServer}`` or a ``{@link Database | Database}``.

    An app can be as big or small as you like - from a single webserver to
    dozens of load-balanced instances serving different parts of your
    application.

    This example adds a ``{@link WebServer | WebServer}`` to the
    ``{@link App.production | production}`` stack::

       # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
       from cloudcamp.aws_runtime import App, WebServer

       app = App()

       WebServer(app.production, "prod-web",
           dockerfile="../Dockerfile"
       )

    :stability: experimental
    :order: 1
    '''

    def __init__(self) -> None:
        '''(experimental) Initialize your cloudcamp application.

        :stability: experimental
        :remarks:

        App is a singleton class - it is instantiated exactly once, before
        any other resources are created.
        :topic: Initialization
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="addStack")
    def add_stack(self, name: builtins.str) -> "Stack":
        '''(experimental) Add a new stack to your application.

        Pass a stack name to create a new, empty stack::

           # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
           dev_stack = app.add_stack("development")

        :param name: The name of the stack.

        :stability: experimental
        '''
        return typing.cast("Stack", jsii.invoke(self, "addStack", [name]))

    @jsii.member(jsii_name="addStage")
    def add_stage(
        self,
        name: builtins.str,
        stage: typing.Optional["Stage"] = None,
    ) -> "Stage":
        '''(experimental) Add a new stage.

        This method can be used to add a stage with a custom ``Stack`` subclass::

           # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
           from cloudcamp.aws_runtime import App, WebServer, Stack

           class CustomStack(Stack):
               def __init__(self, scope, id, props):
                   super().__init__(scope, id, props)
                   WebServer(self, "web",
                       dockerfile="../Dockerfile"
                   )

           # later in the code...
           app = App()
           stage = app.add_stage("dev")
           stack = CustomStack(stage, "dev")

           # stack is automatically set to the new stack we created
           if stage.stack == stack:
               # outputs "True!"
               print("True!")

        :param name: The name of the stage.
        :param stage: An optional stage object. If not specifed, CloudCamp will create and return an empty stage.

        :stability: experimental
        '''
        return typing.cast("Stage", jsii.invoke(self, "addStage", [name, stage]))

    @jsii.member(jsii_name="getStack")
    def get_stack(self, name: builtins.str) -> "Stack":
        '''(experimental) Get an existing stack by name.

        :param name: The name of the stack.

        :stability: experimental
        :remarks:

        In addition to the default stacks provided by cloudcamp, you can
        create your own stacks.
        :topic: Adding custom stacks
        '''
        return typing.cast("Stack", jsii.invoke(self, "getStack", [name]))

    @jsii.member(jsii_name="getStage")
    def get_stage(self, name: builtins.str) -> "Stage":
        '''(experimental) Get an existing stage by name.

        Stages can be obtained by their name to modify their attributes. A common
        use case is to require manual approval to deploy to the production stage::

           # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
           stage = app.get_stage("production")
           stage.needs_manual_approval = True

        :param name: The name of the stage.

        :stability: experimental
        :remarks:

        Stages are responsible for building your stacks. By default,
        CloudCamp creates a stage for each stack and gives it the same name. You
        can customize this behaviour by adding your own stages.
        :topic: Stages
        '''
        return typing.cast("Stage", jsii.invoke(self, "getStage", [name]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        *,
        force: typing.Optional[builtins.bool] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
        validate_on_synthesis: typing.Optional[builtins.bool] = None,
    ) -> aws_cdk.cx_api.CloudAssembly:
        '''(experimental) Synthesize this stage into a cloud assembly.

        Once an assembly has been synthesized, it cannot be modified. Subsequent
        calls will return the same assembly.

        :param force: Force a re-synth, even if the stage has already been synthesized. This is used by tests to allow for incremental verification of the output. Do not use in production. Default: false
        :param skip_validation: Should we skip construct validation. Default: - false
        :param validate_on_synthesis: Whether the stack should be validated after synthesis to check for error metadata. Default: - false

        :stability: experimental
        :ignore: true
        '''
        options = aws_cdk.core.StageSynthesisOptions(
            force=force,
            skip_validation=skip_validation,
            validate_on_synthesis=validate_on_synthesis,
        )

        return typing.cast(aws_cdk.cx_api.CloudAssembly, jsii.invoke(self, "synth", [options]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="instance")
    def instance(cls) -> "App":
        '''(experimental) Returns the global App singleton instance.

        Throws an exception if App has not been instantiated yet.

        :stability: experimental
        '''
        return typing.cast("App", jsii.sget(cls, "instance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="network")
    def network(self) -> "Stack":
        '''(experimental) Use this stack for anything related to the network, for example DNS entries.

        :stability: experimental
        :remarks:

        To deploy resources to the cloud, they are added to a ``Stack``.
        CloudCamp comes with three default stacks:
        :topic: Stacks
        '''
        return typing.cast("Stack", jsii.get(self, "network"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> aws_cdk.pipelines.CdkPipeline:
        '''
        :stability: experimental
        :ignore: true
        '''
        return typing.cast(aws_cdk.pipelines.CdkPipeline, jsii.get(self, "pipeline"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="production")
    def production(self) -> "Stack":
        '''(experimental) The production stack.

        :stability: experimental
        '''
        return typing.cast("Stack", jsii.get(self, "production"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staging")
    def staging(self) -> "Stack":
        '''(experimental) This stack can be used to create an environment for testing changes before deploying to production.

        :stability: experimental
        '''
        return typing.cast("Stack", jsii.get(self, "staging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configuration")
    def configuration(self) -> "Configuration":
        '''
        :stability: experimental
        :ignore: true
        '''
        return typing.cast("Configuration", jsii.get(self, "configuration"))

    @configuration.setter
    def configuration(self, value: "Configuration") -> None:
        jsii.set(self, "configuration", value)


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.CNameRecordProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "target": "target", "ttl": "ttl"},
)
class CNameRecordProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        target: builtins.str,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: 
        :param target: 
        :param ttl: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "target": target,
        }
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CNameRecordProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.Configuration",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "branch": "branch",
        "name": "name",
        "region": "region",
        "repository": "repository",
        "repository_token_secret": "repositoryTokenSecret",
        "vpc_id": "vpcId",
    },
)
class Configuration:
    def __init__(
        self,
        *,
        account: builtins.str,
        branch: builtins.str,
        name: builtins.str,
        region: builtins.str,
        repository: builtins.str,
        repository_token_secret: builtins.str,
        vpc_id: builtins.str,
    ) -> None:
        '''
        :param account: 
        :param branch: 
        :param name: 
        :param region: 
        :param repository: 
        :param repository_token_secret: 
        :param vpc_id: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "branch": branch,
            "name": name,
            "region": region,
            "repository": repository,
            "repository_token_secret": repository_token_secret,
            "vpc_id": vpc_id,
        }

    @builtins.property
    def account(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_token_secret(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("repository_token_secret")
        assert result is not None, "Required property 'repository_token_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc_id")
        assert result is not None, "Required property 'vpc_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Configuration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Database(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.Database",
):
    '''
    :stability: experimental
    :order: 5
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        auto_pause: typing.Optional[jsii.Number] = None,
        database_name: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: the scope.
        :param id: the id.
        :param engine: 
        :param auto_pause: 
        :param database_name: 
        :param max_capacity: 
        :param min_capacity: 
        :param username: 
        :param vpc: 

        :stability: experimental
        '''
        props = DatabaseProps(
            engine=engine,
            auto_pause=auto_pause,
            database_name=database_name,
            max_capacity=max_capacity,
            min_capacity=min_capacity,
            username=username,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_rds.IServerlessCluster:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.IServerlessCluster, jsii.get(self, "cluster"))

    @cluster.setter
    def cluster(self, value: aws_cdk.aws_rds.IServerlessCluster) -> None:
        jsii.set(self, "cluster", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> "DatabaseVariables":
        '''
        :stability: experimental
        '''
        return typing.cast("DatabaseVariables", jsii.get(self, "env"))

    @env.setter
    def env(self, value: "DatabaseVariables") -> None:
        jsii.set(self, "env", value)


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.DatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "engine": "engine",
        "auto_pause": "autoPause",
        "database_name": "databaseName",
        "max_capacity": "maxCapacity",
        "min_capacity": "minCapacity",
        "username": "username",
        "vpc": "vpc",
    },
)
class DatabaseProps:
    def __init__(
        self,
        *,
        engine: builtins.str,
        auto_pause: typing.Optional[jsii.Number] = None,
        database_name: typing.Optional[builtins.str] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        min_capacity: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param engine: 
        :param auto_pause: 
        :param database_name: 
        :param max_capacity: 
        :param min_capacity: 
        :param username: 
        :param vpc: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "engine": engine,
        }
        if auto_pause is not None:
            self._values["auto_pause"] = auto_pause
        if database_name is not None:
            self._values["database_name"] = database_name
        if max_capacity is not None:
            self._values["max_capacity"] = max_capacity
        if min_capacity is not None:
            self._values["min_capacity"] = min_capacity
        if username is not None:
            self._values["username"] = username
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def engine(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_pause(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("auto_pause")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_capacity(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("max_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_capacity(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("min_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.DatabaseVariables",
    jsii_struct_bases=[],
    name_mapping={
        "database_host": "databaseHost",
        "database_name": "databaseName",
        "database_password": "databasePassword",
        "database_port": "databasePort",
        "database_type": "databaseType",
        "database_url": "databaseUrl",
        "database_username": "databaseUsername",
    },
)
class DatabaseVariables:
    def __init__(
        self,
        *,
        database_host: builtins.str,
        database_name: builtins.str,
        database_password: builtins.str,
        database_port: builtins.str,
        database_type: builtins.str,
        database_url: builtins.str,
        database_username: builtins.str,
    ) -> None:
        '''
        :param database_host: 
        :param database_name: 
        :param database_password: 
        :param database_port: 
        :param database_type: 
        :param database_url: 
        :param database_username: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "database_host": database_host,
            "database_name": database_name,
            "database_password": database_password,
            "database_port": database_port,
            "database_type": database_type,
            "database_url": database_url,
            "database_username": database_username,
        }

    @builtins.property
    def database_host(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_host")
        assert result is not None, "Required property 'database_host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_password(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_password")
        assert result is not None, "Required property 'database_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_port(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_port")
        assert result is not None, "Required property 'database_port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_type")
        assert result is not None, "Required property 'database_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_url")
        assert result is not None, "Required property 'database_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("database_username")
        assert result is not None, "Required property 'database_username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Domain(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.Domain",
):
    '''
    :stability: experimental
    :order: 6
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        certificate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: The parent of this resource, for example a ``{@link "app#stacks" | Stack}``.
        :param id: -
        :param name: 
        :param certificate: 

        :stability: experimental
        '''
        props = DomainProps(name=name, certificate=certificate)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAaaaRecord")
    def add_aaaa_record(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        target_ip: builtins.str,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: -
        :param name: 
        :param target_ip: 
        :param ttl: 

        :stability: experimental
        '''
        props = ARecordProps(name=name, target_ip=target_ip, ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "addAaaaRecord", [id, props]))

    @jsii.member(jsii_name="addARecord")
    def add_a_record(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        target_ip: builtins.str,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: -
        :param name: 
        :param target_ip: 
        :param ttl: 

        :stability: experimental
        '''
        props = ARecordProps(name=name, target_ip=target_ip, ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "addARecord", [id, props]))

    @jsii.member(jsii_name="addCnameRecord")
    def add_cname_record(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        target: builtins.str,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: -
        :param name: 
        :param target: 
        :param ttl: 

        :stability: experimental
        '''
        props = CNameRecordProps(name=name, target=target, ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "addCnameRecord", [id, props]))

    @jsii.member(jsii_name="addMxRecords")
    def add_mx_records(
        self,
        id: builtins.str,
        *,
        values: typing.Sequence[aws_cdk.aws_route53.MxRecordValue],
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: -
        :param values: 
        :param ttl: 

        :stability: experimental
        '''
        props = MxRecordProps(values=values, ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "addMxRecords", [id, props]))

    @jsii.member(jsii_name="addTxtRecord")
    def add_txt_record(
        self,
        id: builtins.str,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param id: -
        :param name: 
        :param values: 
        :param ttl: 

        :stability: experimental
        '''
        props = TxtRecordProps(name=name, values=values, ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "addTxtRecord", [id, props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZone")
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.get(self, "hostedZone"))

    @hosted_zone.setter
    def hosted_zone(self, value: aws_cdk.aws_route53.IHostedZone) -> None:
        jsii.set(self, "hostedZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(
        self,
        value: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate],
    ) -> None:
        jsii.set(self, "certificate", value)


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.DomainProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "certificate": "certificate"},
)
class DomainProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        certificate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param name: 
        :param certificate: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if certificate is not None:
            self._values["certificate"] = certificate

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cloudcamp/aws-runtime.LanguageCode")
class LanguageCode(enum.Enum):
    '''(experimental) Language codes supported by CDK.

    :stability: experimental
    '''

    TYPESCRIPT = "TYPESCRIPT"
    '''
    :stability: experimental
    '''
    JAVASCRIPT = "JAVASCRIPT"
    '''
    :stability: experimental
    '''
    PYTHON = "PYTHON"
    '''
    :stability: experimental
    '''
    CSHARP = "CSHARP"
    '''
    :stability: experimental
    '''
    JAVA = "JAVA"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.MetricScalingProps",
    jsii_struct_bases=[],
    name_mapping={
        "max": "max",
        "min": "min",
        "cpu": "cpu",
        "memory": "memory",
        "request_count": "requestCount",
    },
)
class MetricScalingProps:
    def __init__(
        self,
        *,
        max: jsii.Number,
        min: jsii.Number,
        cpu: typing.Optional[jsii.Number] = None,
        memory: typing.Optional[jsii.Number] = None,
        request_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max: 
        :param min: 
        :param cpu: 
        :param memory: 
        :param request_count: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max": max,
            "min": min,
        }
        if cpu is not None:
            self._values["cpu"] = cpu
        if memory is not None:
            self._values["memory"] = memory
        if request_count is not None:
            self._values["request_count"] = request_count

    @builtins.property
    def max(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("max")
        assert result is not None, "Required property 'max' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("min")
        assert result is not None, "Required property 'min' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def request_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("request_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetricScalingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.MxRecordProps",
    jsii_struct_bases=[],
    name_mapping={"values": "values", "ttl": "ttl"},
)
class MxRecordProps:
    def __init__(
        self,
        *,
        values: typing.Sequence[aws_cdk.aws_route53.MxRecordValue],
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param values: 
        :param ttl: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "values": values,
        }
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def values(self) -> typing.List[aws_cdk.aws_route53.MxRecordValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[aws_cdk.aws_route53.MxRecordValue], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MxRecordProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PipelineStack(
    aws_cdk.core.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.PipelineStack",
):
    '''
    :stability: experimental
    :ignore: true
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        app_name: builtins.str,
        branch: builtins.str,
        host: "RepositoryHost",
        owner: builtins.str,
        repo: builtins.str,
        repository_token_secret_name: builtins.str,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.core.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_name: 
        :param branch: 
        :param host: 
        :param owner: 
        :param repo: 
        :param repository_token_secret_name: 
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        props = PipelineStackProps(
            app_name=app_name,
            branch=branch,
            host=host,
            owner=owner,
            repo=repo,
            repository_token_secret_name=repository_token_secret_name,
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> aws_cdk.pipelines.CdkPipeline:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.pipelines.CdkPipeline, jsii.get(self, "pipeline"))

    @pipeline.setter
    def pipeline(self, value: aws_cdk.pipelines.CdkPipeline) -> None:
        jsii.set(self, "pipeline", value)


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.PipelineStackProps",
    jsii_struct_bases=[aws_cdk.core.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "description": "description",
        "env": "env",
        "stack_name": "stackName",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "app_name": "appName",
        "branch": "branch",
        "host": "host",
        "owner": "owner",
        "repo": "repo",
        "repository_token_secret_name": "repositoryTokenSecretName",
    },
)
class PipelineStackProps(aws_cdk.core.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.core.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        app_name: builtins.str,
        branch: builtins.str,
        host: "RepositoryHost",
        owner: builtins.str,
        repo: builtins.str,
        repository_token_secret_name: builtins.str,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param app_name: 
        :param branch: 
        :param host: 
        :param owner: 
        :param repo: 
        :param repository_token_secret_name: 

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = aws_cdk.core.Environment(**env)
        self._values: typing.Dict[str, typing.Any] = {
            "app_name": app_name,
            "branch": branch,
            "host": host,
            "owner": owner,
            "repo": repo,
            "repository_token_secret_name": repository_token_secret_name,
        }
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[aws_cdk.core.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
            # Use a concrete account and region to deploy this stack to:
            # `.account` and `.region` will simply return these values.
            Stack(app, "Stack1",
                env={
                    "account": "123456789012",
                    "region": "us-east-1"
                }
            )
            
            # Use the CLI's current credentials to determine the target environment:
            # `.account` and `.region` will reflect the account+region the CLI
            # is configured to use (based on the user CLI credentials)
            Stack(app, "Stack2",
                env={
                    "account": process.env.CDK_DEFAULT_ACCOUNT,
                    "region": process.env.CDK_DEFAULT_REGION
                }
            )
            
            # Define multiple stacks stage associated with an environment
            my_stage = Stage(app, "MyStage",
                env={
                    "account": "123456789012",
                    "region": "us-east-1"
                }
            )
            
            # both of these stacks will use the stage's account/region:
            # `.account` and `.region` will resolve to the concrete values as above
            MyStack(my_stage, "Stack1")
            YourStack(my_stage, "Stack2")
            
            # Define an environment-agnostic stack:
            # `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            # which will only resolve to actual values by CloudFormation during deployment.
            MyStack(app, "Stack1")
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[aws_cdk.core.Environment], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[aws_cdk.core.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        :default:

        - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag
        is set, ``LegacyStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[aws_cdk.core.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Stack tags that will be applied to all the taggable resources and the stack itself.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def app_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("app_name")
        assert result is not None, "Required property 'app_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> "RepositoryHost":
        '''
        :stability: experimental
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast("RepositoryHost", result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("repo")
        assert result is not None, "Required property 'repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_token_secret_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("repository_token_secret_name")
        assert result is not None, "Required property 'repository_token_secret_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PipelineStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ref(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.Ref",
):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="addCertificate") # type: ignore[misc]
    @builtins.classmethod
    def add_certificate(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificate: -
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        props = RefParameterProps(app_name=app_name, name=name)

        return typing.cast(None, jsii.sinvoke(cls, "addCertificate", [scope, id, certificate, props]))

    @jsii.member(jsii_name="addHostedZone") # type: ignore[misc]
    @builtins.classmethod
    def add_hosted_zone(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: -
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        props = RefParameterProps(app_name=app_name, name=name)

        return typing.cast(None, jsii.sinvoke(cls, "addHostedZone", [scope, id, hosted_zone, props]))

    @jsii.member(jsii_name="addServerlessCluster") # type: ignore[misc]
    @builtins.classmethod
    def add_serverless_cluster(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        serverless_cluster: aws_cdk.aws_rds.IServerlessCluster,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param serverless_cluster: -
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        props = RefParameterProps(app_name=app_name, name=name)

        return typing.cast(None, jsii.sinvoke(cls, "addServerlessCluster", [scope, id, serverless_cluster, props]))

    @jsii.member(jsii_name="getCertificate") # type: ignore[misc]
    @builtins.classmethod
    def get_certificate(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> aws_cdk.aws_certificatemanager.ICertificate:
        '''
        :param scope: -
        :param id: -
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        props = RefParameterProps(app_name=app_name, name=name)

        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, jsii.sinvoke(cls, "getCertificate", [scope, id, props]))

    @jsii.member(jsii_name="getHostedZone") # type: ignore[misc]
    @builtins.classmethod
    def get_hosted_zone(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> aws_cdk.aws_route53.IHostedZone:
        '''
        :param scope: -
        :param id: -
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        props = RefParameterProps(app_name=app_name, name=name)

        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.sinvoke(cls, "getHostedZone", [scope, id, props]))

    @jsii.member(jsii_name="getServerlessCluster") # type: ignore[misc]
    @builtins.classmethod
    def get_serverless_cluster(
        cls,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> aws_cdk.aws_rds.IServerlessCluster:
        '''
        :param scope: -
        :param id: -
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        props = RefParameterProps(app_name=app_name, name=name)

        return typing.cast(aws_cdk.aws_rds.IServerlessCluster, jsii.sinvoke(cls, "getServerlessCluster", [scope, id, props]))


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.RefParameterProps",
    jsii_struct_bases=[],
    name_mapping={"app_name": "appName", "name": "name"},
)
class RefParameterProps:
    def __init__(
        self,
        *,
        app_name: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param app_name: 
        :param name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if app_name is not None:
            self._values["app_name"] = app_name
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def app_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("app_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RefParameterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cloudcamp/aws-runtime.RepositoryHost")
class RepositoryHost(enum.Enum):
    '''
    :stability: experimental
    '''

    GITHUB = "GITHUB"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.ScalingSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "day": "day",
        "hour": "hour",
        "minute": "minute",
        "month": "month",
        "week_day": "weekDay",
        "year": "year",
    },
)
class ScalingSchedule:
    def __init__(
        self,
        *,
        id: builtins.str,
        day: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        week_day: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: 
        :param day: (experimental) The day of the month to run this rule at. Default: - Every day of the month
        :param hour: (experimental) The hour to run this rule at. Default: - Every hour
        :param minute: (experimental) The minute to run this rule at. Default: - Every minute
        :param month: (experimental) The month to run this rule at. Default: - Every month
        :param week_day: (experimental) The day of the week to run this rule at. Default: - Any day of the week
        :param year: (experimental) The year to run this rule at. Default: - Every year

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if day is not None:
            self._values["day"] = day
        if hour is not None:
            self._values["hour"] = hour
        if minute is not None:
            self._values["minute"] = minute
        if month is not None:
            self._values["month"] = month
        if week_day is not None:
            self._values["week_day"] = week_day
        if year is not None:
            self._values["year"] = year

    @builtins.property
    def id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def day(self) -> typing.Optional[builtins.str]:
        '''(experimental) The day of the month to run this rule at.

        :default: - Every day of the month

        :stability: experimental
        '''
        result = self._values.get("day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hour(self) -> typing.Optional[builtins.str]:
        '''(experimental) The hour to run this rule at.

        :default: - Every hour

        :stability: experimental
        '''
        result = self._values.get("hour")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minute(self) -> typing.Optional[builtins.str]:
        '''(experimental) The minute to run this rule at.

        :default: - Every minute

        :stability: experimental
        '''
        result = self._values.get("minute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def month(self) -> typing.Optional[builtins.str]:
        '''(experimental) The month to run this rule at.

        :default: - Every month

        :stability: experimental
        '''
        result = self._values.get("month")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def week_day(self) -> typing.Optional[builtins.str]:
        '''(experimental) The day of the week to run this rule at.

        :default: - Any day of the week

        :stability: experimental
        '''
        result = self._values.get("week_day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def year(self) -> typing.Optional[builtins.str]:
        '''(experimental) The year to run this rule at.

        :default: - Every year

        :stability: experimental
        '''
        result = self._values.get("year")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScalingSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.ScheduleScalingProps",
    jsii_struct_bases=[],
    name_mapping={"max": "max", "min": "min", "schedule": "schedule"},
)
class ScheduleScalingProps:
    def __init__(
        self,
        *,
        max: jsii.Number,
        min: jsii.Number,
        schedule: typing.Sequence[ScalingSchedule],
    ) -> None:
        '''
        :param max: 
        :param min: 
        :param schedule: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "max": max,
            "min": min,
            "schedule": schedule,
        }

    @builtins.property
    def max(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("max")
        assert result is not None, "Required property 'max' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min(self) -> jsii.Number:
        '''
        :stability: experimental
        '''
        result = self._values.get("min")
        assert result is not None, "Required property 'min' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def schedule(self) -> typing.List[ScalingSchedule]:
        '''
        :stability: experimental
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(typing.List[ScalingSchedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleScalingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.SlackConfiguration",
    jsii_struct_bases=[],
    name_mapping={"channel_id": "channelId", "workspace_id": "workspaceId"},
)
class SlackConfiguration:
    def __init__(self, *, channel_id: builtins.str, workspace_id: builtins.str) -> None:
        '''
        :param channel_id: 
        :param workspace_id: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel_id": channel_id,
            "workspace_id": workspace_id,
        }

    @builtins.property
    def channel_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("channel_id")
        assert result is not None, "Required property 'channel_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workspace_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("workspace_id")
        assert result is not None, "Required property 'workspace_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Stack(
    aws_cdk.core.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.Stack",
):
    '''(experimental) Lorem ipsum dolor sit amet, consectetur adipiscing elit.

    Vivamus in convallis
    libero. Ut mattis massa quis dui consequat gravida. Maecenas tincidunt
    euismod metus vitae ornare. Phasellus non sapien tempor, mollis orci vel,
    faucibus quam. Mauris vel ligula sit amet lacus maximus vulputate. Nunc
    tincidunt dolor vehicula neque porta lobortis. Vivamus nec viverra magna. Sed
    diam massa, accumsan ut placerat vel, facilisis ut dui.

    :stability: experimental
    :order: 2
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[aws_cdk.core.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param synthesizer: Synthesis method to use while deploying this stack. Default: - ``DefaultStackSynthesizer`` if the ``@aws-cdk/core:newStyleStackSynthesis`` feature flag is set, ``LegacyStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        props = aws_cdk.core.StackProps(
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class Stage(
    aws_cdk.core.Stage,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.Stage",
):
    '''
    :stability: experimental
    :order: 3
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        env: typing.Optional[aws_cdk.core.Environment] = None,
        outdir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param env: Default AWS environment (account/region) for ``Stack``s in this ``Stage``. Stacks defined inside this ``Stage`` with either ``region`` or ``account`` missing from its env will use the corresponding field given here. If either ``region`` or ``account``is is not configured for ``Stack`` (either on the ``Stack`` itself or on the containing ``Stage``), the Stack will be *environment-agnostic*. Environment-agnostic stacks can be deployed to any environment, may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups, will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environments should be configured on the ``Stack``s.
        :param outdir: The output directory into which to emit synthesized artifacts. Can only be specified if this stage is the root stage (the app). If this is specified and this stage is nested within another stage, an error will be thrown. Default: - for nested stages, outdir will be determined as a relative directory to the outdir of the app. For apps, if outdir is not specified, a temporary directory will be created.

        :stability: experimental
        '''
        props = aws_cdk.core.StageProps(env=env, outdir=outdir)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="needsManualApproval")
    def needs_manual_approval(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "needsManualApproval"))

    @needs_manual_approval.setter
    def needs_manual_approval(self, value: builtins.bool) -> None:
        jsii.set(self, "needsManualApproval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stack")
    def stack(self) -> Stack:
        '''
        :stability: experimental
        '''
        return typing.cast(Stack, jsii.get(self, "stack"))

    @stack.setter
    def stack(self, value: Stack) -> None:
        jsii.set(self, "stack", value)


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.TxtRecordProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values", "ttl": "ttl"},
)
class TxtRecordProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param name: 
        :param values: 
        :param ttl: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TxtRecordProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebServer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcamp/aws-runtime.WebServer",
):
    '''(experimental) A scalable web server running one or more docker containers behind a load balancer.

    ``WebServer`` runs any web application behing a load balancers as docker
    containers. For example, this runs a web application as a single container
    exposed on port 8080::

       # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
       WebServer(app.production, "prod-web",
           dockerfile="../Dockerfile",
           port=8080
       )

    :stability: experimental
    :order: 4
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        dockerfile: builtins.str,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.Cluster] = None,
        cpu: typing.Optional[jsii.Number] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        health_check_path: typing.Optional[builtins.str] = None,
        memory: typing.Optional[jsii.Number] = None,
        port: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''(experimental) Initialize a new web server.

        *Examples:*

        To use your own domain and serve traffic via SSL, use the ``domain``
        and ``ssl`` properties::

           # Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
           WebServer(app.production, "prod",
               dockerfile="../Dockerfile",
               domain="example.com",
               ssl=True
           )

        See ``{@link "command/domain/#domain-create" | domain:create}`` and
        ``{@link "command/cert/#cert-create" | cert:create}`` for more information on
        setting up domains/SSL.

        :param scope: the parent, i.e. a stack.
        :param id: a unique identifier within the parent scope.
        :param dockerfile: (experimental) The path to the Dockerfile to run.
        :param certificate: 
        :param cluster: 
        :param cpu: (experimental) The number of cpu units. Valid values, which determines your range of valid values for the memory parameter: - 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB - 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB - 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB - 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments - 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments Default: 256
        :param desired_count: 
        :param domain: (experimental) TODO.
        :param domain_name: 
        :param domain_zone: 
        :param environment: (experimental) Environment variables.
        :param health_check_path: 
        :param memory: (experimental) The amount (in MiB) of memory. - 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) - 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) - 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) - Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) - Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Default: 512
        :param port: (experimental) The port exposed in the docker container. Default: 80
        :param vpc: 

        :stability: experimental
        :remarks:

        During initialization you can configure: Custom domains, SSL,
        machine configuration, health checks and the default number of instances.
        :topic: Initialization
        '''
        props = WebServerProps(
            dockerfile=dockerfile,
            certificate=certificate,
            cluster=cluster,
            cpu=cpu,
            desired_count=desired_count,
            domain=domain,
            domain_name=domain_name,
            domain_zone=domain_zone,
            environment=environment,
            health_check_path=health_check_path,
            memory=memory,
            port=port,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAlarms")
    def add_alarms(
        self,
        *,
        email: typing.Optional[typing.Sequence[builtins.str]] = None,
        http4xx: typing.Optional[AlarmConfiguration] = None,
        http5xx: typing.Optional[AlarmConfiguration] = None,
        rejected: typing.Optional[AlarmConfiguration] = None,
        slack: typing.Optional[SlackConfiguration] = None,
        slow: typing.Optional[AlarmConfiguration] = None,
        sms: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param email: 
        :param http4xx: 
        :param http5xx: 
        :param rejected: 
        :param slack: 
        :param slow: 
        :param sms: 

        :stability: experimental
        '''
        props = WebServerAlarmProps(
            email=email,
            http4xx=http4xx,
            http5xx=http5xx,
            rejected=rejected,
            slack=slack,
            slow=slow,
            sms=sms,
        )

        return typing.cast(None, jsii.invoke(self, "addAlarms", [props]))

    @jsii.member(jsii_name="scaleOnMetric")
    def scale_on_metric(
        self,
        *,
        max: jsii.Number,
        min: jsii.Number,
        cpu: typing.Optional[jsii.Number] = None,
        memory: typing.Optional[jsii.Number] = None,
        request_count: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max: 
        :param min: 
        :param cpu: 
        :param memory: 
        :param request_count: 

        :stability: experimental
        '''
        props = MetricScalingProps(
            max=max, min=min, cpu=cpu, memory=memory, request_count=request_count
        )

        return typing.cast(None, jsii.invoke(self, "scaleOnMetric", [props]))

    @jsii.member(jsii_name="scaleOnSchedule")
    def scale_on_schedule(
        self,
        *,
        max: jsii.Number,
        min: jsii.Number,
        schedule: typing.Sequence[ScalingSchedule],
    ) -> None:
        '''
        :param max: 
        :param min: 
        :param schedule: 

        :stability: experimental
        '''
        props = ScheduleScalingProps(max=max, min=min, schedule=schedule)

        return typing.cast(None, jsii.invoke(self, "scaleOnSchedule", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fargateService")
    def fargate_service(
        self,
    ) -> aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService, jsii.get(self, "fargateService"))

    @fargate_service.setter
    def fargate_service(
        self,
        value: aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedFargateService,
    ) -> None:
        jsii.set(self, "fargateService", value)


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.WebServerAlarmProps",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "http4xx": "http4xx",
        "http5xx": "http5xx",
        "rejected": "rejected",
        "slack": "slack",
        "slow": "slow",
        "sms": "sms",
    },
)
class WebServerAlarmProps:
    def __init__(
        self,
        *,
        email: typing.Optional[typing.Sequence[builtins.str]] = None,
        http4xx: typing.Optional[AlarmConfiguration] = None,
        http5xx: typing.Optional[AlarmConfiguration] = None,
        rejected: typing.Optional[AlarmConfiguration] = None,
        slack: typing.Optional[SlackConfiguration] = None,
        slow: typing.Optional[AlarmConfiguration] = None,
        sms: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param email: 
        :param http4xx: 
        :param http5xx: 
        :param rejected: 
        :param slack: 
        :param slow: 
        :param sms: 

        :stability: experimental
        '''
        if isinstance(http4xx, dict):
            http4xx = AlarmConfiguration(**http4xx)
        if isinstance(http5xx, dict):
            http5xx = AlarmConfiguration(**http5xx)
        if isinstance(rejected, dict):
            rejected = AlarmConfiguration(**rejected)
        if isinstance(slack, dict):
            slack = SlackConfiguration(**slack)
        if isinstance(slow, dict):
            slow = AlarmConfiguration(**slow)
        self._values: typing.Dict[str, typing.Any] = {}
        if email is not None:
            self._values["email"] = email
        if http4xx is not None:
            self._values["http4xx"] = http4xx
        if http5xx is not None:
            self._values["http5xx"] = http5xx
        if rejected is not None:
            self._values["rejected"] = rejected
        if slack is not None:
            self._values["slack"] = slack
        if slow is not None:
            self._values["slow"] = slow
        if sms is not None:
            self._values["sms"] = sms

    @builtins.property
    def email(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def http4xx(self) -> typing.Optional[AlarmConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("http4xx")
        return typing.cast(typing.Optional[AlarmConfiguration], result)

    @builtins.property
    def http5xx(self) -> typing.Optional[AlarmConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("http5xx")
        return typing.cast(typing.Optional[AlarmConfiguration], result)

    @builtins.property
    def rejected(self) -> typing.Optional[AlarmConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("rejected")
        return typing.cast(typing.Optional[AlarmConfiguration], result)

    @builtins.property
    def slack(self) -> typing.Optional[SlackConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("slack")
        return typing.cast(typing.Optional[SlackConfiguration], result)

    @builtins.property
    def slow(self) -> typing.Optional[AlarmConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("slow")
        return typing.cast(typing.Optional[AlarmConfiguration], result)

    @builtins.property
    def sms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("sms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebServerAlarmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcamp/aws-runtime.WebServerProps",
    jsii_struct_bases=[],
    name_mapping={
        "dockerfile": "dockerfile",
        "certificate": "certificate",
        "cluster": "cluster",
        "cpu": "cpu",
        "desired_count": "desiredCount",
        "domain": "domain",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "environment": "environment",
        "health_check_path": "healthCheckPath",
        "memory": "memory",
        "port": "port",
        "vpc": "vpc",
    },
)
class WebServerProps:
    def __init__(
        self,
        *,
        dockerfile: builtins.str,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.Cluster] = None,
        cpu: typing.Optional[jsii.Number] = None,
        desired_count: typing.Optional[jsii.Number] = None,
        domain: typing.Optional[builtins.str] = None,
        domain_name: typing.Optional[builtins.str] = None,
        domain_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        health_check_path: typing.Optional[builtins.str] = None,
        memory: typing.Optional[jsii.Number] = None,
        port: typing.Optional[jsii.Number] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param dockerfile: (experimental) The path to the Dockerfile to run.
        :param certificate: 
        :param cluster: 
        :param cpu: (experimental) The number of cpu units. Valid values, which determines your range of valid values for the memory parameter: - 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB - 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB - 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB - 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB increments - 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB increments Default: 256
        :param desired_count: 
        :param domain: (experimental) TODO.
        :param domain_name: 
        :param domain_zone: 
        :param environment: (experimental) Environment variables.
        :param health_check_path: 
        :param memory: (experimental) The amount (in MiB) of memory. - 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) - 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) - 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) - Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) - Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Default: 512
        :param port: (experimental) The port exposed in the docker container. Default: 80
        :param vpc: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dockerfile": dockerfile,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if cluster is not None:
            self._values["cluster"] = cluster
        if cpu is not None:
            self._values["cpu"] = cpu
        if desired_count is not None:
            self._values["desired_count"] = desired_count
        if domain is not None:
            self._values["domain"] = domain
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if domain_zone is not None:
            self._values["domain_zone"] = domain_zone
        if environment is not None:
            self._values["environment"] = environment
        if health_check_path is not None:
            self._values["health_check_path"] = health_check_path
        if memory is not None:
            self._values["memory"] = memory
        if port is not None:
            self._values["port"] = port
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def dockerfile(self) -> builtins.str:
        '''(experimental) The path to the Dockerfile to run.

        :stability: experimental
        '''
        result = self._values.get("dockerfile")
        assert result is not None, "Required property 'dockerfile' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''
        :stability: experimental
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.Cluster]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.Cluster], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of cpu units.

        Valid values, which determines your range of valid values for the memory parameter:

        - 256 (.25 vCPU) - Available memory values: 0.5GB, 1GB, 2GB
        - 512 (.5 vCPU) - Available memory values: 1GB, 2GB, 3GB, 4GB
        - 1024 (1 vCPU) - Available memory values: 2GB, 3GB, 4GB, 5GB, 6GB, 7GB,
          8GB
        - 2048 (2 vCPU) - Available memory values: Between 4GB and 16GB in 1GB
          increments
        - 4096 (4 vCPU) - Available memory values: Between 8GB and 30GB in 1GB
          increments

        :default: 256

        :stability: experimental
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def desired_count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("desired_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''(experimental) TODO.

        :stability: experimental
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''
        :stability: experimental
        '''
        result = self._values.get("domain_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables.

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def health_check_path(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("health_check_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The amount (in MiB) of memory.

        - 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25
          vCPU)
        - 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu
          values: 512 (.5 vCPU)
        - 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7
          GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)
        - Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) -
          Available cpu values: 2048 (2 vCPU)
        - Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) -
          Available cpu values: 4096 (4 vCPU)

        :default: 512

        :stability: experimental
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The port exposed in the docker container.

        :default: 80

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''
        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebServerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ARecordProps",
    "AaaaRecordProps",
    "AlarmConfiguration",
    "App",
    "CNameRecordProps",
    "Configuration",
    "Database",
    "DatabaseProps",
    "DatabaseVariables",
    "Domain",
    "DomainProps",
    "LanguageCode",
    "MetricScalingProps",
    "MxRecordProps",
    "PipelineStack",
    "PipelineStackProps",
    "Ref",
    "RefParameterProps",
    "RepositoryHost",
    "ScalingSchedule",
    "ScheduleScalingProps",
    "SlackConfiguration",
    "Stack",
    "Stage",
    "TxtRecordProps",
    "WebServer",
    "WebServerAlarmProps",
    "WebServerProps",
]

publication.publish()
