import sys
import json
import inspect


def register_filters(app):
    """ Special function that registers all member of this module ending in "_filter". """
    # Get the list of methods and excluded this very function.
    filters = [(name, obj) for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj) and name.endswith("_filter")]
    # Loop over the found filter functions and register them in the app object as jinja filters.
    for filter_name, filter_obj in filters:
        filter_name = filter_name.replace("_filter", "")
        app.jinja_env.filters[filter_name] = filter_obj


def json_format_filter(s):
    """ Filter for pretty formatting json's. """
    try:
        return json.dumps(json.loads(s), indent=2)
    except ValueError:
        return s


def hyphenate_filter(s):
    """ Filter for lowercasing and hyphenating a string. """
    try:
        return s.lower().strip().replace(" ", "-")
    except ValueError:
        return s