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

from typing import Mapping, List

import numpy as np


class Scorer:
    """A base class for scoring a collection of data.
    """

    def init_evaluation(self):
        """Initialize evaluation.
        """
        pass

    def evaluate(self, data: Mapping[str, np.ndarray]):
        """Evaluate on data sample.

        Args:
            data (Mapping[str, np.ndarray]): One data sample.
        """
        raise NotImplementedError()

    def finalize_evaluation(self) -> Mapping[str, float]:
        """Finalize the evaluation.

        Returns:
            Mapping[str, float]: The final results.
        """
        raise NotImplementedError()


class MultipleScorers(Scorer):
    def __init__(self, scorers: List[Scorer]) -> None:
        self.scorers = scorers

    def init_evaluation(self):
        for s in self.scorers:
            s.init_evaluation()

    def evaluate(self, data: Mapping[str, np.ndarray]):
        for s in self.scorers:
            s.evaluate(data)

    def finalize_evaluation(self) -> Mapping[str, float]:
        merged_outputs = dict()
        for s in self.scorers:
            merged_outputs.update(s.finalize_evaluation())
        return merged_outputs
