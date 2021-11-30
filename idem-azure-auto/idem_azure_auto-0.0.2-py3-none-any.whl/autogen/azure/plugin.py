def parse(hub, resource_spec: dict, shared_function_data: dict):
    create_api_spec = hub.pop_create.azure.api_spec.parse(resource_spec.get("create"))
    delete_api_spec = hub.pop_create.azure.api_spec.parse(resource_spec.get("delete"))
    list_api_spec = hub.pop_create.azure.api_spec.parse(resource_spec.get("list"))
    patch_parameters = dict()
    if "update" in resource_spec:
        update_api_spec = hub.pop_create.azure.api_spec.parse(
            resource_spec.get("update")
        )
        patch_parameters = generate_patch_parameters(hub, update_api_spec)
    describe_parameters = generate_describe_parameters(hub, create_api_spec)
    present_parameters = generate_parameters(hub, create_api_spec)
    present_parameters["parameters"] = {
        "required": False,
        "default": dict(),
        "target_type": "mapping",
        "target": "kwargs",
        "param_type": "dict",
        "doc": "API request payload parameters",
    }
    present = {
        "params": present_parameters,
        "doc": f"Create or update {resource_spec.get('resource')}",
        "hardcoded": dict(
            path=create_api_spec.get("api_url"),
            patch_parameters=patch_parameters,
            **shared_function_data,
        ),
    }
    absent_parameters = generate_parameters(hub, delete_api_spec)
    absent = {
        "params": absent_parameters,
        "doc": f"Delete {resource_spec.get('resource')}",
        "hardcoded": dict(path=delete_api_spec.get("api_url"), **shared_function_data),
    }
    describe = {
        "doc": f"List all {resource_spec.get('resource')} under the same subscription",
        "hardcoded": dict(
            path=list_api_spec.get("api_url"),
            describe_parameters=describe_parameters,
            **shared_function_data,
        ),
    }
    doc_description = ""
    plugin = {
        "imports": [
            "from collections import OrderedDict",
            "from typing import Any",
            "from typing import Dict",
            "from idem_azure_auto.helpers.exc import DescribeError",
            "from idem_azure_auto.helpers.returns import StateReturn",
            "__contracts__ = ['resource']",
        ],
        "doc": doc_description,
        "functions": {
            "present": present,
            "absent": absent,
            "describe": describe,
        },
    }
    return plugin


def generate_parameters(hub, api_spec: dict):
    params = {}
    api_url = api_spec.get("api_url")
    uri_parameters = api_spec.get("uri_parameters")
    for uri_parameter in uri_parameters:
        params["name"] = hub.pop_create.azure.template.NAME_PARAMETER
        # Skip api-version parameter as this is not an input field. Skip subscriptionId parameter as this will
        # be supplied by acct
        if (
            uri_parameter.get("name") == "api-version"
            or uri_parameter.get("name") == "subscriptionId"
        ):
            continue
        if uri_parameter.get("name_formatted") in api_url:
            param = {
                "required": True,
                "default": None,
                "target_type": "mapping",
                "target": "kwargs",
                "param_type": "str",
                "doc": uri_parameter.get("description"),
            }
            params.update({uri_parameter.get("name_formatted"): param})
    return params


def generate_patch_parameters(hub, api_spec: dict):
    patch_parameters = {}
    request_body = api_spec.get("request_body")
    for parameter in request_body:
        if "." in parameter.get("name"):
            parameter_split = parameter.get("name").split(".")
            if parameter_split[0] not in patch_parameters:
                patch_parameters[parameter_split[0]] = dict()
            patch_parameters[parameter_split[0]][parameter_split[1]] = parameter_split[
                1
            ]
        else:
            patch_parameters[parameter.get("name")] = parameter.get("name")
    return patch_parameters


def generate_describe_parameters(hub, api_spec: dict):
    params = {}
    api_url = api_spec.get("api_url")
    uri_parameters = api_spec.get("uri_parameters")
    # remove api-version parameter from uri
    uri_values = api_url.split("?")[0].split("/")
    for uri_parameter in uri_parameters:
        # skip api-version and subscriptionId parameter
        if (
            uri_parameter.get("name") == "api-version"
            or uri_parameter.get("name") == "subscriptionId"
        ):
            continue
        if uri_parameter.get("name_formatted") in api_url:
            uri_index = uri_values.index(
                "{" + uri_parameter.get("name_formatted") + "}"
            )
            params.update(
                {uri_values[uri_index - 1]: uri_parameter.get("name_formatted")}
            )
    return params
