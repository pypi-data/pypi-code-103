from . import BaseExecutableDriver
from ..proto.helper import pb2array, fill_data


class TokenizerDriver(BaseExecutableDriver):
    """Driver for Tokenize"""

    def __init__(self, method_name: str = 'encode', *args, **kwargs):
        super(TokenizerDriver, self).__init__(method_name=method_name, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        inputs = []

        if self.request.inputs:
            for _input in self.request.inputs:
                nd_array = _input.blobs[0]
                if nd_array.dtype.startswith('<U'):
                    inputs.append(pb2array(nd_array).tolist())
                else:
                    inputs.append([])

        results = [self.executor_fn(*item) for item in inputs]

        for result in results:
            fill_data(self.request.results.add(), result)
