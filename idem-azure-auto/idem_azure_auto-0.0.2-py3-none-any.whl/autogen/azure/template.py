NAME_PARAMETER = {
    "default": None,
    "doc": "The identifier for this state",
    "param_type": "str",
    "required": True,
    "target": "hardcoded",
    "target_type": "arg",
}


PRESENT_REQUEST_FORMAT = r"""
    subscription_id = ctx.acct.subscription_id
    response_get = {{ function.hardcoded.get_function }}(
        ctx,
        url=f"{{ function.hardcoded.path }}",
        success_codes=[200],
        headers=ctx.acct.headers,
    )

    if not response_get["result"]:
        if ctx.get("test", False):
            return StateReturn(
                name=name,
                result=True,
                comment="Would create azure.{{ function.hardcoded.create_ref }}"
            )

        if response_get["status"] == 404:
            # PUT operation to create a resource
            response_put = {{ function.hardcoded.create_function }}(
                ctx,
                url=f"{{ function.hardcoded.path }}",
                success_codes=[200, 201],
                headers=ctx.acct.headers,
                json=parameters,
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create {{ function.hardcoded.resource_name }} {response_put['comment']} {response_put['ret']}"
                )
                return StateReturn(
                    name=name, result=False, comment=response_put["comment"], error=response_put['ret']
                )

            return StateReturn(
                name=name,
                result=True,
                old_obj=None,
                new_obj=response_put["ret"],
                comment=response_put["comment"],
            )
        else:
            hub.log.debug(
                f"Could not get {{ function.hardcoded.resource_name }} {response_get['comment']} {response_get['ret']}"
            )
            return StateReturn(
                name=name, result=False, comment=response_get["comment"], error=response_get['ret']
            )
    {% if function.hardcoded.patch_parameters %}
    else:
        # PATCH operation to update a resource
        patch_parameters = {{ function.hardcoded.patch_parameters }}
        existing_resource = response_get["ret"]
        new_parameters = hub.tool.azure.utils.patch_json_content(patch_parameters, existing_resource, parameters)
        if ctx.get("test", False):
            return StateReturn(
                name=name,
                result=True,
                comment=f"Would update azure.{{ function.hardcoded.create_ref }} with parameters: {new_parameters}"
            )

        if not new_parameters:
            return StateReturn(
                name=name,
                result=True,
                old_obj=existing_resource,
                new_obj=existing_resource,
                comment=f"'{name}' has no property need to be updated.",
            )

        response_patch = {{ function.hardcoded.patch_function }}(
            ctx,
            url=f"{{ function.hardcoded.path }}",
            success_codes=[200],
            headers=ctx.acct.headers,
            json=new_parameters,
        )

        if not response_patch["result"]:
            hub.log.debug(
                f"Could not update {{ function.hardcoded.resource_name }} {response_patch['comment']} {response_patch['ret']}"
            )
            return StateReturn(
                name=name, result=False, comment=response_patch["comment"], error=response_patch['ret']
            )

        return StateReturn(
            name=name,
            result=True,
            old_obj=existing_resource,
            new_obj=response_patch["ret"],
            comment=response_patch["comment"],
        )
    {% else %}
    # No update operation on {{ function.hardcoded.resource_name }} since Azure does not have PATCH api on {{ function.hardcoded.resource_name }}
    return StateReturn(
        name=name,
        result=True,
        old_obj=response_get["ret"],
        new_obj=response_get["ret"],
        comment=response_get["comment"],
    )
    {% endif %}
"""

ABSENT_REQUEST_FORMAT = r"""
    subscription_id = ctx.acct.subscription_id
    response_get = {{ function.hardcoded.get_function }}(
        ctx,
        url=f"{{ function.hardcoded.path }}",
        success_codes=[200],
        headers=ctx.acct.headers,
    )
    if response_get["result"]:
        if ctx.get("test", False):
            return StateReturn(
                name=name,
                result=True,
                comment="Would delete azure.{{ function.hardcoded.create_ref }}"
            )

        existing_resource = response_get["ret"]
        response_delete = {{ function.hardcoded.delete_function }}(
            ctx,
            url=f"{{ function.hardcoded.path }}",
            success_codes=[200, 202, 204],
            headers=ctx.acct.headers,
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete {{ function.hardcoded.resource_name }} {response_delete['comment']} {response_delete['ret']}"
            )
            return StateReturn(
                name=name, result=False, comment=response_delete["comment"], error=response_delete['ret']
            )

        return StateReturn(
            name=name,
            result=True,
            old_obj=existing_resource,
            new_obj={},
            comment=response_delete["comment"],
        )
    elif response_get["status"] == 404:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        return StateReturn(
            name=name,
            result=True,
            old_obj=None,
            new_obj=None,
            comment=f"'{name}' already absent",
        )
    else:
        hub.log.debug(
            f"Could not get {{ function.hardcoded.resource_name }} {response_get['comment']} {response_get['ret']}"
        )
        return StateReturn(
            name=name, result=False, comment=response_get["comment"], error=response_get['ret']
        )
"""

DESCRIBE_REQUEST_FORMAT = r"""
    result = {}
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict({{ function.hardcoded.describe_parameters }})
    try:
        async for page_result in hub.tool.azure.request.paginate(
                ctx,
                url=f"{{ function.hardcoded.path }}",
                success_codes=[200],
                headers=ctx.acct.headers,
        ):
            resource_list = page_result.get("value", None)
            if resource_list:
                for resource in resource_list:
                    uri_parameter_values = (
                        hub.tool.azure.utils.get_uri_parameter_value_from_uri(resource["id"], uri_parameters)
                    )
                    result[resource["id"]] = {f"azure.{{ function.hardcoded.create_ref }}.present": uri_parameter_values
                    + [{"parameters": resource}]}
    except ValueError as e:
        raise DescribeError(f"Error on describing {{ function.hardcoded.resource_name }}: {str(e)}")
    return result
"""
