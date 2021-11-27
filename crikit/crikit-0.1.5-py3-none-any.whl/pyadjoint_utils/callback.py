import time
import datetime
import platform
import getpass
import logging
from typing import Sequence, Callable
from .reduced_function import ReducedFunction
from .reduced_function_numpy import ReducedFunctionNumPy
from pyadjoint.reduced_functional import ReducedFunctional
from pyadjoint.reduced_functional_numpy import ReducedFunctionalNumPy

logger = logging.getLogger("CRIKit")

try:
    from mpi4py import MPI
except ImportError:
    # if we can't import mpi4py, then CRIKit is installed without
    # MPI, meaning everything is serial
    class Comm:
        def Get_rank(self):
            return 0

        def Get_size(self):
            return 1

    class MPI:

        COMM_WORLD = Comm()
        COMM_SELF = Comm()


class Callback:
    """Base class for CRIKit callbacks.

    :param name: The name of the callback, defaults to 'Callback'
    :type name: str
    """

    name: str = "Callback"

    def __init__(self, name=None):
        if name is not None:
            self.name = name

    def __call__(self, xk, state=None):
        """Evaluates the callback at a given point with given state"""
        raise NotImplementedError


def now():
    return datetime.datetime.now().ctime()


class FileLoggerCallback(Callback):
    """A callback that logs info about the problem being solved to a file.

    :param name: The name of this callback. Useful for determining which
    of several callbacks wrote to a given file. Defaults to
    `'minimization_callback'`.
    :type name: str
    :param problem_type: A string describing what sort of problem is being
    solved. Defaults to `'Minimization'`
    :type problem_type: str
    :param filename: The filename of a file to log information about this
    run (including machine and timing info) to. Defaults to
    `'{name}_info.txt'` where `name` is the name of this callback.
    :type filename: str, optional
    :param overwrite_file: If `True`, open the file specified by `filename`
    in write mode instead of append mode, deleting the current contents of
    the file before writing to it. Defaults to False
    :type overwrite_file: bool
    :param rf: The `ReducedFunctional` or `ReducedFunction` used in the
    problem being solved. We use this to get the current values of the
    parameters for said `rf`.
    :param write_params: If `True` and `rf` is not `None`, write the
    parameters in the log. Defaults to True
    :type write_params: bool
    :param mpi_comm: The name of the active MPI communicator, which is
    retrieved via `getattr(mpi4py.MPI, mpi_comm)`, with sensible defaults
    if `MPI` is not installed. This is needed if and only if
    `info_file` is not None, and exists to ensure the file is written only
    on MPI rank 0. Defaults to `COMM_WORLD`.
    :type mpi_comm: str
    """

    def __init__(
        self,
        name="minimize_callback",
        problem_type="Minimization",
        filename=None,
        overwrite_file=False,
        rf=None,
        write_params=True,
        mpi_comm="COMM_WORLD",
    ):

        super().__init__(name=name)
        self.filename = self.name + "_info.txt" if filename is None else filename
        self.problem_type = problem_type
        self.rf = rf
        self.write_params = write_params
        self.mpi_comm = getattr(MPI, mpi_comm)
        self.num_calls = 0
        self.mpi_rank = self.mpi_comm.Get_rank()
        if self.mpi_rank == 0:
            with open(self.filename, "w" if overwrite_file else "a") as f:
                f.write(self._build_header())

    def _build_header(self):
        kernel, node, release, os_version, machine, processor = platform.uname()
        header = (
            self.problem_type
            + " Problem "
            + self.name
            + " on platform "
            + f"{kernel}-{release} on node {node} with OS version {os_version} by user {getpass.getuser()} "
            + f"and machine type {machine}"
        )
        if machine != processor:
            header += " and processor {processor}"

        header += "\nStarting at " + now() + "\n"
        return header

    def _format_params(self, xk):
        if isinstance(self.rf, ReducedFunctional):
            cls = ReducedFunctionalNumPy
        else:
            # if rf is not a ReducedFunctional, it's a ReducedFunction
            cls = ReducedFunctionNumPy

        return str(
            cls(self.rf).set_local([c.tape_value() for c in self.rf.controls], xk)
        )

    def _build_message(self, xk):
        if self.write_params and self.rf is not None:
            params = self._format_params(xk)
            with_params = " with parameters "
        else:
            params = with_params = ""

        self.num_calls += 1
        return (
            now()
            + " : Iteration number "
            + str(self.num_calls)
            + with_params
            + params
            + "\n"
        )

    def __call__(self, xk, state=None):
        if self.mpi_rank == 0:
            with open(self.filename, "a") as f:
                f.write(self._build_message(xk))


class CallbackCombiner(Callback):
    """A {class}`CallbackCombiner` takes in several callback functions
    or classes (which must provide a `__call__` method) and calls all of them
    in order, each inside its own try-catch block. Exceptions are reported
    through the `logging` module at level `ERROR`.

    :param callbacks: A list or tuple of callback functions/classes to callback
    :type callbacks: Sequence[Callable]
    :param name: The name of this instance, defaults to `'CallbackCombiner'`
    :type name: str
    """

    def __init__(self, callbacks, name="CallbackCombiner"):
        self.callbacks = callbacks
        super().__init__(name=name)

    def __call__(self, *args, **kwargs):
        """Evalute the callbacks in order with given arguments. Exceptions
        are reported through the `logging` module at log level `ERROR`.
        """
        for cb in self.callbacks:
            try:
                cb(*args, **kwargs)
            except Exception as e:
                logging.error("Caught exception in " + self.name + ":" + str(e))
