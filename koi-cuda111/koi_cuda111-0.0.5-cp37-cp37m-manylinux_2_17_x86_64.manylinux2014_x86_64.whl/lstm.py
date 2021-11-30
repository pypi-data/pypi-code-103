import torch
import numpy as np
from _runtime import lib
from itertools import groupby
from koi.utils import void_ptr, empty, quantize_tensor
from torch.nn import Module, ModuleList, Parameter, Sequential


def rearrange_weights_buffer(buff):
    """
    Transpose the PyTorch LSTM weights from IFGO to GIFO.
    """
    b = torch.empty_like(buff)
    layer_width = buff.shape[0] // 4

    for out_idx, idx in enumerate(['IFGO'.index(d) for d in 'GIFO']):
        start_idx = idx * layer_width
        end_idx = start_idx + layer_width
        b[out_idx * layer_width:(out_idx + 1) * layer_width] = buff[start_idx:end_idx]
    return b.T.contiguous()


class Permute(Module):
    def __init__(self, dims):
        super().__init__()
        self.dims = dims

    def forward(self, x):
        return x.permute(*self.dims)


class LSTM(Module):

    def __init__(self, layer_size, reverse, quantized=False):
        super().__init__()
        self.w_ih = Parameter(torch.empty(layer_size * 4, layer_size), requires_grad=False)
        self.w_hh = Parameter(torch.empty(layer_size * 4, layer_size), requires_grad=False)
        self.b_ih = Parameter(torch.empty(layer_size * 4), requires_grad=False)
        self.b_hh = Parameter(torch.empty(layer_size * 4), requires_grad=False)
        self.layer = getattr(lib, self._get_lstm_host_function_name(reverse, layer_size, quantized))
        self.quantization_scale = None
        self.quantized = quantized
        self._rearranged = False
        self._weights_quantized = False

    def _rearrange_weights_buffer(self):
        if not self._rearranged:
            self.w_ih = Parameter(rearrange_weights_buffer(self.w_ih), requires_grad=False)
            self.w_hh = Parameter(rearrange_weights_buffer(self.w_hh), requires_grad=False)
            self.b_ih = Parameter(rearrange_weights_buffer(self.b_ih), requires_grad=False)
            self.b_hh = Parameter(rearrange_weights_buffer(self.b_hh), requires_grad=False)
            self._rearranged = True

    def _get_lstm_host_function_name(self, reverse, layer_size, quantized):
        direction = 'reverse' if reverse else 'fwd'
        quantization = '_quantized' if quantized else ''
        return 'host_run_lstm_' + direction + quantization + str(layer_size)

    def _quantize_weights(self):
        if self.quantized and (not self._weights_quantized):
            scale, w_hh = quantize_tensor(self.w_hh)
            self.quantization_scale = scale
            self.w_hh = Parameter(w_hh, requires_grad=False)
            self._weights_quantized = True

    def forward(self, input_buffer, out_buffer, chunks):
        self._rearrange_weights_buffer()
        self._quantize_weights()

        if self.quantized:
            self.layer(
                void_ptr(chunks),
                void_ptr(input_buffer.data @ self.w_ih),
                void_ptr(self.w_hh),
                void_ptr(self.b_ih),
                void_ptr(self.quantization_scale),
                out_buffer.ptr,
                len(chunks)
            )

        else:
            self.layer(
                void_ptr(chunks),
                void_ptr(input_buffer.data @ self.w_ih),
                void_ptr(self.w_hh),
                void_ptr(self.b_ih),
                out_buffer.ptr,
                len(chunks)
            )


class LSTMStack(Module):

    def __init__(self, directions, layer_size, batch_size, chunk_size, device='cuda', quantized=False):
        super().__init__()

        self.chunks = torch.empty((batch_size, 4), device=device, dtype=torch.int32)
        self.chunks[:, 0] = torch.arange(0, chunk_size * batch_size, chunk_size)
        self.chunks[:, 2] = torch.arange(0, chunk_size * batch_size, chunk_size)
        self.chunks[:, 1] = chunk_size
        self.chunks[:, 3] = 0

        self.buffers = (
            empty((batch_size, chunk_size, layer_size), device),
            empty((batch_size, chunk_size, layer_size), device),
        )

        self.layers = ModuleList([LSTM(layer_size, direction, quantized) for direction in directions])

    def forward(self, data):
        if data.dtype != torch.float16:
            raise TypeError('Expected fp16 but received %s' % data.dtype)
        buff1, buff2 = self.buffers
        buff1.data[:data.shape[0], :, :] = data
        for layer in self.layers:
            layer(buff1, buff2, self.chunks)
            buff1, buff2 = buff2, buff1
        return buff1.data


def update_graph(model, batchsize=640, chunksize=720, quantize=True):
    """
    Replace a stack of PyTorch LSTMs with a koi LSTMStack.
    """
    for name, layers in groupby(model, lambda x: x.__class__.__name__):
        if name == 'LSTM':
            features = next(layers).rnn.input_size

    if not quantize and features == 128:
        decode_only = True
    elif features not in [96, 128]:
        decode_only = True
    else:
        decode_only = False

    # The standard PyTorch Bonito CRF has a single Permute(2, 0, 1)
    # between the convolutions layers and the recurrent layers.
    #
    #  pytorch   NCT -> Permute(2, 0, 1) -> TNC
    #
    # KOI LSTMs expects NTC and beam_search expects NTC
    #
    #  koi lstm    NCT -> Permute(0, 2, 1) -> NTC -> Permute(1, 0, 2) -> TNC
    #  koi decode  NCT -> Permute(2, 0, 1) -> TNC -> Permute(1, 0, 2) -> NTC
    #  both        NCT -> Permute(0, 2, 1) -> NTC -> Identity()       -> NTC

    modules = []

    for name, layers in groupby(model, lambda x: x.__class__.__name__):
        if name == 'LSTM':
            if decode_only:
                modules.extend([
                    Permute([2, 0, 1]), # NCT -> TNC for PyTorch LSTMs
                    *layers,            #                PyTorch LSTMs
                    Permute([1, 0, 2])  # TNC -> NTC for Koi decoding
                ])
            else:
                modules.extend([
                    Permute([0, 2, 1]), # NCT -> NTC for Koi LSTMStack
                    LSTMStack(
                        [lstm.reverse for lstm in layers],
                        features, batchsize,
                        chunksize, quantized=quantize,
                    )
                    # Identity()       # Still NTC for Koi decoding
                ])
        elif name == 'Permute':
            continue
        elif name == 'LinearCRFEncoder':
            layer = next(layers)
            layer.expand_blanks = False
            modules.append(layer)
        else:
            modules.extend(layers)

    return Sequential(*modules)
