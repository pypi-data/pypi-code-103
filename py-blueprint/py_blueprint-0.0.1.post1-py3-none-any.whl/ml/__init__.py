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

"""
The machine learning tools.
"""
from .util import barrier, all_gather, all_gather_by_part
from .distributed import DistributedGPURun
from .logger import Logger, Loggers, Printer, StandardLogger, TSVDataLogger, TensorBoardLogger
from .scorer import Scorer, MultipleScorers
from .task import Task, ForwardFlags
from .dataprocessor import DataProcessor, DataSource
from .trainer import EMAConfig, Trainer
from .tester import Tester, tester_of_trainer
from .stats import StatSummary


from .dataset import (Dataset, Subset, ConcatDataset, DatasetRepeatingConstantValue,
                      Split, ALL, TRAIN, VAL, TEST, REFINED_TEST, TOY)
from .storage import Storage, FilesStorage, ZipStorage, Frozen, freeze, Modality, Mode
from .inference import BatchList, NonStackable, collate, decollate
from .sampler import DistributedRandomMixSampler, UnifiedDistributedSampler

from . import augmenters as aug
from .augmenters import augment, augment_each
from . import datasets
from . import viz
