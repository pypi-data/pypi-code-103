from typing import Union, Callable, List

import numpy as np

from .grpc import GrpcClient
from .. import request
from ...proto.bert2tf_pb2 import Request
from ...proto.helper import pb2array


class PyClient(GrpcClient):
    def call(self, inputs: Union[List[List[str]], List[str], List[List[List[int]]]], tname: str,
             callback: Callable = None,
             **kwargs) -> Request:
        req = getattr(request, tname)(inputs, **kwargs)
        req = self._stub.CallUnary(req)

        if callback:
            callback(req)

        return req

    def predict(self, inputs: Union[List[List[str]], List[str], List[List[List[int]]]], **kwargs) -> List[np.ndarray]:
        req = self.start(inputs, tname='predict', **kwargs)

        return [[pb2array(blob).tolist() for blob in result.blobs] for result in
                req.predict.results]
