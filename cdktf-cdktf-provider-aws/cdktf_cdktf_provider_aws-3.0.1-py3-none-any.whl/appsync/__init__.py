import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class AppsyncApiKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncApiKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html aws_appsync_api_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expires: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html aws_appsync_api_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#api_id AppsyncApiKey#api_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#description AppsyncApiKey#description}.
        :param expires: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#expires AppsyncApiKey#expires}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AppsyncApiKeyConfig(
            api_id=api_id,
            description=description,
            expires=expires,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExpires")
    def reset_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpires", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiIdInput")
    def api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expiresInput")
    def expires_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expiresInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="expires")
    def expires(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expires"))

    @expires.setter
    def expires(self, value: builtins.str) -> None:
        jsii.set(self, "expires", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncApiKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "api_id": "apiId",
        "description": "description",
        "expires": "expires",
    },
)
class AppsyncApiKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        api_id: builtins.str,
        description: typing.Optional[builtins.str] = None,
        expires: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS AppSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#api_id AppsyncApiKey#api_id}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#description AppsyncApiKey#description}.
        :param expires: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#expires AppsyncApiKey#expires}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if expires is not None:
            self._values["expires"] = expires

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#api_id AppsyncApiKey#api_id}.'''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#description AppsyncApiKey#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expires(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_api_key.html#expires AppsyncApiKey#expires}.'''
        result = self._values.get("expires")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncApiKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncDatasource(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html aws_appsync_datasource}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        dynamodb_config: typing.Optional["AppsyncDatasourceDynamodbConfig"] = None,
        elasticsearch_config: typing.Optional["AppsyncDatasourceElasticsearchConfig"] = None,
        http_config: typing.Optional["AppsyncDatasourceHttpConfig"] = None,
        lambda_config: typing.Optional["AppsyncDatasourceLambdaConfig"] = None,
        service_role_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html aws_appsync_datasource} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#api_id AppsyncDatasource#api_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#name AppsyncDatasource#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#type AppsyncDatasource#type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#description AppsyncDatasource#description}.
        :param dynamodb_config: dynamodb_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#dynamodb_config AppsyncDatasource#dynamodb_config}
        :param elasticsearch_config: elasticsearch_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#elasticsearch_config AppsyncDatasource#elasticsearch_config}
        :param http_config: http_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#http_config AppsyncDatasource#http_config}
        :param lambda_config: lambda_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#lambda_config AppsyncDatasource#lambda_config}
        :param service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#service_role_arn AppsyncDatasource#service_role_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AppsyncDatasourceConfig(
            api_id=api_id,
            name=name,
            type=type,
            description=description,
            dynamodb_config=dynamodb_config,
            elasticsearch_config=elasticsearch_config,
            http_config=http_config,
            lambda_config=lambda_config,
            service_role_arn=service_role_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDynamodbConfig")
    def put_dynamodb_config(
        self,
        *,
        table_name: builtins.str,
        region: typing.Optional[builtins.str] = None,
        use_caller_credentials: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#table_name AppsyncDatasource#table_name}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#region AppsyncDatasource#region}.
        :param use_caller_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#use_caller_credentials AppsyncDatasource#use_caller_credentials}.
        '''
        value = AppsyncDatasourceDynamodbConfig(
            table_name=table_name,
            region=region,
            use_caller_credentials=use_caller_credentials,
        )

        return typing.cast(None, jsii.invoke(self, "putDynamodbConfig", [value]))

    @jsii.member(jsii_name="putElasticsearchConfig")
    def put_elasticsearch_config(
        self,
        *,
        endpoint: builtins.str,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#endpoint AppsyncDatasource#endpoint}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#region AppsyncDatasource#region}.
        '''
        value = AppsyncDatasourceElasticsearchConfig(endpoint=endpoint, region=region)

        return typing.cast(None, jsii.invoke(self, "putElasticsearchConfig", [value]))

    @jsii.member(jsii_name="putHttpConfig")
    def put_http_config(self, *, endpoint: builtins.str) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#endpoint AppsyncDatasource#endpoint}.
        '''
        value = AppsyncDatasourceHttpConfig(endpoint=endpoint)

        return typing.cast(None, jsii.invoke(self, "putHttpConfig", [value]))

    @jsii.member(jsii_name="putLambdaConfig")
    def put_lambda_config(self, *, function_arn: builtins.str) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#function_arn AppsyncDatasource#function_arn}.
        '''
        value = AppsyncDatasourceLambdaConfig(function_arn=function_arn)

        return typing.cast(None, jsii.invoke(self, "putLambdaConfig", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDynamodbConfig")
    def reset_dynamodb_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDynamodbConfig", []))

    @jsii.member(jsii_name="resetElasticsearchConfig")
    def reset_elasticsearch_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticsearchConfig", []))

    @jsii.member(jsii_name="resetHttpConfig")
    def reset_http_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpConfig", []))

    @jsii.member(jsii_name="resetLambdaConfig")
    def reset_lambda_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaConfig", []))

    @jsii.member(jsii_name="resetServiceRoleArn")
    def reset_service_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceRoleArn", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbConfig")
    def dynamodb_config(self) -> "AppsyncDatasourceDynamodbConfigOutputReference":
        return typing.cast("AppsyncDatasourceDynamodbConfigOutputReference", jsii.get(self, "dynamodbConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchConfig")
    def elasticsearch_config(
        self,
    ) -> "AppsyncDatasourceElasticsearchConfigOutputReference":
        return typing.cast("AppsyncDatasourceElasticsearchConfigOutputReference", jsii.get(self, "elasticsearchConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpConfig")
    def http_config(self) -> "AppsyncDatasourceHttpConfigOutputReference":
        return typing.cast("AppsyncDatasourceHttpConfigOutputReference", jsii.get(self, "httpConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaConfig")
    def lambda_config(self) -> "AppsyncDatasourceLambdaConfigOutputReference":
        return typing.cast("AppsyncDatasourceLambdaConfigOutputReference", jsii.get(self, "lambdaConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiIdInput")
    def api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamodbConfigInput")
    def dynamodb_config_input(
        self,
    ) -> typing.Optional["AppsyncDatasourceDynamodbConfig"]:
        return typing.cast(typing.Optional["AppsyncDatasourceDynamodbConfig"], jsii.get(self, "dynamodbConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticsearchConfigInput")
    def elasticsearch_config_input(
        self,
    ) -> typing.Optional["AppsyncDatasourceElasticsearchConfig"]:
        return typing.cast(typing.Optional["AppsyncDatasourceElasticsearchConfig"], jsii.get(self, "elasticsearchConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpConfigInput")
    def http_config_input(self) -> typing.Optional["AppsyncDatasourceHttpConfig"]:
        return typing.cast(typing.Optional["AppsyncDatasourceHttpConfig"], jsii.get(self, "httpConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaConfigInput")
    def lambda_config_input(self) -> typing.Optional["AppsyncDatasourceLambdaConfig"]:
        return typing.cast(typing.Optional["AppsyncDatasourceLambdaConfig"], jsii.get(self, "lambdaConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArnInput")
    def service_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRoleArn"))

    @service_role_arn.setter
    def service_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "api_id": "apiId",
        "name": "name",
        "type": "type",
        "description": "description",
        "dynamodb_config": "dynamodbConfig",
        "elasticsearch_config": "elasticsearchConfig",
        "http_config": "httpConfig",
        "lambda_config": "lambdaConfig",
        "service_role_arn": "serviceRoleArn",
    },
)
class AppsyncDatasourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        api_id: builtins.str,
        name: builtins.str,
        type: builtins.str,
        description: typing.Optional[builtins.str] = None,
        dynamodb_config: typing.Optional["AppsyncDatasourceDynamodbConfig"] = None,
        elasticsearch_config: typing.Optional["AppsyncDatasourceElasticsearchConfig"] = None,
        http_config: typing.Optional["AppsyncDatasourceHttpConfig"] = None,
        lambda_config: typing.Optional["AppsyncDatasourceLambdaConfig"] = None,
        service_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS AppSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#api_id AppsyncDatasource#api_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#name AppsyncDatasource#name}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#type AppsyncDatasource#type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#description AppsyncDatasource#description}.
        :param dynamodb_config: dynamodb_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#dynamodb_config AppsyncDatasource#dynamodb_config}
        :param elasticsearch_config: elasticsearch_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#elasticsearch_config AppsyncDatasource#elasticsearch_config}
        :param http_config: http_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#http_config AppsyncDatasource#http_config}
        :param lambda_config: lambda_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#lambda_config AppsyncDatasource#lambda_config}
        :param service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#service_role_arn AppsyncDatasource#service_role_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(dynamodb_config, dict):
            dynamodb_config = AppsyncDatasourceDynamodbConfig(**dynamodb_config)
        if isinstance(elasticsearch_config, dict):
            elasticsearch_config = AppsyncDatasourceElasticsearchConfig(**elasticsearch_config)
        if isinstance(http_config, dict):
            http_config = AppsyncDatasourceHttpConfig(**http_config)
        if isinstance(lambda_config, dict):
            lambda_config = AppsyncDatasourceLambdaConfig(**lambda_config)
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "name": name,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if dynamodb_config is not None:
            self._values["dynamodb_config"] = dynamodb_config
        if elasticsearch_config is not None:
            self._values["elasticsearch_config"] = elasticsearch_config
        if http_config is not None:
            self._values["http_config"] = http_config
        if lambda_config is not None:
            self._values["lambda_config"] = lambda_config
        if service_role_arn is not None:
            self._values["service_role_arn"] = service_role_arn

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#api_id AppsyncDatasource#api_id}.'''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#name AppsyncDatasource#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#type AppsyncDatasource#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#description AppsyncDatasource#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dynamodb_config(self) -> typing.Optional["AppsyncDatasourceDynamodbConfig"]:
        '''dynamodb_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#dynamodb_config AppsyncDatasource#dynamodb_config}
        '''
        result = self._values.get("dynamodb_config")
        return typing.cast(typing.Optional["AppsyncDatasourceDynamodbConfig"], result)

    @builtins.property
    def elasticsearch_config(
        self,
    ) -> typing.Optional["AppsyncDatasourceElasticsearchConfig"]:
        '''elasticsearch_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#elasticsearch_config AppsyncDatasource#elasticsearch_config}
        '''
        result = self._values.get("elasticsearch_config")
        return typing.cast(typing.Optional["AppsyncDatasourceElasticsearchConfig"], result)

    @builtins.property
    def http_config(self) -> typing.Optional["AppsyncDatasourceHttpConfig"]:
        '''http_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#http_config AppsyncDatasource#http_config}
        '''
        result = self._values.get("http_config")
        return typing.cast(typing.Optional["AppsyncDatasourceHttpConfig"], result)

    @builtins.property
    def lambda_config(self) -> typing.Optional["AppsyncDatasourceLambdaConfig"]:
        '''lambda_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#lambda_config AppsyncDatasource#lambda_config}
        '''
        result = self._values.get("lambda_config")
        return typing.cast(typing.Optional["AppsyncDatasourceLambdaConfig"], result)

    @builtins.property
    def service_role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#service_role_arn AppsyncDatasource#service_role_arn}.'''
        result = self._values.get("service_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncDatasourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceDynamodbConfig",
    jsii_struct_bases=[],
    name_mapping={
        "table_name": "tableName",
        "region": "region",
        "use_caller_credentials": "useCallerCredentials",
    },
)
class AppsyncDatasourceDynamodbConfig:
    def __init__(
        self,
        *,
        table_name: builtins.str,
        region: typing.Optional[builtins.str] = None,
        use_caller_credentials: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param table_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#table_name AppsyncDatasource#table_name}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#region AppsyncDatasource#region}.
        :param use_caller_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#use_caller_credentials AppsyncDatasource#use_caller_credentials}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "table_name": table_name,
        }
        if region is not None:
            self._values["region"] = region
        if use_caller_credentials is not None:
            self._values["use_caller_credentials"] = use_caller_credentials

    @builtins.property
    def table_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#table_name AppsyncDatasource#table_name}.'''
        result = self._values.get("table_name")
        assert result is not None, "Required property 'table_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#region AppsyncDatasource#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_caller_credentials(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#use_caller_credentials AppsyncDatasource#use_caller_credentials}.'''
        result = self._values.get("use_caller_credentials")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncDatasourceDynamodbConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncDatasourceDynamodbConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceDynamodbConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetUseCallerCredentials")
    def reset_use_caller_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseCallerCredentials", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableNameInput")
    def table_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tableNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useCallerCredentialsInput")
    def use_caller_credentials_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useCallerCredentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @table_name.setter
    def table_name(self, value: builtins.str) -> None:
        jsii.set(self, "tableName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useCallerCredentials")
    def use_caller_credentials(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useCallerCredentials"))

    @use_caller_credentials.setter
    def use_caller_credentials(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useCallerCredentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncDatasourceDynamodbConfig]:
        return typing.cast(typing.Optional[AppsyncDatasourceDynamodbConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncDatasourceDynamodbConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceElasticsearchConfig",
    jsii_struct_bases=[],
    name_mapping={"endpoint": "endpoint", "region": "region"},
)
class AppsyncDatasourceElasticsearchConfig:
    def __init__(
        self,
        *,
        endpoint: builtins.str,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#endpoint AppsyncDatasource#endpoint}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#region AppsyncDatasource#region}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
        }
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#endpoint AppsyncDatasource#endpoint}.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#region AppsyncDatasource#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncDatasourceElasticsearchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncDatasourceElasticsearchConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceElasticsearchConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncDatasourceElasticsearchConfig]:
        return typing.cast(typing.Optional[AppsyncDatasourceElasticsearchConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncDatasourceElasticsearchConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceHttpConfig",
    jsii_struct_bases=[],
    name_mapping={"endpoint": "endpoint"},
)
class AppsyncDatasourceHttpConfig:
    def __init__(self, *, endpoint: builtins.str) -> None:
        '''
        :param endpoint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#endpoint AppsyncDatasource#endpoint}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
        }

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#endpoint AppsyncDatasource#endpoint}.'''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncDatasourceHttpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncDatasourceHttpConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceHttpConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: builtins.str) -> None:
        jsii.set(self, "endpoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncDatasourceHttpConfig]:
        return typing.cast(typing.Optional[AppsyncDatasourceHttpConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncDatasourceHttpConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceLambdaConfig",
    jsii_struct_bases=[],
    name_mapping={"function_arn": "functionArn"},
)
class AppsyncDatasourceLambdaConfig:
    def __init__(self, *, function_arn: builtins.str) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#function_arn AppsyncDatasource#function_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_arn": function_arn,
        }

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_datasource.html#function_arn AppsyncDatasource#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncDatasourceLambdaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncDatasourceLambdaConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncDatasourceLambdaConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArnInput")
    def function_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @function_arn.setter
    def function_arn(self, value: builtins.str) -> None:
        jsii.set(self, "functionArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncDatasourceLambdaConfig]:
        return typing.cast(typing.Optional[AppsyncDatasourceLambdaConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncDatasourceLambdaConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class AppsyncFunction(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncFunction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html aws_appsync_function}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        data_source: builtins.str,
        name: builtins.str,
        request_mapping_template: builtins.str,
        response_mapping_template: builtins.str,
        description: typing.Optional[builtins.str] = None,
        function_version: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html aws_appsync_function} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#api_id AppsyncFunction#api_id}.
        :param data_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#data_source AppsyncFunction#data_source}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#name AppsyncFunction#name}.
        :param request_mapping_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#request_mapping_template AppsyncFunction#request_mapping_template}.
        :param response_mapping_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#response_mapping_template AppsyncFunction#response_mapping_template}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#description AppsyncFunction#description}.
        :param function_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#function_version AppsyncFunction#function_version}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AppsyncFunctionConfig(
            api_id=api_id,
            data_source=data_source,
            name=name,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            description=description,
            function_version=function_version,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFunctionVersion")
    def reset_function_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionVersion", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionId")
    def function_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiIdInput")
    def api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceInput")
    def data_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersionInput")
    def function_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestMappingTemplateInput")
    def request_mapping_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestMappingTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseMappingTemplateInput")
    def response_mapping_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseMappingTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSource")
    def data_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSource"))

    @data_source.setter
    def data_source(self, value: builtins.str) -> None:
        jsii.set(self, "dataSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionVersion")
    def function_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionVersion"))

    @function_version.setter
    def function_version(self, value: builtins.str) -> None:
        jsii.set(self, "functionVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestMappingTemplate")
    def request_mapping_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestMappingTemplate"))

    @request_mapping_template.setter
    def request_mapping_template(self, value: builtins.str) -> None:
        jsii.set(self, "requestMappingTemplate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseMappingTemplate")
    def response_mapping_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseMappingTemplate"))

    @response_mapping_template.setter
    def response_mapping_template(self, value: builtins.str) -> None:
        jsii.set(self, "responseMappingTemplate", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncFunctionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "api_id": "apiId",
        "data_source": "dataSource",
        "name": "name",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
        "description": "description",
        "function_version": "functionVersion",
    },
)
class AppsyncFunctionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        api_id: builtins.str,
        data_source: builtins.str,
        name: builtins.str,
        request_mapping_template: builtins.str,
        response_mapping_template: builtins.str,
        description: typing.Optional[builtins.str] = None,
        function_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS AppSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#api_id AppsyncFunction#api_id}.
        :param data_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#data_source AppsyncFunction#data_source}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#name AppsyncFunction#name}.
        :param request_mapping_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#request_mapping_template AppsyncFunction#request_mapping_template}.
        :param response_mapping_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#response_mapping_template AppsyncFunction#response_mapping_template}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#description AppsyncFunction#description}.
        :param function_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#function_version AppsyncFunction#function_version}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "data_source": data_source,
            "name": name,
            "request_mapping_template": request_mapping_template,
            "response_mapping_template": response_mapping_template,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if function_version is not None:
            self._values["function_version"] = function_version

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#api_id AppsyncFunction#api_id}.'''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#data_source AppsyncFunction#data_source}.'''
        result = self._values.get("data_source")
        assert result is not None, "Required property 'data_source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#name AppsyncFunction#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def request_mapping_template(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#request_mapping_template AppsyncFunction#request_mapping_template}.'''
        result = self._values.get("request_mapping_template")
        assert result is not None, "Required property 'request_mapping_template' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def response_mapping_template(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#response_mapping_template AppsyncFunction#response_mapping_template}.'''
        result = self._values.get("response_mapping_template")
        assert result is not None, "Required property 'response_mapping_template' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#description AppsyncFunction#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def function_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_function.html#function_version AppsyncFunction#function_version}.'''
        result = self._values.get("function_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncFunctionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncGraphqlApi(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApi",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html aws_appsync_graphql_api}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authentication_type: builtins.str,
        name: builtins.str,
        additional_authentication_provider: typing.Optional[typing.Sequence["AppsyncGraphqlApiAdditionalAuthenticationProvider"]] = None,
        log_config: typing.Optional["AppsyncGraphqlApiLogConfig"] = None,
        openid_connect_config: typing.Optional["AppsyncGraphqlApiOpenidConnectConfig"] = None,
        schema: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_pool_config: typing.Optional["AppsyncGraphqlApiUserPoolConfig"] = None,
        xray_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html aws_appsync_graphql_api} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#authentication_type AppsyncGraphqlApi#authentication_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#name AppsyncGraphqlApi#name}.
        :param additional_authentication_provider: additional_authentication_provider block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#additional_authentication_provider AppsyncGraphqlApi#additional_authentication_provider}
        :param log_config: log_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#log_config AppsyncGraphqlApi#log_config}
        :param openid_connect_config: openid_connect_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#openid_connect_config AppsyncGraphqlApi#openid_connect_config}
        :param schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#schema AppsyncGraphqlApi#schema}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#tags AppsyncGraphqlApi#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#tags_all AppsyncGraphqlApi#tags_all}.
        :param user_pool_config: user_pool_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_config AppsyncGraphqlApi#user_pool_config}
        :param xray_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#xray_enabled AppsyncGraphqlApi#xray_enabled}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AppsyncGraphqlApiConfig(
            authentication_type=authentication_type,
            name=name,
            additional_authentication_provider=additional_authentication_provider,
            log_config=log_config,
            openid_connect_config=openid_connect_config,
            schema=schema,
            tags=tags,
            tags_all=tags_all,
            user_pool_config=user_pool_config,
            xray_enabled=xray_enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putLogConfig")
    def put_log_config(
        self,
        *,
        cloudwatch_logs_role_arn: builtins.str,
        field_log_level: builtins.str,
        exclude_verbose_content: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param cloudwatch_logs_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#cloudwatch_logs_role_arn AppsyncGraphqlApi#cloudwatch_logs_role_arn}.
        :param field_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#field_log_level AppsyncGraphqlApi#field_log_level}.
        :param exclude_verbose_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#exclude_verbose_content AppsyncGraphqlApi#exclude_verbose_content}.
        '''
        value = AppsyncGraphqlApiLogConfig(
            cloudwatch_logs_role_arn=cloudwatch_logs_role_arn,
            field_log_level=field_log_level,
            exclude_verbose_content=exclude_verbose_content,
        )

        return typing.cast(None, jsii.invoke(self, "putLogConfig", [value]))

    @jsii.member(jsii_name="putOpenidConnectConfig")
    def put_openid_connect_config(
        self,
        *,
        issuer: builtins.str,
        auth_ttl: typing.Optional[jsii.Number] = None,
        client_id: typing.Optional[builtins.str] = None,
        iat_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param issuer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#issuer AppsyncGraphqlApi#issuer}.
        :param auth_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#auth_ttl AppsyncGraphqlApi#auth_ttl}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#client_id AppsyncGraphqlApi#client_id}.
        :param iat_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#iat_ttl AppsyncGraphqlApi#iat_ttl}.
        '''
        value = AppsyncGraphqlApiOpenidConnectConfig(
            issuer=issuer, auth_ttl=auth_ttl, client_id=client_id, iat_ttl=iat_ttl
        )

        return typing.cast(None, jsii.invoke(self, "putOpenidConnectConfig", [value]))

    @jsii.member(jsii_name="putUserPoolConfig")
    def put_user_pool_config(
        self,
        *,
        default_action: builtins.str,
        user_pool_id: builtins.str,
        app_id_client_regex: typing.Optional[builtins.str] = None,
        aws_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#default_action AppsyncGraphqlApi#default_action}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_id AppsyncGraphqlApi#user_pool_id}.
        :param app_id_client_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#app_id_client_regex AppsyncGraphqlApi#app_id_client_regex}.
        :param aws_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#aws_region AppsyncGraphqlApi#aws_region}.
        '''
        value = AppsyncGraphqlApiUserPoolConfig(
            default_action=default_action,
            user_pool_id=user_pool_id,
            app_id_client_regex=app_id_client_regex,
            aws_region=aws_region,
        )

        return typing.cast(None, jsii.invoke(self, "putUserPoolConfig", [value]))

    @jsii.member(jsii_name="resetAdditionalAuthenticationProvider")
    def reset_additional_authentication_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalAuthenticationProvider", []))

    @jsii.member(jsii_name="resetLogConfig")
    def reset_log_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogConfig", []))

    @jsii.member(jsii_name="resetOpenidConnectConfig")
    def reset_openid_connect_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenidConnectConfig", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUserPoolConfig")
    def reset_user_pool_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserPoolConfig", []))

    @jsii.member(jsii_name="resetXrayEnabled")
    def reset_xray_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetXrayEnabled", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="uris")
    def uris(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "uris", [key]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logConfig")
    def log_config(self) -> "AppsyncGraphqlApiLogConfigOutputReference":
        return typing.cast("AppsyncGraphqlApiLogConfigOutputReference", jsii.get(self, "logConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openidConnectConfig")
    def openid_connect_config(
        self,
    ) -> "AppsyncGraphqlApiOpenidConnectConfigOutputReference":
        return typing.cast("AppsyncGraphqlApiOpenidConnectConfigOutputReference", jsii.get(self, "openidConnectConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolConfig")
    def user_pool_config(self) -> "AppsyncGraphqlApiUserPoolConfigOutputReference":
        return typing.cast("AppsyncGraphqlApiUserPoolConfigOutputReference", jsii.get(self, "userPoolConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalAuthenticationProviderInput")
    def additional_authentication_provider_input(
        self,
    ) -> typing.Optional[typing.List["AppsyncGraphqlApiAdditionalAuthenticationProvider"]]:
        return typing.cast(typing.Optional[typing.List["AppsyncGraphqlApiAdditionalAuthenticationProvider"]], jsii.get(self, "additionalAuthenticationProviderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationTypeInput")
    def authentication_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logConfigInput")
    def log_config_input(self) -> typing.Optional["AppsyncGraphqlApiLogConfig"]:
        return typing.cast(typing.Optional["AppsyncGraphqlApiLogConfig"], jsii.get(self, "logConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="openidConnectConfigInput")
    def openid_connect_config_input(
        self,
    ) -> typing.Optional["AppsyncGraphqlApiOpenidConnectConfig"]:
        return typing.cast(typing.Optional["AppsyncGraphqlApiOpenidConnectConfig"], jsii.get(self, "openidConnectConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolConfigInput")
    def user_pool_config_input(
        self,
    ) -> typing.Optional["AppsyncGraphqlApiUserPoolConfig"]:
        return typing.cast(typing.Optional["AppsyncGraphqlApiUserPoolConfig"], jsii.get(self, "userPoolConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xrayEnabledInput")
    def xray_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "xrayEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalAuthenticationProvider")
    def additional_authentication_provider(
        self,
    ) -> typing.List["AppsyncGraphqlApiAdditionalAuthenticationProvider"]:
        return typing.cast(typing.List["AppsyncGraphqlApiAdditionalAuthenticationProvider"], jsii.get(self, "additionalAuthenticationProvider"))

    @additional_authentication_provider.setter
    def additional_authentication_provider(
        self,
        value: typing.List["AppsyncGraphqlApiAdditionalAuthenticationProvider"],
    ) -> None:
        jsii.set(self, "additionalAuthenticationProvider", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationType")
    def authentication_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationType"))

    @authentication_type.setter
    def authentication_type(self, value: builtins.str) -> None:
        jsii.set(self, "authenticationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        jsii.set(self, "schema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xrayEnabled")
    def xray_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "xrayEnabled"))

    @xray_enabled.setter
    def xray_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "xrayEnabled", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiAdditionalAuthenticationProvider",
    jsii_struct_bases=[],
    name_mapping={
        "authentication_type": "authenticationType",
        "openid_connect_config": "openidConnectConfig",
        "user_pool_config": "userPoolConfig",
    },
)
class AppsyncGraphqlApiAdditionalAuthenticationProvider:
    def __init__(
        self,
        *,
        authentication_type: builtins.str,
        openid_connect_config: typing.Optional["AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig"] = None,
        user_pool_config: typing.Optional["AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig"] = None,
    ) -> None:
        '''
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#authentication_type AppsyncGraphqlApi#authentication_type}.
        :param openid_connect_config: openid_connect_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#openid_connect_config AppsyncGraphqlApi#openid_connect_config}
        :param user_pool_config: user_pool_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_config AppsyncGraphqlApi#user_pool_config}
        '''
        if isinstance(openid_connect_config, dict):
            openid_connect_config = AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig(**openid_connect_config)
        if isinstance(user_pool_config, dict):
            user_pool_config = AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig(**user_pool_config)
        self._values: typing.Dict[str, typing.Any] = {
            "authentication_type": authentication_type,
        }
        if openid_connect_config is not None:
            self._values["openid_connect_config"] = openid_connect_config
        if user_pool_config is not None:
            self._values["user_pool_config"] = user_pool_config

    @builtins.property
    def authentication_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#authentication_type AppsyncGraphqlApi#authentication_type}.'''
        result = self._values.get("authentication_type")
        assert result is not None, "Required property 'authentication_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def openid_connect_config(
        self,
    ) -> typing.Optional["AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig"]:
        '''openid_connect_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#openid_connect_config AppsyncGraphqlApi#openid_connect_config}
        '''
        result = self._values.get("openid_connect_config")
        return typing.cast(typing.Optional["AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig"], result)

    @builtins.property
    def user_pool_config(
        self,
    ) -> typing.Optional["AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig"]:
        '''user_pool_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_config AppsyncGraphqlApi#user_pool_config}
        '''
        result = self._values.get("user_pool_config")
        return typing.cast(typing.Optional["AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiAdditionalAuthenticationProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig",
    jsii_struct_bases=[],
    name_mapping={
        "issuer": "issuer",
        "auth_ttl": "authTtl",
        "client_id": "clientId",
        "iat_ttl": "iatTtl",
    },
)
class AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig:
    def __init__(
        self,
        *,
        issuer: builtins.str,
        auth_ttl: typing.Optional[jsii.Number] = None,
        client_id: typing.Optional[builtins.str] = None,
        iat_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param issuer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#issuer AppsyncGraphqlApi#issuer}.
        :param auth_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#auth_ttl AppsyncGraphqlApi#auth_ttl}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#client_id AppsyncGraphqlApi#client_id}.
        :param iat_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#iat_ttl AppsyncGraphqlApi#iat_ttl}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "issuer": issuer,
        }
        if auth_ttl is not None:
            self._values["auth_ttl"] = auth_ttl
        if client_id is not None:
            self._values["client_id"] = client_id
        if iat_ttl is not None:
            self._values["iat_ttl"] = iat_ttl

    @builtins.property
    def issuer(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#issuer AppsyncGraphqlApi#issuer}.'''
        result = self._values.get("issuer")
        assert result is not None, "Required property 'issuer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#auth_ttl AppsyncGraphqlApi#auth_ttl}.'''
        result = self._values.get("auth_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#client_id AppsyncGraphqlApi#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iat_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#iat_ttl AppsyncGraphqlApi#iat_ttl}.'''
        result = self._values.get("iat_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAuthTtl")
    def reset_auth_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthTtl", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetIatTtl")
    def reset_iat_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIatTtl", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTtlInput")
    def auth_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "authTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iatTtlInput")
    def iat_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iatTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuerInput")
    def issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTtl")
    def auth_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "authTtl"))

    @auth_ttl.setter
    def auth_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "authTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iatTtl")
    def iat_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iatTtl"))

    @iat_ttl.setter
    def iat_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "iatTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        jsii.set(self, "issuer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig]:
        return typing.cast(typing.Optional[AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig",
    jsii_struct_bases=[],
    name_mapping={
        "user_pool_id": "userPoolId",
        "app_id_client_regex": "appIdClientRegex",
        "aws_region": "awsRegion",
    },
)
class AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig:
    def __init__(
        self,
        *,
        user_pool_id: builtins.str,
        app_id_client_regex: typing.Optional[builtins.str] = None,
        aws_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_id AppsyncGraphqlApi#user_pool_id}.
        :param app_id_client_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#app_id_client_regex AppsyncGraphqlApi#app_id_client_regex}.
        :param aws_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#aws_region AppsyncGraphqlApi#aws_region}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool_id": user_pool_id,
        }
        if app_id_client_regex is not None:
            self._values["app_id_client_regex"] = app_id_client_regex
        if aws_region is not None:
            self._values["aws_region"] = aws_region

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_id AppsyncGraphqlApi#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_id_client_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#app_id_client_regex AppsyncGraphqlApi#app_id_client_regex}.'''
        result = self._values.get("app_id_client_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#aws_region AppsyncGraphqlApi#aws_region}.'''
        result = self._values.get("aws_region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAppIdClientRegex")
    def reset_app_id_client_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppIdClientRegex", []))

    @jsii.member(jsii_name="resetAwsRegion")
    def reset_aws_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsRegion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdClientRegexInput")
    def app_id_client_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdClientRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsRegionInput")
    def aws_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsRegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdClientRegex")
    def app_id_client_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appIdClientRegex"))

    @app_id_client_regex.setter
    def app_id_client_regex(self, value: builtins.str) -> None:
        jsii.set(self, "appIdClientRegex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsRegion")
    def aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRegion"))

    @aws_region.setter
    def aws_region(self, value: builtins.str) -> None:
        jsii.set(self, "awsRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig]:
        return typing.cast(typing.Optional[AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "authentication_type": "authenticationType",
        "name": "name",
        "additional_authentication_provider": "additionalAuthenticationProvider",
        "log_config": "logConfig",
        "openid_connect_config": "openidConnectConfig",
        "schema": "schema",
        "tags": "tags",
        "tags_all": "tagsAll",
        "user_pool_config": "userPoolConfig",
        "xray_enabled": "xrayEnabled",
    },
)
class AppsyncGraphqlApiConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        authentication_type: builtins.str,
        name: builtins.str,
        additional_authentication_provider: typing.Optional[typing.Sequence[AppsyncGraphqlApiAdditionalAuthenticationProvider]] = None,
        log_config: typing.Optional["AppsyncGraphqlApiLogConfig"] = None,
        openid_connect_config: typing.Optional["AppsyncGraphqlApiOpenidConnectConfig"] = None,
        schema: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_pool_config: typing.Optional["AppsyncGraphqlApiUserPoolConfig"] = None,
        xray_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS AppSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param authentication_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#authentication_type AppsyncGraphqlApi#authentication_type}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#name AppsyncGraphqlApi#name}.
        :param additional_authentication_provider: additional_authentication_provider block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#additional_authentication_provider AppsyncGraphqlApi#additional_authentication_provider}
        :param log_config: log_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#log_config AppsyncGraphqlApi#log_config}
        :param openid_connect_config: openid_connect_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#openid_connect_config AppsyncGraphqlApi#openid_connect_config}
        :param schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#schema AppsyncGraphqlApi#schema}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#tags AppsyncGraphqlApi#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#tags_all AppsyncGraphqlApi#tags_all}.
        :param user_pool_config: user_pool_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_config AppsyncGraphqlApi#user_pool_config}
        :param xray_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#xray_enabled AppsyncGraphqlApi#xray_enabled}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(log_config, dict):
            log_config = AppsyncGraphqlApiLogConfig(**log_config)
        if isinstance(openid_connect_config, dict):
            openid_connect_config = AppsyncGraphqlApiOpenidConnectConfig(**openid_connect_config)
        if isinstance(user_pool_config, dict):
            user_pool_config = AppsyncGraphqlApiUserPoolConfig(**user_pool_config)
        self._values: typing.Dict[str, typing.Any] = {
            "authentication_type": authentication_type,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if additional_authentication_provider is not None:
            self._values["additional_authentication_provider"] = additional_authentication_provider
        if log_config is not None:
            self._values["log_config"] = log_config
        if openid_connect_config is not None:
            self._values["openid_connect_config"] = openid_connect_config
        if schema is not None:
            self._values["schema"] = schema
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if user_pool_config is not None:
            self._values["user_pool_config"] = user_pool_config
        if xray_enabled is not None:
            self._values["xray_enabled"] = xray_enabled

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def authentication_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#authentication_type AppsyncGraphqlApi#authentication_type}.'''
        result = self._values.get("authentication_type")
        assert result is not None, "Required property 'authentication_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#name AppsyncGraphqlApi#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_authentication_provider(
        self,
    ) -> typing.Optional[typing.List[AppsyncGraphqlApiAdditionalAuthenticationProvider]]:
        '''additional_authentication_provider block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#additional_authentication_provider AppsyncGraphqlApi#additional_authentication_provider}
        '''
        result = self._values.get("additional_authentication_provider")
        return typing.cast(typing.Optional[typing.List[AppsyncGraphqlApiAdditionalAuthenticationProvider]], result)

    @builtins.property
    def log_config(self) -> typing.Optional["AppsyncGraphqlApiLogConfig"]:
        '''log_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#log_config AppsyncGraphqlApi#log_config}
        '''
        result = self._values.get("log_config")
        return typing.cast(typing.Optional["AppsyncGraphqlApiLogConfig"], result)

    @builtins.property
    def openid_connect_config(
        self,
    ) -> typing.Optional["AppsyncGraphqlApiOpenidConnectConfig"]:
        '''openid_connect_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#openid_connect_config AppsyncGraphqlApi#openid_connect_config}
        '''
        result = self._values.get("openid_connect_config")
        return typing.cast(typing.Optional["AppsyncGraphqlApiOpenidConnectConfig"], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#schema AppsyncGraphqlApi#schema}.'''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#tags AppsyncGraphqlApi#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#tags_all AppsyncGraphqlApi#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def user_pool_config(self) -> typing.Optional["AppsyncGraphqlApiUserPoolConfig"]:
        '''user_pool_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_config AppsyncGraphqlApi#user_pool_config}
        '''
        result = self._values.get("user_pool_config")
        return typing.cast(typing.Optional["AppsyncGraphqlApiUserPoolConfig"], result)

    @builtins.property
    def xray_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#xray_enabled AppsyncGraphqlApi#xray_enabled}.'''
        result = self._values.get("xray_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiLogConfig",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_logs_role_arn": "cloudwatchLogsRoleArn",
        "field_log_level": "fieldLogLevel",
        "exclude_verbose_content": "excludeVerboseContent",
    },
)
class AppsyncGraphqlApiLogConfig:
    def __init__(
        self,
        *,
        cloudwatch_logs_role_arn: builtins.str,
        field_log_level: builtins.str,
        exclude_verbose_content: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param cloudwatch_logs_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#cloudwatch_logs_role_arn AppsyncGraphqlApi#cloudwatch_logs_role_arn}.
        :param field_log_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#field_log_level AppsyncGraphqlApi#field_log_level}.
        :param exclude_verbose_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#exclude_verbose_content AppsyncGraphqlApi#exclude_verbose_content}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cloudwatch_logs_role_arn": cloudwatch_logs_role_arn,
            "field_log_level": field_log_level,
        }
        if exclude_verbose_content is not None:
            self._values["exclude_verbose_content"] = exclude_verbose_content

    @builtins.property
    def cloudwatch_logs_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#cloudwatch_logs_role_arn AppsyncGraphqlApi#cloudwatch_logs_role_arn}.'''
        result = self._values.get("cloudwatch_logs_role_arn")
        assert result is not None, "Required property 'cloudwatch_logs_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field_log_level(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#field_log_level AppsyncGraphqlApi#field_log_level}.'''
        result = self._values.get("field_log_level")
        assert result is not None, "Required property 'field_log_level' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclude_verbose_content(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#exclude_verbose_content AppsyncGraphqlApi#exclude_verbose_content}.'''
        result = self._values.get("exclude_verbose_content")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiLogConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncGraphqlApiLogConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiLogConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetExcludeVerboseContent")
    def reset_exclude_verbose_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeVerboseContent", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsRoleArnInput")
    def cloudwatch_logs_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudwatchLogsRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeVerboseContentInput")
    def exclude_verbose_content_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "excludeVerboseContentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldLogLevelInput")
    def field_log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldLogLevelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchLogsRoleArn")
    def cloudwatch_logs_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudwatchLogsRoleArn"))

    @cloudwatch_logs_role_arn.setter
    def cloudwatch_logs_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "cloudwatchLogsRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludeVerboseContent")
    def exclude_verbose_content(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "excludeVerboseContent"))

    @exclude_verbose_content.setter
    def exclude_verbose_content(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "excludeVerboseContent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldLogLevel")
    def field_log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldLogLevel"))

    @field_log_level.setter
    def field_log_level(self, value: builtins.str) -> None:
        jsii.set(self, "fieldLogLevel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncGraphqlApiLogConfig]:
        return typing.cast(typing.Optional[AppsyncGraphqlApiLogConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncGraphqlApiLogConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiOpenidConnectConfig",
    jsii_struct_bases=[],
    name_mapping={
        "issuer": "issuer",
        "auth_ttl": "authTtl",
        "client_id": "clientId",
        "iat_ttl": "iatTtl",
    },
)
class AppsyncGraphqlApiOpenidConnectConfig:
    def __init__(
        self,
        *,
        issuer: builtins.str,
        auth_ttl: typing.Optional[jsii.Number] = None,
        client_id: typing.Optional[builtins.str] = None,
        iat_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param issuer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#issuer AppsyncGraphqlApi#issuer}.
        :param auth_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#auth_ttl AppsyncGraphqlApi#auth_ttl}.
        :param client_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#client_id AppsyncGraphqlApi#client_id}.
        :param iat_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#iat_ttl AppsyncGraphqlApi#iat_ttl}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "issuer": issuer,
        }
        if auth_ttl is not None:
            self._values["auth_ttl"] = auth_ttl
        if client_id is not None:
            self._values["client_id"] = client_id
        if iat_ttl is not None:
            self._values["iat_ttl"] = iat_ttl

    @builtins.property
    def issuer(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#issuer AppsyncGraphqlApi#issuer}.'''
        result = self._values.get("issuer")
        assert result is not None, "Required property 'issuer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#auth_ttl AppsyncGraphqlApi#auth_ttl}.'''
        result = self._values.get("auth_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#client_id AppsyncGraphqlApi#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iat_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#iat_ttl AppsyncGraphqlApi#iat_ttl}.'''
        result = self._values.get("iat_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiOpenidConnectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncGraphqlApiOpenidConnectConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiOpenidConnectConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAuthTtl")
    def reset_auth_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthTtl", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetIatTtl")
    def reset_iat_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIatTtl", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTtlInput")
    def auth_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "authTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iatTtlInput")
    def iat_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "iatTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuerInput")
    def issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authTtl")
    def auth_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "authTtl"))

    @auth_ttl.setter
    def auth_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "authTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        jsii.set(self, "clientId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iatTtl")
    def iat_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "iatTtl"))

    @iat_ttl.setter
    def iat_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "iatTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        jsii.set(self, "issuer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncGraphqlApiOpenidConnectConfig]:
        return typing.cast(typing.Optional[AppsyncGraphqlApiOpenidConnectConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncGraphqlApiOpenidConnectConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiUserPoolConfig",
    jsii_struct_bases=[],
    name_mapping={
        "default_action": "defaultAction",
        "user_pool_id": "userPoolId",
        "app_id_client_regex": "appIdClientRegex",
        "aws_region": "awsRegion",
    },
)
class AppsyncGraphqlApiUserPoolConfig:
    def __init__(
        self,
        *,
        default_action: builtins.str,
        user_pool_id: builtins.str,
        app_id_client_regex: typing.Optional[builtins.str] = None,
        aws_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param default_action: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#default_action AppsyncGraphqlApi#default_action}.
        :param user_pool_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_id AppsyncGraphqlApi#user_pool_id}.
        :param app_id_client_regex: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#app_id_client_regex AppsyncGraphqlApi#app_id_client_regex}.
        :param aws_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#aws_region AppsyncGraphqlApi#aws_region}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "default_action": default_action,
            "user_pool_id": user_pool_id,
        }
        if app_id_client_regex is not None:
            self._values["app_id_client_regex"] = app_id_client_regex
        if aws_region is not None:
            self._values["aws_region"] = aws_region

    @builtins.property
    def default_action(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#default_action AppsyncGraphqlApi#default_action}.'''
        result = self._values.get("default_action")
        assert result is not None, "Required property 'default_action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_pool_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#user_pool_id AppsyncGraphqlApi#user_pool_id}.'''
        result = self._values.get("user_pool_id")
        assert result is not None, "Required property 'user_pool_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_id_client_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#app_id_client_regex AppsyncGraphqlApi#app_id_client_regex}.'''
        result = self._values.get("app_id_client_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_graphql_api.html#aws_region AppsyncGraphqlApi#aws_region}.'''
        result = self._values.get("aws_region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncGraphqlApiUserPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncGraphqlApiUserPoolConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncGraphqlApiUserPoolConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAppIdClientRegex")
    def reset_app_id_client_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppIdClientRegex", []))

    @jsii.member(jsii_name="resetAwsRegion")
    def reset_aws_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsRegion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdClientRegexInput")
    def app_id_client_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdClientRegexInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsRegionInput")
    def aws_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsRegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultActionInput")
    def default_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolIdInput")
    def user_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPoolIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appIdClientRegex")
    def app_id_client_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appIdClientRegex"))

    @app_id_client_regex.setter
    def app_id_client_regex(self, value: builtins.str) -> None:
        jsii.set(self, "appIdClientRegex", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsRegion")
    def aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRegion"))

    @aws_region.setter
    def aws_region(self, value: builtins.str) -> None:
        jsii.set(self, "awsRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultAction")
    def default_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultAction"))

    @default_action.setter
    def default_action(self, value: builtins.str) -> None:
        jsii.set(self, "defaultAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolId")
    def user_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPoolId"))

    @user_pool_id.setter
    def user_pool_id(self, value: builtins.str) -> None:
        jsii.set(self, "userPoolId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncGraphqlApiUserPoolConfig]:
        return typing.cast(typing.Optional[AppsyncGraphqlApiUserPoolConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncGraphqlApiUserPoolConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class AppsyncResolver(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncResolver",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html aws_appsync_resolver}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_id: builtins.str,
        field: builtins.str,
        type: builtins.str,
        caching_config: typing.Optional["AppsyncResolverCachingConfig"] = None,
        data_source: typing.Optional[builtins.str] = None,
        kind: typing.Optional[builtins.str] = None,
        pipeline_config: typing.Optional["AppsyncResolverPipelineConfig"] = None,
        request_template: typing.Optional[builtins.str] = None,
        response_template: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html aws_appsync_resolver} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#api_id AppsyncResolver#api_id}.
        :param field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#field AppsyncResolver#field}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#type AppsyncResolver#type}.
        :param caching_config: caching_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#caching_config AppsyncResolver#caching_config}
        :param data_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#data_source AppsyncResolver#data_source}.
        :param kind: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#kind AppsyncResolver#kind}.
        :param pipeline_config: pipeline_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#pipeline_config AppsyncResolver#pipeline_config}
        :param request_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#request_template AppsyncResolver#request_template}.
        :param response_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#response_template AppsyncResolver#response_template}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AppsyncResolverConfig(
            api_id=api_id,
            field=field,
            type=type,
            caching_config=caching_config,
            data_source=data_source,
            kind=kind,
            pipeline_config=pipeline_config,
            request_template=request_template,
            response_template=response_template,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCachingConfig")
    def put_caching_config(
        self,
        *,
        caching_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param caching_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#caching_keys AppsyncResolver#caching_keys}.
        :param ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#ttl AppsyncResolver#ttl}.
        '''
        value = AppsyncResolverCachingConfig(caching_keys=caching_keys, ttl=ttl)

        return typing.cast(None, jsii.invoke(self, "putCachingConfig", [value]))

    @jsii.member(jsii_name="putPipelineConfig")
    def put_pipeline_config(
        self,
        *,
        functions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param functions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#functions AppsyncResolver#functions}.
        '''
        value = AppsyncResolverPipelineConfig(functions=functions)

        return typing.cast(None, jsii.invoke(self, "putPipelineConfig", [value]))

    @jsii.member(jsii_name="resetCachingConfig")
    def reset_caching_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCachingConfig", []))

    @jsii.member(jsii_name="resetDataSource")
    def reset_data_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSource", []))

    @jsii.member(jsii_name="resetKind")
    def reset_kind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKind", []))

    @jsii.member(jsii_name="resetPipelineConfig")
    def reset_pipeline_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPipelineConfig", []))

    @jsii.member(jsii_name="resetRequestTemplate")
    def reset_request_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTemplate", []))

    @jsii.member(jsii_name="resetResponseTemplate")
    def reset_response_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseTemplate", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachingConfig")
    def caching_config(self) -> "AppsyncResolverCachingConfigOutputReference":
        return typing.cast("AppsyncResolverCachingConfigOutputReference", jsii.get(self, "cachingConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineConfig")
    def pipeline_config(self) -> "AppsyncResolverPipelineConfigOutputReference":
        return typing.cast("AppsyncResolverPipelineConfigOutputReference", jsii.get(self, "pipelineConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiIdInput")
    def api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachingConfigInput")
    def caching_config_input(self) -> typing.Optional["AppsyncResolverCachingConfig"]:
        return typing.cast(typing.Optional["AppsyncResolverCachingConfig"], jsii.get(self, "cachingConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceInput")
    def data_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldInput")
    def field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kindInput")
    def kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kindInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pipelineConfigInput")
    def pipeline_config_input(self) -> typing.Optional["AppsyncResolverPipelineConfig"]:
        return typing.cast(typing.Optional["AppsyncResolverPipelineConfig"], jsii.get(self, "pipelineConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestTemplateInput")
    def request_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplateInput")
    def response_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseTemplateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        jsii.set(self, "apiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSource")
    def data_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSource"))

    @data_source.setter
    def data_source(self, value: builtins.str) -> None:
        jsii.set(self, "dataSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @field.setter
    def field(self, value: builtins.str) -> None:
        jsii.set(self, "field", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @kind.setter
    def kind(self, value: builtins.str) -> None:
        jsii.set(self, "kind", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="requestTemplate")
    def request_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestTemplate"))

    @request_template.setter
    def request_template(self, value: builtins.str) -> None:
        jsii.set(self, "requestTemplate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseTemplate")
    def response_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseTemplate"))

    @response_template.setter
    def response_template(self, value: builtins.str) -> None:
        jsii.set(self, "responseTemplate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncResolverCachingConfig",
    jsii_struct_bases=[],
    name_mapping={"caching_keys": "cachingKeys", "ttl": "ttl"},
)
class AppsyncResolverCachingConfig:
    def __init__(
        self,
        *,
        caching_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param caching_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#caching_keys AppsyncResolver#caching_keys}.
        :param ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#ttl AppsyncResolver#ttl}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if caching_keys is not None:
            self._values["caching_keys"] = caching_keys
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def caching_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#caching_keys AppsyncResolver#caching_keys}.'''
        result = self._values.get("caching_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#ttl AppsyncResolver#ttl}.'''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncResolverCachingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncResolverCachingConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncResolverCachingConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetCachingKeys")
    def reset_caching_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCachingKeys", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachingKeysInput")
    def caching_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cachingKeysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachingKeys")
    def caching_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cachingKeys"))

    @caching_keys.setter
    def caching_keys(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "cachingKeys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "ttl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncResolverCachingConfig]:
        return typing.cast(typing.Optional[AppsyncResolverCachingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncResolverCachingConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncResolverConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "api_id": "apiId",
        "field": "field",
        "type": "type",
        "caching_config": "cachingConfig",
        "data_source": "dataSource",
        "kind": "kind",
        "pipeline_config": "pipelineConfig",
        "request_template": "requestTemplate",
        "response_template": "responseTemplate",
    },
)
class AppsyncResolverConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        api_id: builtins.str,
        field: builtins.str,
        type: builtins.str,
        caching_config: typing.Optional[AppsyncResolverCachingConfig] = None,
        data_source: typing.Optional[builtins.str] = None,
        kind: typing.Optional[builtins.str] = None,
        pipeline_config: typing.Optional["AppsyncResolverPipelineConfig"] = None,
        request_template: typing.Optional[builtins.str] = None,
        response_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS AppSync.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param api_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#api_id AppsyncResolver#api_id}.
        :param field: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#field AppsyncResolver#field}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#type AppsyncResolver#type}.
        :param caching_config: caching_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#caching_config AppsyncResolver#caching_config}
        :param data_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#data_source AppsyncResolver#data_source}.
        :param kind: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#kind AppsyncResolver#kind}.
        :param pipeline_config: pipeline_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#pipeline_config AppsyncResolver#pipeline_config}
        :param request_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#request_template AppsyncResolver#request_template}.
        :param response_template: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#response_template AppsyncResolver#response_template}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(caching_config, dict):
            caching_config = AppsyncResolverCachingConfig(**caching_config)
        if isinstance(pipeline_config, dict):
            pipeline_config = AppsyncResolverPipelineConfig(**pipeline_config)
        self._values: typing.Dict[str, typing.Any] = {
            "api_id": api_id,
            "field": field,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if caching_config is not None:
            self._values["caching_config"] = caching_config
        if data_source is not None:
            self._values["data_source"] = data_source
        if kind is not None:
            self._values["kind"] = kind
        if pipeline_config is not None:
            self._values["pipeline_config"] = pipeline_config
        if request_template is not None:
            self._values["request_template"] = request_template
        if response_template is not None:
            self._values["response_template"] = response_template

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def api_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#api_id AppsyncResolver#api_id}.'''
        result = self._values.get("api_id")
        assert result is not None, "Required property 'api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#field AppsyncResolver#field}.'''
        result = self._values.get("field")
        assert result is not None, "Required property 'field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#type AppsyncResolver#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def caching_config(self) -> typing.Optional[AppsyncResolverCachingConfig]:
        '''caching_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#caching_config AppsyncResolver#caching_config}
        '''
        result = self._values.get("caching_config")
        return typing.cast(typing.Optional[AppsyncResolverCachingConfig], result)

    @builtins.property
    def data_source(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#data_source AppsyncResolver#data_source}.'''
        result = self._values.get("data_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kind(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#kind AppsyncResolver#kind}.'''
        result = self._values.get("kind")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pipeline_config(self) -> typing.Optional["AppsyncResolverPipelineConfig"]:
        '''pipeline_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#pipeline_config AppsyncResolver#pipeline_config}
        '''
        result = self._values.get("pipeline_config")
        return typing.cast(typing.Optional["AppsyncResolverPipelineConfig"], result)

    @builtins.property
    def request_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#request_template AppsyncResolver#request_template}.'''
        result = self._values.get("request_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#response_template AppsyncResolver#response_template}.'''
        result = self._values.get("response_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncResolverConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.appsync.AppsyncResolverPipelineConfig",
    jsii_struct_bases=[],
    name_mapping={"functions": "functions"},
)
class AppsyncResolverPipelineConfig:
    def __init__(
        self,
        *,
        functions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param functions: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#functions AppsyncResolver#functions}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if functions is not None:
            self._values["functions"] = functions

    @builtins.property
    def functions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/appsync_resolver.html#functions AppsyncResolver#functions}.'''
        result = self._values.get("functions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncResolverPipelineConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AppsyncResolverPipelineConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.appsync.AppsyncResolverPipelineConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetFunctions")
    def reset_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionsInput")
    def functions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "functionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functions")
    def functions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "functions"))

    @functions.setter
    def functions(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "functions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AppsyncResolverPipelineConfig]:
        return typing.cast(typing.Optional[AppsyncResolverPipelineConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AppsyncResolverPipelineConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "AppsyncApiKey",
    "AppsyncApiKeyConfig",
    "AppsyncDatasource",
    "AppsyncDatasourceConfig",
    "AppsyncDatasourceDynamodbConfig",
    "AppsyncDatasourceDynamodbConfigOutputReference",
    "AppsyncDatasourceElasticsearchConfig",
    "AppsyncDatasourceElasticsearchConfigOutputReference",
    "AppsyncDatasourceHttpConfig",
    "AppsyncDatasourceHttpConfigOutputReference",
    "AppsyncDatasourceLambdaConfig",
    "AppsyncDatasourceLambdaConfigOutputReference",
    "AppsyncFunction",
    "AppsyncFunctionConfig",
    "AppsyncGraphqlApi",
    "AppsyncGraphqlApiAdditionalAuthenticationProvider",
    "AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfig",
    "AppsyncGraphqlApiAdditionalAuthenticationProviderOpenidConnectConfigOutputReference",
    "AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfig",
    "AppsyncGraphqlApiAdditionalAuthenticationProviderUserPoolConfigOutputReference",
    "AppsyncGraphqlApiConfig",
    "AppsyncGraphqlApiLogConfig",
    "AppsyncGraphqlApiLogConfigOutputReference",
    "AppsyncGraphqlApiOpenidConnectConfig",
    "AppsyncGraphqlApiOpenidConnectConfigOutputReference",
    "AppsyncGraphqlApiUserPoolConfig",
    "AppsyncGraphqlApiUserPoolConfigOutputReference",
    "AppsyncResolver",
    "AppsyncResolverCachingConfig",
    "AppsyncResolverCachingConfigOutputReference",
    "AppsyncResolverConfig",
    "AppsyncResolverPipelineConfig",
    "AppsyncResolverPipelineConfigOutputReference",
]

publication.publish()
