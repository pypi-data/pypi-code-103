from functools import partial

from loky.backend import get_context
from torch.utils.data.dataloader import _BaseDataLoaderIter, DataLoader as _DataLoader
import torch.multiprocessing as multiprocessing
import multiprocessing as python_multiprocessing

from .base import NotifySingleProcessDataLoaderIter, NotifyMultiProcessingDataLoaderIter

__all__ = ['LokyDataLoader']


class LokyDataLoader(_DataLoader):
    #
    @property
    def multiprocessing_context(self):
        return self.__multiprocessing_context

    @multiprocessing_context.setter
    def multiprocessing_context(self, multiprocessing_context):
        if multiprocessing_context is not None:
            if self.num_workers > 0:
                if isinstance(multiprocessing_context, str):
                    valid_start_methods = multiprocessing.get_all_start_methods()
                    if multiprocessing_context not in valid_start_methods:
                        raise ValueError(
                            ('multiprocessing_context option '
                             'should specify a valid start method in {!r}, but got '
                             'multiprocessing_context={!r}').format(valid_start_methods, multiprocessing_context))
                    # error: Argument 1 to "get_context" has incompatible type "Union[str, bytes]"; expected "str"  [arg-type]
                    multiprocessing_context = multiprocessing.get_context(
                        multiprocessing_context)  # type: ignore[arg-type]

                if not isinstance(multiprocessing_context, python_multiprocessing.context.BaseContext):
                    raise TypeError(('multiprocessing_context option should be a valid context '
                                     'object or a string specifying the start method, but got '
                                     'multiprocessing_context={}').format(multiprocessing_context))
        else:
            if self.num_workers > 0:
                multiprocessing_context = get_context('loky')
        self.__multiprocessing_context = multiprocessing_context

    def _get_iterator(self) -> '_BaseDataLoaderIter':
        if self.num_workers == 0:
            return NotifySingleProcessDataLoaderIter(self)
        else:
            self.check_worker_number_rationality()
            return NotifyMultiProcessingDataLoaderIter(self)
