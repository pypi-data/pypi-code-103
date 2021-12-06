DESCRIBE_FUNCTIONS = ("describe", "get", "search", "list")

DELETE_FUNCTIONS = (
    "delete",
    "disassociate",
    "reject",
    "deallocate",
    "unassign",
    "deregister",
    "deprovision",
    "revoke",
    "release",
    "terminate",
    "cancel",
    "disable",
)

CREATE_FUNCTIONS = (
    "create",
    "associate",
    "accept",
    "allocate",
    "assign",
    "register",
    "provision",
    "authorize",
    "run",
    "enable",
    "upload",
    "put",
    "publish",
)

NAME_PARAMETER = {
    "default": None,
    "doc": "A name, ID, or JMES search path to identify the resource",
    "param_type": "Text",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}


PRESENT_REQUEST_FORMAT = r"""
    result = dict(comment="", changes= None, name=name, result=True)

    {%- if (not function.hardcoded.is_idempotent) %}
    ret = await hub.exec.boto3.client.{{ function.hardcoded.service_name }}.{{ function.hardcoded.resource }}.id(
        ctx,
        jmes_path=name
    )
    if ret["status"]:
        # name is now the first id that matched the JMES search path
        name = ret["ret"]
    {% endif %}

    {{ function.hardcoded.resource_function_call }}
    before = {{ function.hardcoded.describe_function_call }}

    if before:
        result["comment"] = f"'{name}' already exists"
    else:
        try:
            ret = await {{ function.hardcoded.create_function }}(
                ctx,
                {{ "DryRun=ctx.test," if function.hardcoded.has_dry_run }}
                {{ "ClientToken=name," if function.hardcoded.has_client_token }}
                **{{ parameter.mapping.kwargs|default({}) }}
            )
            result["result"] = ret["status"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            ret["comment"] = f"Created '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = f"{e.__class__.__name__}: {e}"

    {{ function.hardcoded.waiter_call }}
    # TODO perform other modifications as needed here
    ...

    after = {{ function.hardcoded.describe_function_call }}
    result["changes"] = differ.deep_diff(before, after)
    return result
"""

ABSENT_REQUEST_FORMAT = r"""
    result = dict(comment="", changes= None, name=name, result=True)
    {%- if (not function.hardcoded.is_idempotent) %}
    ret = await hub.exec.boto3.client.{{ function.hardcoded.service_name }}.{{ function.hardcoded.resource }}.id(
        ctx,
        jmes_path=name
    )
    if ret["status"]:
        # name is now the first id that matched the JMES search path
        name = ret["ret"]
    {% endif %}

    {{ function.hardcoded.resource_function_call }}

    before = {{ function.hardcoded.describe_function_call }}

    if not before:
        result["comment"] = f"'{name}' already absent"
    else:
        try:
            ret = await {{ function.hardcoded.delete_function }}(
                ctx,
                {{ "DryRun=ctx.test," if function.hardcoded.has_dry_run }}
                {{ "ClientToken=name," if function.hardcoded.has_client_token }}
                **{{ parameter.mapping.kwargs|default({}) }}
            )
            result["result"] = ret["status"]
            if not result["result"]:
                result["comment"] = ret["comment"]
                return result
            result["comment"] = f"Deleted '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            result["comment"] = f"{e.__class__.__name__}: {e}"

    {{ function.hardcoded.waiter_call }}

    after = {{ function.hardcoded.describe_function_call }}
    result["changes"] = differ.deep_diff(before, after)
    return result
"""

DESCRIBE_REQUEST_FORMAT = r"""
    result = {}

    ret = await {{ function.hardcoded.list_function}}(ctx)
    if not ret["status"]:
        hub.log.debug(f"Could not describe {{ function.hardcoded.resource }} {ret['comment']}")
        return result

    for {{ function.hardcoded.resource }} in ret["ret"]["{{ function.hardcoded.list_item }}"]:
        new_{{ function.hardcoded.resource }} = [
            {{ function.hardcoded.present_params }}
        ]
        result[{{ function.hardcoded.resource }}["{{ function.hardcoded.resource }}Id"]] = {"{{ function.ref }}.present": new_{{ function.hardcoded.resource }}}

        for i, data in enumerate({{ function.hardcoded.resource }}.get("", ())):
            sub_{{ function.hardcoded.resource }} = copy.deepcopy(new_{{ function.hardcoded.resource }})

            # TODO check for subresouruces
            sub_{{ function.hardcoded.resource }}.append({})
            sub_{{ function.hardcoded.resource }}.append({"name": "{{ function.hardcoded.resource_id }}"})
            result[f"{{ function.hardcoded.resource_id }}-{i}"] = {"{{ function.ref }}.present": sub_{{ function.hardcoded.resource }}}

    return result
"""
