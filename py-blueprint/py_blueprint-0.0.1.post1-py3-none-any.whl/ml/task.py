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

from typing import Mapping, Any, Tuple, List
from dataclasses import dataclass

import torch
from torch import nn
import torch.nn.functional as F


@dataclass
class ForwardFlags:
    with_losses: bool = True  # for training
    with_outputs: bool = True  # for measurement
    with_images: bool = True  # for visualization


class Task(nn.Module):
    """A task module that computes losses and outputs with given networks and data.
    """

    def setup_networks(self, networks: Mapping[str, nn.Module]):
        """Setup networks.

        Attach those networks whose parameters will be updated.
        """
        pass

    def forward_networks(self, data: Mapping[str, torch.Tensor]
                         ) -> Mapping[str, torch.Tensor]:
        raise NotImplementedError()

    def compute_losses_and_outputs(
            self, data: Mapping[str, torch.Tensor],
            flags: ForwardFlags) -> Tuple[torch.Tensor,
                                          Mapping[str, torch.Tensor],
                                          Mapping[str, torch.Tensor],
                                          Mapping[str, torch.Tensor]]:
        raise NotImplementedError()

    def forward(self, data: Mapping[str, torch.Tensor], flags: ForwardFlags
                ) -> Tuple[torch.Tensor,
                           Mapping[str, torch.Tensor],
                           Mapping[str, torch.Tensor],
                           Mapping[str, torch.Tensor]]:
        """Forwarding with one batch of data, and returns corresponding losses/scores and outputs.

        Args:
            data (Mapping[str, torch.Tensor]): One data batch.
            with_outputs (bool): Whether to compute the outputs for visualization.
            flags (ForwardFlags): Flags for computation.

        Returns:
            Tuple[torch.Tensor, Mapping[str, torch.Tensor], Mapping[str, torch.Tensor], Mapping[str, torch.Tensor]]:
                The total loss/score, the named losses/scores, outputs (can be None) and output_images.
        """
        raise NotImplementedError()
