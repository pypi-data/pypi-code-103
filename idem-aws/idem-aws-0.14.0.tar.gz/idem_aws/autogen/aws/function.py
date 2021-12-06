import botocore.client
import botocore.docs.docstring


def parse(hub, client: "botocore.client.BaseClient", service: str, operation: str):
    function = getattr(client, operation)
    doc: botocore.docs.docstring.ClientMethodDocstring = function.__doc__
    docstring = hub.tool.format.html.parse(doc._gen_kwargs["method_description"])
    try:
        # TODO what does botocore expect?
        params = doc._gen_kwargs["operation_model"].input_shape.members
        required_params = doc._gen_kwargs[
            "operation_model"
        ].input_shape.required_members
        parameters = {
            p: hub.pop_create.aws.plugin.parameter(
                param=data, required=p in required_params
            )
            for p, data in params.items()
        }
    except AttributeError:
        parameters = {}
    try:
        return_type = hub.pop_create.aws.plugin.type(
            doc._gen_kwargs["operation_model"].output_shape.type_name
        )
    except AttributeError:
        return_type = None

    ret = {
        "doc": "\n".join(hub.tool.format.wrap.wrap(docstring, width=112)),
        "params": parameters,
        "return_type": return_type,
        "hardcoded": {"service": service, "operation": operation},
    }

    return ret
