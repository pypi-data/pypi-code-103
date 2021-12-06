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


class ConnectContactFlow(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.connect.ConnectContactFlow",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html aws_connect_contact_flow}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_id: builtins.str,
        name: builtins.str,
        content: typing.Optional[builtins.str] = None,
        content_hash: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        filename: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["ConnectContactFlowTimeouts"] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html aws_connect_contact_flow} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#instance_id ConnectContactFlow#instance_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#name ConnectContactFlow#name}.
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#content ConnectContactFlow#content}.
        :param content_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#content_hash ConnectContactFlow#content_hash}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#description ConnectContactFlow#description}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#filename ConnectContactFlow#filename}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#tags ConnectContactFlow#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#tags_all ConnectContactFlow#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#timeouts ConnectContactFlow#timeouts}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#type ConnectContactFlow#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ConnectContactFlowConfig(
            instance_id=instance_id,
            name=name,
            content=content,
            content_hash=content_hash,
            description=description,
            filename=filename,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#create ConnectContactFlow#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#update ConnectContactFlow#update}.
        '''
        value = ConnectContactFlowTimeouts(create=create, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetContent")
    def reset_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContent", []))

    @jsii.member(jsii_name="resetContentHash")
    def reset_content_hash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentHash", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFilename")
    def reset_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFilename", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="contactFlowId")
    def contact_flow_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contactFlowId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ConnectContactFlowTimeoutsOutputReference":
        return typing.cast("ConnectContactFlowTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHashInput")
    def content_hash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentHashInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filenameInput")
    def filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["ConnectContactFlowTimeouts"]:
        return typing.cast(typing.Optional["ConnectContactFlowTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        jsii.set(self, "content", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentHash")
    def content_hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentHash"))

    @content_hash.setter
    def content_hash(self, value: builtins.str) -> None:
        jsii.set(self, "contentHash", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filename")
    def filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filename"))

    @filename.setter
    def filename(self, value: builtins.str) -> None:
        jsii.set(self, "filename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        jsii.set(self, "instanceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.connect.ConnectContactFlowConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_id": "instanceId",
        "name": "name",
        "content": "content",
        "content_hash": "contentHash",
        "description": "description",
        "filename": "filename",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "type": "type",
    },
)
class ConnectContactFlowConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_id: builtins.str,
        name: builtins.str,
        content: typing.Optional[builtins.str] = None,
        content_hash: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        filename: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["ConnectContactFlowTimeouts"] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Connect.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#instance_id ConnectContactFlow#instance_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#name ConnectContactFlow#name}.
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#content ConnectContactFlow#content}.
        :param content_hash: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#content_hash ConnectContactFlow#content_hash}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#description ConnectContactFlow#description}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#filename ConnectContactFlow#filename}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#tags ConnectContactFlow#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#tags_all ConnectContactFlow#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#timeouts ConnectContactFlow#timeouts}
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#type ConnectContactFlow#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = ConnectContactFlowTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_id": instance_id,
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
        if content is not None:
            self._values["content"] = content
        if content_hash is not None:
            self._values["content_hash"] = content_hash
        if description is not None:
            self._values["description"] = description
        if filename is not None:
            self._values["filename"] = filename
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if type is not None:
            self._values["type"] = type

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
    def instance_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#instance_id ConnectContactFlow#instance_id}.'''
        result = self._values.get("instance_id")
        assert result is not None, "Required property 'instance_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#name ConnectContactFlow#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#content ConnectContactFlow#content}.'''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_hash(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#content_hash ConnectContactFlow#content_hash}.'''
        result = self._values.get("content_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#description ConnectContactFlow#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#filename ConnectContactFlow#filename}.'''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#tags ConnectContactFlow#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#tags_all ConnectContactFlow#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ConnectContactFlowTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#timeouts ConnectContactFlow#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ConnectContactFlowTimeouts"], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#type ConnectContactFlow#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConnectContactFlowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.connect.ConnectContactFlowTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "update": "update"},
)
class ConnectContactFlowTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#create ConnectContactFlow#create}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#update ConnectContactFlow#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#create ConnectContactFlow#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_contact_flow.html#update ConnectContactFlow#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConnectContactFlowTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConnectContactFlowTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.connect.ConnectContactFlowTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ConnectContactFlowTimeouts]:
        return typing.cast(typing.Optional[ConnectContactFlowTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ConnectContactFlowTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ConnectInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.connect.ConnectInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html aws_connect_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity_management_type: builtins.str,
        inbound_calls_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        outbound_calls_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        auto_resolve_best_voices_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        contact_flow_logs_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        contact_lens_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        directory_id: typing.Optional[builtins.str] = None,
        early_media_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_alias: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["ConnectInstanceTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html aws_connect_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity_management_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#identity_management_type ConnectInstance#identity_management_type}.
        :param inbound_calls_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#inbound_calls_enabled ConnectInstance#inbound_calls_enabled}.
        :param outbound_calls_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#outbound_calls_enabled ConnectInstance#outbound_calls_enabled}.
        :param auto_resolve_best_voices_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#auto_resolve_best_voices_enabled ConnectInstance#auto_resolve_best_voices_enabled}.
        :param contact_flow_logs_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#contact_flow_logs_enabled ConnectInstance#contact_flow_logs_enabled}.
        :param contact_lens_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#contact_lens_enabled ConnectInstance#contact_lens_enabled}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#directory_id ConnectInstance#directory_id}.
        :param early_media_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#early_media_enabled ConnectInstance#early_media_enabled}.
        :param instance_alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#instance_alias ConnectInstance#instance_alias}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#timeouts ConnectInstance#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ConnectInstanceConfig(
            identity_management_type=identity_management_type,
            inbound_calls_enabled=inbound_calls_enabled,
            outbound_calls_enabled=outbound_calls_enabled,
            auto_resolve_best_voices_enabled=auto_resolve_best_voices_enabled,
            contact_flow_logs_enabled=contact_flow_logs_enabled,
            contact_lens_enabled=contact_lens_enabled,
            directory_id=directory_id,
            early_media_enabled=early_media_enabled,
            instance_alias=instance_alias,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#create ConnectInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#delete ConnectInstance#delete}.
        '''
        value = ConnectInstanceTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAutoResolveBestVoicesEnabled")
    def reset_auto_resolve_best_voices_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoResolveBestVoicesEnabled", []))

    @jsii.member(jsii_name="resetContactFlowLogsEnabled")
    def reset_contact_flow_logs_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContactFlowLogsEnabled", []))

    @jsii.member(jsii_name="resetContactLensEnabled")
    def reset_contact_lens_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContactLensEnabled", []))

    @jsii.member(jsii_name="resetDirectoryId")
    def reset_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDirectoryId", []))

    @jsii.member(jsii_name="resetEarlyMediaEnabled")
    def reset_early_media_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEarlyMediaEnabled", []))

    @jsii.member(jsii_name="resetInstanceAlias")
    def reset_instance_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceAlias", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="createdTime")
    def created_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ConnectInstanceTimeoutsOutputReference":
        return typing.cast("ConnectInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoResolveBestVoicesEnabledInput")
    def auto_resolve_best_voices_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoResolveBestVoicesEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactFlowLogsEnabledInput")
    def contact_flow_logs_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "contactFlowLogsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactLensEnabledInput")
    def contact_lens_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "contactLensEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIdInput")
    def directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyMediaEnabledInput")
    def early_media_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "earlyMediaEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityManagementTypeInput")
    def identity_management_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityManagementTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inboundCallsEnabledInput")
    def inbound_calls_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "inboundCallsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAliasInput")
    def instance_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceAliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outboundCallsEnabledInput")
    def outbound_calls_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "outboundCallsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["ConnectInstanceTimeouts"]:
        return typing.cast(typing.Optional["ConnectInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoResolveBestVoicesEnabled")
    def auto_resolve_best_voices_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoResolveBestVoicesEnabled"))

    @auto_resolve_best_voices_enabled.setter
    def auto_resolve_best_voices_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoResolveBestVoicesEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactFlowLogsEnabled")
    def contact_flow_logs_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "contactFlowLogsEnabled"))

    @contact_flow_logs_enabled.setter
    def contact_flow_logs_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "contactFlowLogsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactLensEnabled")
    def contact_lens_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "contactLensEnabled"))

    @contact_lens_enabled.setter
    def contact_lens_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "contactLensEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyMediaEnabled")
    def early_media_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "earlyMediaEnabled"))

    @early_media_enabled.setter
    def early_media_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "earlyMediaEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityManagementType")
    def identity_management_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityManagementType"))

    @identity_management_type.setter
    def identity_management_type(self, value: builtins.str) -> None:
        jsii.set(self, "identityManagementType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inboundCallsEnabled")
    def inbound_calls_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "inboundCallsEnabled"))

    @inbound_calls_enabled.setter
    def inbound_calls_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "inboundCallsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAlias")
    def instance_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceAlias"))

    @instance_alias.setter
    def instance_alias(self, value: builtins.str) -> None:
        jsii.set(self, "instanceAlias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outboundCallsEnabled")
    def outbound_calls_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "outboundCallsEnabled"))

    @outbound_calls_enabled.setter
    def outbound_calls_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "outboundCallsEnabled", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.connect.ConnectInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity_management_type": "identityManagementType",
        "inbound_calls_enabled": "inboundCallsEnabled",
        "outbound_calls_enabled": "outboundCallsEnabled",
        "auto_resolve_best_voices_enabled": "autoResolveBestVoicesEnabled",
        "contact_flow_logs_enabled": "contactFlowLogsEnabled",
        "contact_lens_enabled": "contactLensEnabled",
        "directory_id": "directoryId",
        "early_media_enabled": "earlyMediaEnabled",
        "instance_alias": "instanceAlias",
        "timeouts": "timeouts",
    },
)
class ConnectInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity_management_type: builtins.str,
        inbound_calls_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        outbound_calls_enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        auto_resolve_best_voices_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        contact_flow_logs_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        contact_lens_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        directory_id: typing.Optional[builtins.str] = None,
        early_media_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_alias: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["ConnectInstanceTimeouts"] = None,
    ) -> None:
        '''AWS Connect.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity_management_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#identity_management_type ConnectInstance#identity_management_type}.
        :param inbound_calls_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#inbound_calls_enabled ConnectInstance#inbound_calls_enabled}.
        :param outbound_calls_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#outbound_calls_enabled ConnectInstance#outbound_calls_enabled}.
        :param auto_resolve_best_voices_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#auto_resolve_best_voices_enabled ConnectInstance#auto_resolve_best_voices_enabled}.
        :param contact_flow_logs_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#contact_flow_logs_enabled ConnectInstance#contact_flow_logs_enabled}.
        :param contact_lens_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#contact_lens_enabled ConnectInstance#contact_lens_enabled}.
        :param directory_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#directory_id ConnectInstance#directory_id}.
        :param early_media_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#early_media_enabled ConnectInstance#early_media_enabled}.
        :param instance_alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#instance_alias ConnectInstance#instance_alias}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#timeouts ConnectInstance#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = ConnectInstanceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "identity_management_type": identity_management_type,
            "inbound_calls_enabled": inbound_calls_enabled,
            "outbound_calls_enabled": outbound_calls_enabled,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_resolve_best_voices_enabled is not None:
            self._values["auto_resolve_best_voices_enabled"] = auto_resolve_best_voices_enabled
        if contact_flow_logs_enabled is not None:
            self._values["contact_flow_logs_enabled"] = contact_flow_logs_enabled
        if contact_lens_enabled is not None:
            self._values["contact_lens_enabled"] = contact_lens_enabled
        if directory_id is not None:
            self._values["directory_id"] = directory_id
        if early_media_enabled is not None:
            self._values["early_media_enabled"] = early_media_enabled
        if instance_alias is not None:
            self._values["instance_alias"] = instance_alias
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def identity_management_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#identity_management_type ConnectInstance#identity_management_type}.'''
        result = self._values.get("identity_management_type")
        assert result is not None, "Required property 'identity_management_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def inbound_calls_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#inbound_calls_enabled ConnectInstance#inbound_calls_enabled}.'''
        result = self._values.get("inbound_calls_enabled")
        assert result is not None, "Required property 'inbound_calls_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def outbound_calls_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#outbound_calls_enabled ConnectInstance#outbound_calls_enabled}.'''
        result = self._values.get("outbound_calls_enabled")
        assert result is not None, "Required property 'outbound_calls_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def auto_resolve_best_voices_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#auto_resolve_best_voices_enabled ConnectInstance#auto_resolve_best_voices_enabled}.'''
        result = self._values.get("auto_resolve_best_voices_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def contact_flow_logs_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#contact_flow_logs_enabled ConnectInstance#contact_flow_logs_enabled}.'''
        result = self._values.get("contact_flow_logs_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def contact_lens_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#contact_lens_enabled ConnectInstance#contact_lens_enabled}.'''
        result = self._values.get("contact_lens_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#directory_id ConnectInstance#directory_id}.'''
        result = self._values.get("directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def early_media_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#early_media_enabled ConnectInstance#early_media_enabled}.'''
        result = self._values.get("early_media_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#instance_alias ConnectInstance#instance_alias}.'''
        result = self._values.get("instance_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ConnectInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#timeouts ConnectInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ConnectInstanceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConnectInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.connect.ConnectInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class ConnectInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#create ConnectInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#delete ConnectInstance#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#create ConnectInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/connect_instance.html#delete ConnectInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConnectInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConnectInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.connect.ConnectInstanceTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ConnectInstanceTimeouts]:
        return typing.cast(typing.Optional[ConnectInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ConnectInstanceTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsConnectContactFlow(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.connect.DataAwsConnectContactFlow",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html aws_connect_contact_flow}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_id: builtins.str,
        contact_flow_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html aws_connect_contact_flow} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#instance_id DataAwsConnectContactFlow#instance_id}.
        :param contact_flow_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#contact_flow_id DataAwsConnectContactFlow#contact_flow_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#name DataAwsConnectContactFlow#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#tags DataAwsConnectContactFlow#tags}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#type DataAwsConnectContactFlow#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsConnectContactFlowConfig(
            instance_id=instance_id,
            contact_flow_id=contact_flow_id,
            name=name,
            tags=tags,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetContactFlowId")
    def reset_contact_flow_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContactFlowId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactFlowIdInput")
    def contact_flow_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contactFlowIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactFlowId")
    def contact_flow_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contactFlowId"))

    @contact_flow_id.setter
    def contact_flow_id(self, value: builtins.str) -> None:
        jsii.set(self, "contactFlowId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        jsii.set(self, "instanceId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.connect.DataAwsConnectContactFlowConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_id": "instanceId",
        "contact_flow_id": "contactFlowId",
        "name": "name",
        "tags": "tags",
        "type": "type",
    },
)
class DataAwsConnectContactFlowConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_id: builtins.str,
        contact_flow_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Connect.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#instance_id DataAwsConnectContactFlow#instance_id}.
        :param contact_flow_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#contact_flow_id DataAwsConnectContactFlow#contact_flow_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#name DataAwsConnectContactFlow#name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#tags DataAwsConnectContactFlow#tags}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#type DataAwsConnectContactFlow#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_id": instance_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if contact_flow_id is not None:
            self._values["contact_flow_id"] = contact_flow_id
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags
        if type is not None:
            self._values["type"] = type

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
    def instance_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#instance_id DataAwsConnectContactFlow#instance_id}.'''
        result = self._values.get("instance_id")
        assert result is not None, "Required property 'instance_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def contact_flow_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#contact_flow_id DataAwsConnectContactFlow#contact_flow_id}.'''
        result = self._values.get("contact_flow_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#name DataAwsConnectContactFlow#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#tags DataAwsConnectContactFlow#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_contact_flow.html#type DataAwsConnectContactFlow#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsConnectContactFlowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsConnectInstance(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.connect.DataAwsConnectInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html aws_connect_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        instance_alias: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html aws_connect_instance} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html#instance_alias DataAwsConnectInstance#instance_alias}.
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html#instance_id DataAwsConnectInstance#instance_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsConnectInstanceConfig(
            instance_alias=instance_alias,
            instance_id=instance_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetInstanceAlias")
    def reset_instance_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceAlias", []))

    @jsii.member(jsii_name="resetInstanceId")
    def reset_instance_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceId", []))

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
    @jsii.member(jsii_name="autoResolveBestVoicesEnabled")
    def auto_resolve_best_voices_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "autoResolveBestVoicesEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactFlowLogsEnabled")
    def contact_flow_logs_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "contactFlowLogsEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contactLensEnabled")
    def contact_lens_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "contactLensEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdTime")
    def created_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyMediaEnabled")
    def early_media_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "earlyMediaEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityManagementType")
    def identity_management_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityManagementType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inboundCallsEnabled")
    def inbound_calls_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "inboundCallsEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outboundCallsEnabled")
    def outbound_calls_enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "outboundCallsEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def service_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAliasInput")
    def instance_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceAliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceAlias")
    def instance_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceAlias"))

    @instance_alias.setter
    def instance_alias(self, value: builtins.str) -> None:
        jsii.set(self, "instanceAlias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        jsii.set(self, "instanceId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.connect.DataAwsConnectInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_alias": "instanceAlias",
        "instance_id": "instanceId",
    },
)
class DataAwsConnectInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_alias: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Connect.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_alias: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html#instance_alias DataAwsConnectInstance#instance_alias}.
        :param instance_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html#instance_id DataAwsConnectInstance#instance_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if instance_alias is not None:
            self._values["instance_alias"] = instance_alias
        if instance_id is not None:
            self._values["instance_id"] = instance_id

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
    def instance_alias(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html#instance_alias DataAwsConnectInstance#instance_alias}.'''
        result = self._values.get("instance_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/connect_instance.html#instance_id DataAwsConnectInstance#instance_id}.'''
        result = self._values.get("instance_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsConnectInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ConnectContactFlow",
    "ConnectContactFlowConfig",
    "ConnectContactFlowTimeouts",
    "ConnectContactFlowTimeoutsOutputReference",
    "ConnectInstance",
    "ConnectInstanceConfig",
    "ConnectInstanceTimeouts",
    "ConnectInstanceTimeoutsOutputReference",
    "DataAwsConnectContactFlow",
    "DataAwsConnectContactFlowConfig",
    "DataAwsConnectInstance",
    "DataAwsConnectInstanceConfig",
]

publication.publish()
