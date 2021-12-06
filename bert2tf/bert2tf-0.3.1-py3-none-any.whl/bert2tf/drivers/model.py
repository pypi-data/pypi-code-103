import tensorflow as tf

from . import BaseExecutableDriver
from ..client.request import fill_data
from ..proto.helper import pb2array


class ModelDriver(BaseExecutableDriver):
    """Driver for model"""

    def __init__(self, method_name: str = 'call', *args, **kwargs):
        super(ModelDriver, self).__init__(method_name=method_name, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.request.inputs and not self.request.inputs[0].blobs[0].dtype.startswith('<U'):
            original_inputs = [[pb2array(blob) for blob in _input.blobs] for _input in self.request.inputs]

            inputs = []
            for idx1 in range(len(original_inputs[0])):
                inputs.append(
                    [tf.convert_to_tensor([original_inputs[idx2][idx1]]) for idx2 in range(len(original_inputs))])

        else:
            inputs = [[tf.convert_to_tensor([pb2array(blob)]) for blob in _input.blobs] for _input in
                      self.request.results]

        results = []
        for _input in inputs:
            results.append(self.executor_fn(*_input))

        self.request.ClearField('results')
        for result in results:
            fill_data(self.request.results.add(), result)


class ARBeamSearchDriver(ModelDriver):
    """Driver for Auto Regressive model which use beam search to auto regressive"""

    def __init__(self, *args, **kwargs):
        super(ARBeamSearchDriver, self).__init__(method_name='beam_search', *args, **kwargs)


class ARRandomSampleDriver(ModelDriver):
    """Driver for Auto Regressive model which use random sample h to auto regressive"""

    def __init__(self, *args, **kwargs):
        super(ARRandomSampleDriver, self).__init__(method_name='random_sample', *args, **kwargs)
