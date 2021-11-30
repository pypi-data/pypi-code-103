from fastapi import Header


async def check_headers(
    x_request_id: str = Header(..., description="Id of a request. Helps to trace logs"),  # noqa
    x_service_name: str = Header(..., description="Client name. Helps to trace logs"),  # noqa
):
    pass
