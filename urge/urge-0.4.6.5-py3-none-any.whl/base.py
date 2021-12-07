import time
import copy
import typing as t
import schedule as sche
from functools import partial, wraps

# from .utils import convert_time, callable_check, drop
from urge.utils import convert_time, callable_check, drop


class Action:

    # procs: t.Sequence[t.Callable]
    procs: t.Union[t.List, "ProcManager"]

    def once(self):
        ret = self._excute()
        return ret

    def every(self, freq) -> None:
        # shoud be in convert_time ?
        if isinstance(freq, dict):
            freq = convert_time(freq)

        sche.every(freq).seconds.do(self.once)

    def when(self, time: str):
        sche.every().day.at(time).do(self.once)

    def _excute(self):
        if not self.procs:
            raise Exception()
        elif isinstance(self.procs, list):
            self.procs = ProcManager(*self.procs)

        # seed = copy.deepcopy(self.__dict__)
        seed = self.__dict__.copy()
        seed = drop(seed, ["procs", "self"])
        ret = self.procs.excute(seed)
        # ret = self.procs(seed)
        # ret = self.procs(self.__dict__)
        # DONE Need change procs() -> procs.excute() -> way better
        return ret

    @classmethod
    def set_procs(cls, procs: t.List):
        cls.procs = procs
        return cls()


class ProcManager:
    def __init__(self, *procs) -> None:
        map(callable_check, procs)
        # self._procs += procs -> Because instances share their class _proc
        self._procs = procs

    def __add__(self, other):
        _new_procs = self._procs + other._procs
        return ProcManager(*_new_procs)

    def __call__(self, seed):
        ret = self.pipe(seed, *self._procs)
        return ret

    def excute(self, seed):
        ret = self.pipe(seed, *self._procs)
        return ret

    def pipe(self, seed, *funcs) -> t.Any:

        # TODO
        # when is a Action instance

        # _funcs = arg_load()

        for func in funcs:
            if isinstance(seed, dict):
                seed = func(**seed)
                continue
            seed = func(seed)
        return seed


class action(Action):
    def __init__(self, procs: t.List) -> None:
        self.procs = procs

    def __call__(self, decorated):
        # TODO really need a smarter way to detect self, and get result from procs
        @wraps(decorated)
        def instead(*args, **kwd) -> Action:
            seed = decorated(*args, **kwd)
            self.__dict__.update(seed)
            return self

        return instead


def require():
    '''
    load some .py file from a path as module to run
    this fuction returns Action
    '''
    pass


def env(**kwd):
    import os

    os.environ.update(kwd)


def start():
    while True:
        time.sleep(1)
        sche.run_pending()
