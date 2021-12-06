# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import dataclass
from typing import Mapping, Union


from torch import nn
from copy import deepcopy


@dataclass
class EMAConfig:
    """EMA configuration.
    """
    network_name: str
    decay: float


def _interpret_ema_networks(networks: Mapping[str, Union[nn.Module, EMAConfig]]) -> Mapping[str, nn.Module]:
    outputs = dict()
    for name, net in networks.items():
        if isinstance(net, EMAConfig):
            orig_net = networks[net.network_name]
            assert isinstance(orig_net, nn.Module)
            new_net = deepcopy(orig_net)
            assert not hasattr(new_net, '_ema_cfg')
            new_net._ema_cfg = net
            net = new_net
        outputs[name] = net
    return outputs
