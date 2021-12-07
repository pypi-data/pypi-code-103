'''
# replace this
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

import aws_cdk.aws_apigatewayv2
import aws_cdk.aws_ec2
import aws_cdk.aws_ecr
import aws_cdk.aws_ecr_assets
import aws_cdk.aws_iam
import aws_cdk.aws_lambda_python
import aws_cdk.core


class ManagementAPI(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-minecraft-server.ManagementAPI",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        api_name: builtins.str,
        server_instance: "ServerInstance",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_name: 
        :param server_instance: 
        '''
        props = ManagementAPIProps(api_name=api_name, server_instance=server_instance)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAPIGateway")
    def management_api_gateway(self) -> aws_cdk.aws_apigatewayv2.HttpApi:
        return typing.cast(aws_cdk.aws_apigatewayv2.HttpApi, jsii.get(self, "managementAPIGateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shutdownServerLambda")
    def shutdown_server_lambda(self) -> aws_cdk.aws_lambda_python.PythonFunction:
        return typing.cast(aws_cdk.aws_lambda_python.PythonFunction, jsii.get(self, "shutdownServerLambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startServerLambda")
    def start_server_lambda(self) -> aws_cdk.aws_lambda_python.PythonFunction:
        return typing.cast(aws_cdk.aws_lambda_python.PythonFunction, jsii.get(self, "startServerLambda"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusLambda")
    def status_lambda(self) -> aws_cdk.aws_lambda_python.PythonFunction:
        return typing.cast(aws_cdk.aws_lambda_python.PythonFunction, jsii.get(self, "statusLambda"))


@jsii.data_type(
    jsii_type="cdk-minecraft-server.ManagementAPIProps",
    jsii_struct_bases=[],
    name_mapping={"api_name": "apiName", "server_instance": "serverInstance"},
)
class ManagementAPIProps:
    def __init__(
        self,
        *,
        api_name: builtins.str,
        server_instance: "ServerInstance",
    ) -> None:
        '''
        :param api_name: 
        :param server_instance: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_name": api_name,
            "server_instance": server_instance,
        }

    @builtins.property
    def api_name(self) -> builtins.str:
        result = self._values.get("api_name")
        assert result is not None, "Required property 'api_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_instance(self) -> "ServerInstance":
        result = self._values.get("server_instance")
        assert result is not None, "Required property 'server_instance' is missing"
        return typing.cast("ServerInstance", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagementAPIProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MinecraftServer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-minecraft-server.MinecraftServer",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        game_server_name: builtins.str,
        server_zip_path: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        additional_security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        custom_user_data_script: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        ec2_instance_class: typing.Optional[aws_cdk.aws_ec2.InstanceClass] = None,
        ec2_instance_name: typing.Optional[builtins.str] = None,
        ec2_instance_size: typing.Optional[aws_cdk.aws_ec2.InstanceSize] = None,
        server_management_api: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param game_server_name: Name for Minecraft server.
        :param server_zip_path: Path to zip folder for Minecraft server can be in s3 or local.
        :param vpc: The VPC to use for creating the Minecraft server's.
        :param additional_security_groups: Additional security groups.
        :param custom_user_data_script: Custom user data script.
        :param ec2_instance_class: The ec2 instance type for hosting the minecraft server. Default: - c5a
        :param ec2_instance_name: Name to be given to EC2 instance where minecraft server will run. Default: - the Minecraft server name will be used
        :param ec2_instance_size: The ec2 instance size for hosting the minecraft server. Default: - large
        :param server_management_api: Whether or not the server management API should be created as part of the deployment. The server api will allow you to do things such as start and stop your ec2 instance Default: true
        '''
        props = MinecraftServerProps(
            game_server_name=game_server_name,
            server_zip_path=server_zip_path,
            vpc=vpc,
            additional_security_groups=additional_security_groups,
            custom_user_data_script=custom_user_data_script,
            ec2_instance_class=ec2_instance_class,
            ec2_instance_name=ec2_instance_name,
            ec2_instance_size=ec2_instance_size,
            server_management_api=server_management_api,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverInstance")
    def server_instance(self) -> "ServerInstance":
        return typing.cast("ServerInstance", jsii.get(self, "serverInstance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAPI")
    def management_api(self) -> typing.Optional[ManagementAPI]:
        return typing.cast(typing.Optional[ManagementAPI], jsii.get(self, "managementAPI"))


@jsii.data_type(
    jsii_type="cdk-minecraft-server.MinecraftServerProps",
    jsii_struct_bases=[],
    name_mapping={
        "game_server_name": "gameServerName",
        "server_zip_path": "serverZipPath",
        "vpc": "vpc",
        "additional_security_groups": "additionalSecurityGroups",
        "custom_user_data_script": "customUserDataScript",
        "ec2_instance_class": "ec2InstanceClass",
        "ec2_instance_name": "ec2InstanceName",
        "ec2_instance_size": "ec2InstanceSize",
        "server_management_api": "serverManagementAPI",
    },
)
class MinecraftServerProps:
    def __init__(
        self,
        *,
        game_server_name: builtins.str,
        server_zip_path: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        additional_security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        custom_user_data_script: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        ec2_instance_class: typing.Optional[aws_cdk.aws_ec2.InstanceClass] = None,
        ec2_instance_name: typing.Optional[builtins.str] = None,
        ec2_instance_size: typing.Optional[aws_cdk.aws_ec2.InstanceSize] = None,
        server_management_api: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for creating Minecraft server.

        :param game_server_name: Name for Minecraft server.
        :param server_zip_path: Path to zip folder for Minecraft server can be in s3 or local.
        :param vpc: The VPC to use for creating the Minecraft server's.
        :param additional_security_groups: Additional security groups.
        :param custom_user_data_script: Custom user data script.
        :param ec2_instance_class: The ec2 instance type for hosting the minecraft server. Default: - c5a
        :param ec2_instance_name: Name to be given to EC2 instance where minecraft server will run. Default: - the Minecraft server name will be used
        :param ec2_instance_size: The ec2 instance size for hosting the minecraft server. Default: - large
        :param server_management_api: Whether or not the server management API should be created as part of the deployment. The server api will allow you to do things such as start and stop your ec2 instance Default: true
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "game_server_name": game_server_name,
            "server_zip_path": server_zip_path,
            "vpc": vpc,
        }
        if additional_security_groups is not None:
            self._values["additional_security_groups"] = additional_security_groups
        if custom_user_data_script is not None:
            self._values["custom_user_data_script"] = custom_user_data_script
        if ec2_instance_class is not None:
            self._values["ec2_instance_class"] = ec2_instance_class
        if ec2_instance_name is not None:
            self._values["ec2_instance_name"] = ec2_instance_name
        if ec2_instance_size is not None:
            self._values["ec2_instance_size"] = ec2_instance_size
        if server_management_api is not None:
            self._values["server_management_api"] = server_management_api

    @builtins.property
    def game_server_name(self) -> builtins.str:
        '''Name for Minecraft server.'''
        result = self._values.get("game_server_name")
        assert result is not None, "Required property 'game_server_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_zip_path(self) -> builtins.str:
        '''Path to zip folder for Minecraft server can be in s3 or local.

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            /some/directory / location / minecraft.zips3:
        '''
        result = self._values.get("server_zip_path")
        assert result is not None, "Required property 'server_zip_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use for creating the Minecraft server's.

        :attribute: true
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def additional_security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''Additional security groups.'''
        result = self._values.get("additional_security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def custom_user_data_script(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        '''Custom user data script.'''
        result = self._values.get("custom_user_data_script")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    @builtins.property
    def ec2_instance_class(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceClass]:
        '''The ec2 instance type for hosting the minecraft server.

        :default: - c5a
        '''
        result = self._values.get("ec2_instance_class")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceClass], result)

    @builtins.property
    def ec2_instance_name(self) -> typing.Optional[builtins.str]:
        '''Name to be given to EC2 instance where minecraft server will run.

        :default: - the Minecraft server name will be used
        '''
        result = self._values.get("ec2_instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instance_size(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceSize]:
        '''The ec2 instance size for hosting the minecraft server.

        :default: - large
        '''
        result = self._values.get("ec2_instance_size")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceSize], result)

    @builtins.property
    def server_management_api(self) -> typing.Optional[builtins.bool]:
        '''Whether or not the server management API should be created as part of the deployment.

        The server api will allow you to do things such as start
        and stop your ec2 instance

        :default: true
        '''
        result = self._values.get("server_management_api")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MinecraftServerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServerInstance(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-minecraft-server.ServerInstance",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        ec2_instance_name: builtins.str,
        game_server_name: builtins.str,
        server_zip_path: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        additional_security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        custom_user_data_script: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        ec2_instance_class: typing.Optional[aws_cdk.aws_ec2.InstanceClass] = None,
        ec2_instance_size: typing.Optional[aws_cdk.aws_ec2.InstanceSize] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ec2_instance_name: 
        :param game_server_name: 
        :param server_zip_path: 
        :param vpc: 
        :param additional_security_groups: 
        :param custom_user_data_script: 
        :param ec2_instance_class: 
        :param ec2_instance_size: 
        '''
        props = ServerInstanceProps(
            ec2_instance_name=ec2_instance_name,
            game_server_name=game_server_name,
            server_zip_path=server_zip_path,
            vpc=vpc,
            additional_security_groups=additional_security_groups,
            custom_user_data_script=custom_user_data_script,
            ec2_instance_class=ec2_instance_class,
            ec2_instance_size=ec2_instance_size,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUserDataScript")
    def custom_user_data_script(self) -> aws_cdk.aws_ec2.UserData:
        return typing.cast(aws_cdk.aws_ec2.UserData, jsii.get(self, "customUserDataScript"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSecurityGroup")
    def default_security_group(self) -> aws_cdk.aws_ec2.ISecurityGroup:
        return typing.cast(aws_cdk.aws_ec2.ISecurityGroup, jsii.get(self, "defaultSecurityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerFile")
    def docker_file(self) -> aws_cdk.aws_ecr_assets.DockerImageAsset:
        return typing.cast(aws_cdk.aws_ecr_assets.DockerImageAsset, jsii.get(self, "dockerFile"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2Ami")
    def ec2_ami(self) -> aws_cdk.aws_ec2.IMachineImage:
        return typing.cast(aws_cdk.aws_ec2.IMachineImage, jsii.get(self, "ec2Ami"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2Instance")
    def ec2_instance(self) -> aws_cdk.aws_ec2.Instance:
        return typing.cast(aws_cdk.aws_ec2.Instance, jsii.get(self, "ec2Instance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InstanceClass")
    def ec2_instance_class(self) -> aws_cdk.aws_ec2.InstanceClass:
        return typing.cast(aws_cdk.aws_ec2.InstanceClass, jsii.get(self, "ec2InstanceClass"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InstanceName")
    def ec2_instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2InstanceName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InstanceSize")
    def ec2_instance_size(self) -> aws_cdk.aws_ec2.InstanceSize:
        return typing.cast(aws_cdk.aws_ec2.InstanceSize, jsii.get(self, "ec2InstanceSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecrRepo")
    def ecr_repo(self) -> aws_cdk.aws_ecr.Repository:
        return typing.cast(aws_cdk.aws_ecr.Repository, jsii.get(self, "ecrRepo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fullInstanceType")
    def full_instance_type(self) -> aws_cdk.aws_ec2.InstanceType:
        return typing.cast(aws_cdk.aws_ec2.InstanceType, jsii.get(self, "fullInstanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gameServerName")
    def game_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gameServerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceRole")
    def instance_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "instanceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverZipPath")
    def server_zip_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverZipPath"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="cdk-minecraft-server.ServerInstanceProps",
    jsii_struct_bases=[],
    name_mapping={
        "ec2_instance_name": "ec2InstanceName",
        "game_server_name": "gameServerName",
        "server_zip_path": "serverZipPath",
        "vpc": "vpc",
        "additional_security_groups": "additionalSecurityGroups",
        "custom_user_data_script": "customUserDataScript",
        "ec2_instance_class": "ec2InstanceClass",
        "ec2_instance_size": "ec2InstanceSize",
    },
)
class ServerInstanceProps:
    def __init__(
        self,
        *,
        ec2_instance_name: builtins.str,
        game_server_name: builtins.str,
        server_zip_path: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        additional_security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        custom_user_data_script: typing.Optional[aws_cdk.aws_ec2.UserData] = None,
        ec2_instance_class: typing.Optional[aws_cdk.aws_ec2.InstanceClass] = None,
        ec2_instance_size: typing.Optional[aws_cdk.aws_ec2.InstanceSize] = None,
    ) -> None:
        '''
        :param ec2_instance_name: 
        :param game_server_name: 
        :param server_zip_path: 
        :param vpc: 
        :param additional_security_groups: 
        :param custom_user_data_script: 
        :param ec2_instance_class: 
        :param ec2_instance_size: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ec2_instance_name": ec2_instance_name,
            "game_server_name": game_server_name,
            "server_zip_path": server_zip_path,
            "vpc": vpc,
        }
        if additional_security_groups is not None:
            self._values["additional_security_groups"] = additional_security_groups
        if custom_user_data_script is not None:
            self._values["custom_user_data_script"] = custom_user_data_script
        if ec2_instance_class is not None:
            self._values["ec2_instance_class"] = ec2_instance_class
        if ec2_instance_size is not None:
            self._values["ec2_instance_size"] = ec2_instance_size

    @builtins.property
    def ec2_instance_name(self) -> builtins.str:
        result = self._values.get("ec2_instance_name")
        assert result is not None, "Required property 'ec2_instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def game_server_name(self) -> builtins.str:
        result = self._values.get("game_server_name")
        assert result is not None, "Required property 'game_server_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_zip_path(self) -> builtins.str:
        result = self._values.get("server_zip_path")
        assert result is not None, "Required property 'server_zip_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def additional_security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        result = self._values.get("additional_security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def custom_user_data_script(self) -> typing.Optional[aws_cdk.aws_ec2.UserData]:
        result = self._values.get("custom_user_data_script")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.UserData], result)

    @builtins.property
    def ec2_instance_class(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceClass]:
        result = self._values.get("ec2_instance_class")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceClass], result)

    @builtins.property
    def ec2_instance_size(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceSize]:
        result = self._values.get("ec2_instance_size")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceSize], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ManagementAPI",
    "ManagementAPIProps",
    "MinecraftServer",
    "MinecraftServerProps",
    "ServerInstance",
    "ServerInstanceProps",
]

publication.publish()
