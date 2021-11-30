import logging
from collections import OrderedDict


def _is_within(parent, o, ignore: set):
    """
    Determine of an object is within a parent object.
    :param parent: The object in which o hopefully exists.
    :param o: The object to find in parent.
    :param ignore: A set of keys to ignore in parent.
    return: True if o is within parent somewhere. False otherwise.
    """
    if not isinstance(parent, type(o)):
        return False
    elif isinstance(o, dict):
        return _is_within_dict(parent, o, ignore)
    else:
        return parent == o


def _is_within_dict(parent, o, ignore: set):
    """
    Determine of an object is within a parent dict object.
    :param parent: The object in which o hopefully exists.
    :param o: The object to find in parent.
    :param ignore: A set of keys to ignore in parent.
    return: True if o is within parent somewhere. False otherwise.
    """
    ret = False
    for k, v in o.items():
        if k in ignore:
            ret = True
            break
        elif k in parent and parent[k] == v:
            ret = True
            break
    return ret


def get_from_list(hub, parent, o):
    """
    Returns the first object found in parent that contains o, None if no object is found.
    :param hub: The redistributed pop central hub. This is required in
    Idem, so while not used, must appear.
    :param parent: An iterable object to search for o.
    :param o: An object the values of which must exist in one of the iterables.

    For example:

    The subset:

    { name: "my_object" }

    exists within (and would be returned)

    [
        { name: "not_my_object", something_else: "not the other thing" }
        { name: "my_object", something_else: "some other thing"},
    ]
    """
    ret = None

    for item in parent:
        if isinstance(item, dict):
            if _is_within(item, o, set()):
                ret = item
                break
        else:
            logging.warning(f"Item {str(item)} should be a dict. Skipping this item.")

    return ret


def _no_update(old_value, new_value) -> bool:
    """Given two value, check if there is a need to update from the old_value to new_value."""
    if isinstance(old_value, str) and isinstance(new_value, str):
        # If the two values are the same string, then no need to update.
        return old_value == new_value
    elif isinstance(old_value, dict) and isinstance(new_value, dict):
        # If the new value dictionary is a subset of the old value dictionary, then no need to update
        return new_value.items() <= old_value.items()
    else:
        return False


def patch_json_content(
    hub, patch_parameters: dict, old_values: dict, new_values: dict
) -> dict:
    """
    Generate a json that contains all the parameters and their values that will be sent during a PATCH operation
    :param hub: The redistributed pop central hub. This is required in
    Idem, so while not used, must appear.
    :param patch_parameters: A dictionary of patchable parameters.
    For example: {"tags": "tags", "properties": {"properties_1": "properties_1", "properties_2": "properties_2"}}
    :param old_values: A dictionary that contains the old values of parameters.
    For example: {"tags": "new-tag", "properties": {"properties_1": "value_1", "properties_2": "value_2"}}
    :param new_values: A dictionary that contains the new values of parameters. This should be the exact structure as
     what old_values have.
    For example: {"tags": "new-tag", "properties": {"properties_1": "value_1", "properties_2": "value_2"}}
    """
    payload = {}
    for parameter_key, parameter_fields in patch_parameters.items():
        value = new_values.get(parameter_key, None)
        if value is None:
            continue
        elif isinstance(parameter_fields, str):
            if not (
                parameter_fields in old_values
                and (
                    old_values[parameter_fields] == value
                    or _no_update(old_values[parameter_fields], value)
                )
            ):
                payload.update({parameter_key: value})
        elif isinstance(parameter_fields, dict):
            if parameter_key in old_values:
                sub_payload = patch_json_content(
                    hub, parameter_fields, old_values[parameter_key], value
                )
            else:
                sub_payload = patch_json_content(hub, parameter_fields, dict(), value)
            if sub_payload:
                payload.update({parameter_key: sub_payload})
        else:
            continue
    return payload


def get_uri_parameter_value_from_uri(hub, uri: str, parameters: OrderedDict) -> list:
    """
    Generate a list of pairs of uri parameter and its value. And convert uri parameters to expected key used in sls files
    For example /virtualNetworks/virtual-network-name/subnets/subnet-name} will output
    [{"virtualNetworks": "virtual-network-name"}, {"subnets": "subnet-name"}]
    :param hub: The redistributed pop central hub. This is required in Idem, so while not used, must appear.
    :param uri: the uri
    :param parameters: parameters to search through the uri.
    For example: OrderedDict({"virtualNetworks": "virtual_network_name"})
    """
    ret = []
    uri_values = uri.split("/")
    for parameter_key, parameter_value in parameters.items():
        if parameter_key in uri_values:
            uri_index = uri_values.index(parameter_key)
            # Convert parameters from camel case to snake case
            ret.append({parameter_value: uri_values[uri_index + 1]})
    return ret
