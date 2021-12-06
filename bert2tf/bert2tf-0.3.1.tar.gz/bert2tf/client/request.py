from typing import Union, List

from ..proto import bert2tf_pb2
from ..proto.helper import fill_data


def _generate(inputs: Union[List[List[str]], List[List[List[int]]]], request_id: int = 0) -> bert2tf_pb2.Request:
    """Generate a request"""
    request = bert2tf_pb2.Request()
    request.request_id = request_id

    for _input in inputs:
        fill_data(request.predict.inputs.add(), _input)

    return request


def predict(*args, **kwargs):
    """Generate predict request"""
    return _generate(*args, **kwargs)
