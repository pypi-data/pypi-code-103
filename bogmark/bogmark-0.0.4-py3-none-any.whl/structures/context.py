from contextvars import ContextVar

context_var = ContextVar("request_id")


def set_current_request_id(current_rid):
    if not isinstance(current_rid, str):
        raise TypeError("wrong type for request_id")
    context_var.set(current_rid)


def get_current_request_id():
    try:
        rid = context_var.get()
    except LookupError:
        rid = "default_request_id"
    return rid
