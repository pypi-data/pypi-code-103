from rest_framework.response import Response


def generic_error(status: int, error_code: str, error_message: str) -> Response:
    data = {"error_code": error_code, "error_message": error_message}
    return Response(status=status, data=data)
