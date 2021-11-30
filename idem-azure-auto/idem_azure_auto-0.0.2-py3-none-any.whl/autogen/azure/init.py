import os
import pathlib
import traceback
from os.path import exists

import tqdm
from dict_tools.data import NamespaceDict

try:
    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def context(hub, ctx, directory: pathlib.Path):
    ctx = hub.pop_create.idem_cloud.init.context(ctx, directory)

    ctx.servers = [
        "https://management.azure.com/",
        "https://management.core.windows.net/",
    ]

    # We already have an acct plugin
    ctx.has_acct_plugin = False
    ctx.service_name = ctx.service_name or "azure_auto"
    docs_api = "https://docs.microsoft.com"

    # plugins = hub.pop_create.azure.resource.parse(docs_api)

    # TODO: This list below will be replaced once the webpages parsers getting finished
    resources = [
        {
            "service": "Resource Management",
            "resource": "Resource Groups",
            "create": "https://docs.microsoft.com/en-us/rest/api/resources/resource-groups/create-or-update",
            "update": "https://docs.microsoft.com/en-us/rest/api/resources/resource-groups/update",
            "list": "https://docs.microsoft.com/en-us/rest/api/resources/resource-groups/list",
            "delete": "https://docs.microsoft.com/en-us/rest/api/resources/resource-groups/delete",
            "get": "https://docs.microsoft.com/en-us/rest/api/resources/resource-groups/get",
        },
        {
            "service": "Virtual Networks",
            "resource": "Virtual Networks",
            "create": "https://docs.microsoft.com/en-us/rest/api/virtualnetwork/virtual-networks/create-or-update",
            "update": "https://docs.microsoft.com/en-us/rest/api/virtualnetwork/virtual-networks/update-tags",
            "list": "https://docs.microsoft.com/en-us/rest/api/virtualnetwork/virtual-networks/list-all",
            "delete": "https://docs.microsoft.com/en-us/rest/api/virtualnetwork/virtual-networks/delete",
            "get": "https://docs.microsoft.com/en-us/rest/api/virtualnetwork/virtual-networks/get",
        },
    ]

    # Initialize cloud spec
    ctx.cloud_spec = NamespaceDict(
        project_name=ctx.project_name,
        service_name=ctx.service_name,
        request_format={
            "present": hub.pop_create.azure.template.PRESENT_REQUEST_FORMAT,
            "absent": hub.pop_create.azure.template.ABSENT_REQUEST_FORMAT,
            "describe": hub.pop_create.azure.template.DESCRIBE_REQUEST_FORMAT,
        },
        plugins={},
    )

    for resource in tqdm.tqdm(resources):
        try:
            plugins = plugin(hub, resource)
            if plugins:
                ctx.cloud_spec.plugins = plugins
                hub.cloudspec.init.run(
                    ctx,
                    directory,
                    create_plugins=["state_modules"],
                )
        except Exception as e:
            hub.log.error(
                f"Error when generating {resource.get('resource')} with error {traceback.print_stack(e)}"
            )

    hub.pop_create.init.run(
        directory=directory,
        subparsers=["cicd"],
        **ctx,
    )

    ctx.cloud_spec.plugins = {}
    return ctx


def plugin(hub, resource):
    service_name_formatted = resource.get("service").lower().strip().replace(" ", "_")
    resource_name_formatted = resource.get("resource").lower().strip().replace(" ", "_")
    plugin_key = f"{service_name_formatted}.{resource_name_formatted}"
    plugins = dict()
    if exists(
        f"{os.path.dirname(os.path.realpath(__file__))}/../../states/azure_auto/{service_name_formatted}/{resource_name_formatted}.py"
    ):
        # if the auto-generated file has existed, skip generating this resource
        return plugins
    shared_function_data = {
        "get_function": f"await hub.exec.request.json.get",
        "create_function": f"await hub.exec.request.json.put",
        "list_function": f"await hub.exec.request.json.get",
        "delete_function": f"await hub.exec.request.raw.delete",
        "patch_function": f"await hub.exec.request.json.patch",
        "resource_name": resource.get("resource"),
        "create_ref": plugin_key,
    }
    resource_plugin = hub.pop_create.azure.plugin.parse(resource, shared_function_data)
    plugins[plugin_key] = resource_plugin
    return plugins
