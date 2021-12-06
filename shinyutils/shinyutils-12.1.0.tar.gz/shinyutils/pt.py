"""Utilities for pytorch."""

try:
    import torch
except ImportError:
    raise ImportError("shinyutils.pt needs `pytorch`") from None

import inspect
import json
import sys
import warnings
from argparse import Action, ArgumentParser, ArgumentTypeError
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    overload,
    Sequence,
    Tuple,
    TYPE_CHECKING,
)
from unittest.mock import Mock

import torch.nn.functional as F
from corgy import Corgy, corgyparser
from corgy.types import KeyValuePairs, SubClass
from torch import nn
from torch.optim.lr_scheduler import _LRScheduler
from torch.optim.optimizer import Optimizer
from torch.utils.data import DataLoader, Dataset, TensorDataset

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

try:
    from tqdm import trange
except ImportError:
    warnings.warn("progress bar disabled: could not import `tqdm`", RuntimeWarning)

    class trange:  # type: ignore
        def __init__(self, n, *args, **kwargs):
            self._range = range(n)

        def __enter__(self):
            return self

        def __iter__(self):
            return iter(self._range)


if TYPE_CHECKING:
    import numpy as np

__all__ = ("DEFAULT_DEVICE", "PTOpt", "FCNet", "NNTrainer", "TBLogs")

DEFAULT_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class PTOpt(Corgy):
    """Wrapper around PyTorch optimizer and learning rate scheduler.

    Usage::

        >>> opt = PTOpt(Adam, {"lr": 0.001})
        >>> net = nn.Module(...)  # some network
        >>> opt.set_weights(net.parameters())
        >>> opt.zero_grad()
        >>> opt.step()
    """

    __slots__ = ("optimizer", "lr_scheduler")

    class _OptimizerSubClass(SubClass[Optimizer]):
        @classmethod
        def _choices(cls):
            return tuple(
                _c
                for _c in super()._choices()
                if _c.__module__ != "torch.optim._multi_tensor"
            )

    optim_cls: Annotated[
        _OptimizerSubClass, "optimizer sub class"
    ] = _OptimizerSubClass("Adam")

    optim_params: Annotated[
        KeyValuePairs, "arguments for the optimizer"
    ] = KeyValuePairs("")

    lr_sched_cls: Annotated[
        Optional[SubClass[_LRScheduler]], "learning rate scheduler sub class"
    ] = None

    lr_sched_params: Annotated[
        KeyValuePairs, "arguments for the learning rate scheduler"
    ] = KeyValuePairs("")

    @corgyparser("optim_params")
    @corgyparser("lr_sched_params")
    @staticmethod
    def _t_params(s: str) -> KeyValuePairs:
        dic = KeyValuePairs[str, str](s)
        for k, v in dic.items():
            v = json.loads(v)
            dic[k] = v
        return dic

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.optimizer = None
        self.lr_scheduler = None

    def set_weights(self, weights: Iterable[torch.Tensor]):
        """Set weights of underlying optimizer."""
        self.optimizer = self.optim_cls(weights, **self.optim_params)
        if self.lr_sched_cls is not None:
            self.lr_scheduler = self.lr_sched_cls(  # pylint: disable=not-callable
                self.optimizer, **self.lr_sched_params
            )

    @staticmethod
    def _better_lr_sched_repr(lr_sched: _LRScheduler) -> str:
        return (
            lr_sched.__class__.__name__
            + "(\n    "
            + "\n    ".join(
                f"{k}: {v}"
                for k, v in lr_sched.state_dict().items()
                if not k.startswith("_")
            )
            + "\n)"
        )

    def __repr__(self) -> str:
        if self.optimizer is None:
            return super().__repr__()
        r = repr(self.optimizer)
        if self.lr_scheduler is not None:
            r += f"\n{self._better_lr_sched_repr(self.lr_scheduler)}"
        return r

    def _ensure_initialized(self):
        if self.optimizer is None:
            raise TypeError("no weights set: call `PTOpt.set_weights` first")

    def zero_grad(self):
        """Call `zero_grad` on underlying optimizer."""
        self._ensure_initialized()
        self.optimizer.zero_grad()

    def step(self):
        """Call `step` on underlying optimizer, and lr scheduler (if present)."""
        self._ensure_initialized()
        self.optimizer.step()
        if self.lr_scheduler is not None:
            self.lr_scheduler.step()

    @staticmethod
    def add_help_args_to_parser(
        base_parser: ArgumentParser, group_title: Optional[str] = "pytorch help"
    ):
        """Add parser arguments for help on PyTorch optimizers and lr schedulers.

        Args:
            base_parser: `ArgumentParser` instance to add arguments to.
            group_title: Title of a new group to add arguments to. If `None`, arguments
                are added to the base parser instead. Default is `"pytorch help"`.

        Example::

            >>> arg_parser = ArgumentParser(
                    add_help=False, formatter_class=corgy.CorgyHelpFormatter
            )
            >>> PTOpt.add_help_args_to_parser(arg_parser)
            >>> arg_parser.print_help()
            pytorch help:
              --explain-optimizer cls  describe arguments of a torch optimizer
                                       (optional)
              --explain-lr-sched cls   describe arguments of a torch lr scheduler
                                       (optional)
            >>> arg_parser.parse_args(["--explain-optimizer", "Adamax"])
            Adamax(params, lr=0.002, betas=(0.9, 0.999), eps=1e-08, weight_decay=0)
            ...
        """

        class _ShowHelp(Action):
            def __call__(self, parser, namespace, values, option_string=None):
                cls_name = values.__name__
                cls_sig = inspect.signature(values)
                cls_doc = inspect.getdoc(values)
                print(f"{cls_name}{cls_sig}\n\n{cls_doc}")
                parser.exit()

        if group_title is not None:
            base_parser = base_parser.add_argument_group(group_title)  # type: ignore

        base_parser.add_argument(
            "--explain-optimizer",
            type=PTOpt._OptimizerSubClass,
            action=_ShowHelp,
            help="describe a pytorch optimizer",
            choices=PTOpt._OptimizerSubClass._choices(),
        )
        base_parser.add_argument(
            "--explain-lr-sched",
            type=SubClass[_LRScheduler],
            action=_ShowHelp,
            help="describe a pytorch lr scheduler",
            choices=SubClass[_LRScheduler]._choices(),
        )


