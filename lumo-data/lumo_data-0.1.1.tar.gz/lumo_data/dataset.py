import warnings
from torch.utils.data import Dataset
from dbrecord.dblist import PList
from typing import List

__all__ = ['DBDataset', 'BatchDataset']


class BatchDataset(Dataset):

    def notify(self, ids: List[int]):
        pass


class DBDataset(BatchDataset):
    def __init__(self, database, transform=None):
        self.data = PList(database)
        self.transform = transform

        self._hooked = False

    def __len__(self):
        return len(self.data)

    def _get_from_cache(self, item):
        if self.ids is None:
            raise ValueError('This exception raised because using DBBatchSampler to `notify` DBDataset'
                             ' but not actually use the sampler in DataLoader.')
        reid = self.ids[item]
        res = self.batch[reid]
        if self.transform is not None:
            res = self.transform(res)
        return res

    def _get_from_db(self, item):
        return self.data.gets(item)[0]

    def __getitem__(self, item):
        if not self._hooked:
            warnings.warn("It's recommond to use notify method to cache batch data when reading data from database."
                          "Try use LokyDataLoader")
            res = self._get_from_db(item)
        else:
            res = self._get_from_cache(item)
        return res

    def notify(self, ids):
        self._hooked = True
        self.ids = {id: i for i, id in enumerate(ids)}
        self.batch = self.data.gets(ids)
