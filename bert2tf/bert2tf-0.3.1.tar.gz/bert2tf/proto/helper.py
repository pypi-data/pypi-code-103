from typing import Union, Iterator, List

import numpy as np
import tensorflow as tf

from . import bert2tf_pb2
from .bert2tf_pb2 import Request
from ..excepts import BadInputs, UnknownRequestError

__all__ = ['pb2array', 'array2pb', 'fill_data', 'is_data_request', 'is_terminate_request', 'is_idle_request',
           'add_route', 'add_envelope', 'get_request_type']


def pb2array(blob: bert2tf_pb2.NdArray) -> np.ndarray:
    """Convert a blob protobuf to a numpy ndarray.

    Note if the argument ``quantize`` is specified in :func:`array2pb` then the returned result may be lossy.
    Nonetheless, it will always in original ``dtype``, i.e. ``float32`` or ``float64``

    :param blob: a blob described in protobuf
    """
    x = np.frombuffer(blob.buffer, dtype=blob.dtype)

    if blob.quantization == bert2tf_pb2.NdArray.FP16:
        x = x.astype(blob.original_dtype)
    elif blob.quantization == bert2tf_pb2.NdArray.UINT8:
        x = x.astype(blob.original_dtype) * blob.scale + blob.min_val

    return x.reshape(blob.shape)


def array2pb(x: np.ndarray, quantize: str = None) -> bert2tf_pb2.NdArray:
    """Convert a numpy ndarray to blob protobuf.

    :param x: the target ndarray
    :param quantize: the quantization method used when converting to protobuf.
            Availables are ``fp16``, ``uint8``, default is None.

    Remarks on quantization:
        The quantization only works when ``x`` is in ``float32`` or ``float64``. The motivation is to
        save the network bandwidth by using less bits to store the numpy array in the protobuf.

            - ``fp16`` quantization is lossless, can be used widely. Each float is represented by 16 bits.
            - ``uint8`` quantization is lossy. Each float is represented by 8 bits. The algorithm behind is standard scaling.

        There is no need to specify the quantization type in :func:`pb2array`,
        as the quantize type is stored and the blob is self-contained to recover the original numpy array
    """
    blob = bert2tf_pb2.NdArray()

    if quantize == 'fp16' and (x.dtype == np.float32 or x.dtype == np.float64):
        blob.quantization = bert2tf_pb2.NdArray.FP16
        blob.original_dtype = x.dtype.name
        x = x.astype(np.float16)
    elif quantize == 'uint8' and (x.dtype == np.float32 or x.dtype == np.float64 or x.dtype == np.float16):
        blob.quantization = bert2tf_pb2.NdArray.UINT8
        blob.max_val, blob.min_val = x.max(), x.min()
        blob.original_dtype = x.dtype.name
        blob.scale = (blob.max_val - blob.min_val) / 256
        x = ((x - blob.min_val) / blob.scale).astype(np.uint8)

    else:
        blob.quantization = bert2tf_pb2.NdArray.NONE

    blob.buffer = x.tobytes()
    blob.shape.extend(list(x.shape))
    blob.dtype = x.dtype.str
    return blob


def fill_data(data: bert2tf_pb2.Data,
              inputs: Union[List[str], List[List[int]], Iterator[tf.Tensor], tf.Tensor, str, np.ndarray]) -> None:
    """Add data into protobuf message"""
    if isinstance(inputs, (list, tuple)):
        if isinstance(inputs[0], tf.Tensor):
            inputs = [item.numpy() for item in inputs]

        elif isinstance(inputs[0], str):
            inputs = [inputs]

        elif isinstance(inputs[0], (list, tuple)):
            pass

        else:
            raise BadInputs(
                f'in first dimension of inputs, data type except `tuple`, `list`, `tf.Tensor`, got {type(inputs[0])}')

        for item in inputs:
            data.blobs.add().CopyFrom(array2pb(np.array(item)))

    elif isinstance(inputs, tf.Tensor):
        data.blobs.add().CopyFrom(array2pb(inputs.numpy()))
    elif isinstance(inputs, np.ndarray):
        data.blobs.add().CopyFrom(array2pb(inputs))
    elif isinstance(inputs, str):
        data.blobs.add().CopyFrom(array2pb(np.array([inputs])))
    else:
        raise ValueError(f'the inputs data type: {type(inputs)} is not support')


def is_data_request(req: Request) -> bool:
    """check if the request is data request"""
    req_type = type(req)
    return req_type != Request.ControlRequest


def is_idle_request(req: Request) -> bool:
    """check if the request is idle request"""
    if type(req) == Request.ControlRequest and req.command == Request.ControlRequest.Command.IDLE:
        return True
    return False


def is_terminate_request(req: Request) -> bool:
    """check if the request is terminate request"""
    if type(req) == Request.ControlRequest and req.command == Request.ControlRequest.Command.TERMINATE:
        return True
    return False


def add_envelope(req: bert2tf_pb2.Request, pod_name: str, client_id: str) -> bert2tf_pb2.Message:
    """Add envelope to a request and make it as a complete message, which can be transmitted between pods.

    :param req: the protobuf request
    :param pod_name: the name of the current pod
    :param client_id: the id of the send pod
    :return: the resulted protobuf message
    """
    msg = bert2tf_pb2.Message()
    msg.envelope.client_id = client_id
    if req.request_id is not None:
        msg.envelope.request_id = req.request_id
    else:
        raise AttributeError('"request_id" is missing or unset!')
    add_route(msg.envelope, pod_name, client_id)
    msg.request.CopyFrom(req)

    return msg


def add_route(envelope: bert2tf_pb2.Envelope, pod_name: str, identity: str):
    r = envelope.routes.add()
    r.pod = pod_name
    r.start_time.GetCurrentTime()
    r.pod_id = identity


def get_request_type(req: bert2tf_pb2.Request) -> str:
    """Get message request type.

    :param req: message request
    :return: return one of request type str in predict, idle, terminate
    """
    if is_data_request(req):
        return 'predict'
    elif is_idle_request(req):
        return 'idle'
    elif is_terminate_request(req):
        return 'terminate'
    else:
        raise UnknownRequestError(f'unknown request type {req}')