class FCNet(Corgy, nn.Module):
    """Fully connected PyTorch network."""

    _ActType = Callable[..., torch.Tensor]
    _ActType.__metavar__ = "fun"  # type: ignore

    __slots__ = ("__dict__",)

    in_dim: Annotated[int, "number of input features"]
    out_dim: Annotated[int, "number of output features"]
    hidden_dims: Annotated[Sequence[int], "hidden layer dimensions"]
    hidden_act: Annotated[_ActType, "activation function for hidden layers"] = F.relu
    out_act: Annotated[
        Optional[_ActType], "activation function for output layer"
    ] = None

    @corgyparser("hidden_act")
    @corgyparser("out_act")
    @staticmethod
    def _activation_function(s: str) -> _ActType:
        try:
            return getattr(F, s)
        except AttributeError:
            raise ArgumentTypeError(
                f"`torch.nn.functional` has no attribute `{s}`"
            ) from None

    def __init__(self, **kwargs):
        nn.Module.__init__(self)
        Corgy.__init__(self, **kwargs)
        layer_sizes = [self.in_dim] + self.hidden_dims + [self.out_dim]
        self.layers = nn.ModuleList(
            [nn.Linear(ls, ls_n) for ls, ls_n in zip(layer_sizes, layer_sizes[1:])]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward a tensor through the network, and return the result.

        Args:
            x: Input tensor of shape `(batch_size, in_dim)`.
        """
        for layer in self.layers[:-1]:
            x = self.hidden_act(layer(x))
        x = self.layers[-1](x)
        if self.out_act is not None:
            x = self.out_act(x)  # pylint: disable=not-callable
        return x


class NNTrainer(Corgy):
    """Helper class for training a PyTorch model on a dataset."""

    __slots__ = ("_dataset", "_data_loader")

    iters: Annotated[int, "number of training iterations"]
    ptopt: Annotated[PTOpt, "optimizer and learning rate scheduler"]
    batch_size: Annotated[int, "batch size for training"] = 8
    data_workers: Annotated[int, "number of workers for loading data"] = 0
    shuffle_data: Annotated[bool, "whether to shuffle the dataset"] = True
    pin_cuda: Annotated[bool, "whether to pin data to CUDA memory"] = True
    drop_last: Annotated[bool, "whether to drop the last incomplete batch"] = False
    pbar_desc: Annotated[str, "description for training progress bar"] = "Training"

    @overload
    def set_dataset(self, value: Dataset):
        ...

    @overload
    def set_dataset(self, value: Tuple[torch.Tensor, ...]):
        ...

    @overload
    def set_dataset(self, value: Tuple["np.ndarray", ...]):
        ...

    def set_dataset(self, value):
        """Set the training data.

        Args:
            value: `torch.utils.data.Dataset` instance, or tuple of `torch.Tensor` or
                `np.ndarray` objects.
        """
        if isinstance(value, Dataset):
            self._dataset = value
        elif isinstance(value, tuple):
            if not isinstance(value[0], torch.Tensor):
                value = [torch.from_numpy(val_i) for val_i in value]
            self._dataset = TensorDataset(*value)
        else:
            raise ValueError(f"can't set dataset from type `{type(value)}`")

        self._data_loader = DataLoader(
            self._dataset,
            batch_size=self.batch_size,
            num_workers=self.data_workers,
            shuffle=self.shuffle_data,
            pin_memory=self.pin_cuda,
            drop_last=self.drop_last,
        )

    def train(
        self,
        model: nn.Module,
        loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
        post_iter_hook: Optional[
            Callable[
                [int, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, Any], None
            ]
        ] = None,
    ):
        """Train a model.

        Args:
            model: Model (`nn.Module` instance) to train.
            loss_fn: Loss function mapping input tensors to a loss tensor.
            post_iter_hook: Optional callback function to call after each iteration.
                The function will be called with arguments
                `(iteration, x_batch, y_batch, yhat_batch, loss, pbar)`.
        """
        if self._dataset is None:
            raise RuntimeError("dataset not set: call `set_dataset` before `train`")
        bat_iter = iter(self._data_loader)

        model = model.to(DEFAULT_DEVICE)
        self.ptopt.set_weights(model.parameters())

        with trange(self.iters, desc=self.pbar_desc) as pbar:
            for _iter in pbar:
                try:
                    x_bat, y_bat = next(bat_iter)
                except StopIteration:
                    bat_iter = iter(self._data_loader)
                    x_bat, y_bat = next(bat_iter)
                x_bat, y_bat = x_bat.to(DEFAULT_DEVICE), y_bat.to(DEFAULT_DEVICE)

                yhat_bat = model(x_bat)
                loss = loss_fn(yhat_bat, y_bat)
                pbar.set_postfix(loss=float(loss))

                self.ptopt.zero_grad()
                loss.backward()
                self.ptopt.step()

                if post_iter_hook is not None:
                    post_iter_hook(_iter, x_bat, y_bat, yhat_bat, loss, pbar)


class TBLogs:
    """TensorBoard logs type.

    Args:
        path: Path to log directory. If `None` (default), a mock instance is
            returned.

    Usage::

        tb_logs = TBLogs("tmp/tb")
        tb_logs.writer  # `SummaryWriter` instance
        TBLogs.mock  # mock instance
    """

    __metavar__ = "dir"
    _mock: Optional["TBLogs"] = None

    def __init__(self, path: Optional[str] = None):
        if path is not None:
            try:
                from torch.utils.tensorboard import SummaryWriter
            except ImportError:
                raise RuntimeError("tensorboard not installed") from None
            self.writer = SummaryWriter(path)
        else:
            self.writer = Mock()

    @classmethod
    @property
    def mock(cls) -> "TBLogs":
        """Mock instace that no-ops for every call."""
        if cls._mock is None:
            cls._mock = cls()
        return cls._mock

    def __repr__(self) -> str:
        if isinstance(self.writer, Mock):
            return "TBLogs.mock"
        return f"TBLogs({self.writer.log_dir!r})"
