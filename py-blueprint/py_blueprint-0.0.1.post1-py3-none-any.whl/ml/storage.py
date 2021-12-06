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

from typing import Mapping, Type, Any
import os
import pickle
import numpy as np
import cv2
import zipfile
import io
from enum import Enum

from .dataset import Dataset


class Modality(Enum):
    CONFIG = 0
    IMAGE_PNG = 1
    IMAGE_JPG = 2
    IMAGE_LABEL = 3
    IMAGE_GRAY = 4


CONFIG = Modality.CONFIG
IMAGE_PNG = Modality.IMAGE_PNG
IMAGE_JPG = Modality.IMAGE_JPG
IMAGE_LABEL = Modality.IMAGE_LABEL
IMAGE_GRAY = Modality.IMAGE_GRAY


class Mode(Enum):
    READ = 0
    WRITE = 1


READ = Mode.READ
WRITE = Mode.WRITE


class _CompatibleUnpickler(pickle.Unpickler):
    def find_class(self, module_name: str, global_name: str) -> Any:
        if module_name.startswith('haya.'):
            module_name = 'blueprint.' + module_name[len('haya.'):]
        if module_name == 'blueprint.data' and global_name == 'Modality':
            module_name = 'blueprint.ml.storage'
        return super().find_class(module_name, global_name)


def _compatible_load(f):
    return _CompatibleUnpickler(f).load()


def _compatible_loads(bs):
    return _CompatibleUnpickler(io.BytesIO(bs)).load()


class Storage:
    """All storage classes should inherit this class.
    """

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def allocate_key(self, key: str) -> None:
        pass

    def save(self, sample_name: str, key: str, value, modality: Modality) -> str:
        raise NotImplementedError()

    def load(self, sample_name: str, key: str, rep: str, modality: Modality):
        raise NotImplementedError()

    def save_config(self, config: dict):
        raise NotImplementedError()

    def load_config(self) -> dict:
        raise NotImplementedError()

    def close(self):
        pass


def _try_mkdir(s):
    if not os.path.exists(s):
        os.mkdir(s)


class FilesStorage(Storage):
    def __init__(self, root, mode: Mode):
        assert root is not None
        _try_mkdir(root)
        self.root = root

    def allocate_key(self, key):
        folder = os.path.join(self.root, key)
        _try_mkdir(folder)

    def save(self, sample_name, key, value, modality):
        if modality == Modality.IMAGE_PNG:
            assert value.ndim == 3
            cv2.imwrite(os.path.join(
                self.root, key, sample_name+'.png'), value[:, :, ::-1])
            return os.path.join(key, sample_name+'.png')
        elif modality == Modality.IMAGE_JPG:
            assert value.ndim == 3
            cv2.imwrite(os.path.join(
                self.root, key, sample_name+'.jpg'), value[:, :, ::-1])
            return os.path.join(key, sample_name+'.jpg')
        elif modality in {Modality.IMAGE_LABEL, Modality.IMAGE_GRAY}:
            assert value.ndim == 2
            cv2.imwrite(os.path.join(
                self.root, key, sample_name+'.png'), value)
            return os.path.join(key, sample_name+'.png')
        else:
            return value

    def load(self, sample_name, key, rep, modality):
        if modality in {Modality.IMAGE_JPG, Modality.IMAGE_PNG}:
            return cv2.cvtColor(cv2.imread(
                os.path.join(self.root, rep)), cv2.COLOR_BGR2RGB)
        elif modality in {Modality.IMAGE_LABEL, Modality.IMAGE_GRAY}:
            return cv2.imread(os.path.join(
                self.root, rep), cv2.IMREAD_GRAYSCALE)
        else:
            return rep

    def save_config(self, config):
        with open(os.path.join(self.root, 'config.pk'), 'wb') as f:
            pickle.dump(config, f)

    def load_config(self):
        with open(os.path.join(self.root, 'config.pk'), 'rb') as f:
            return _compatible_load(f)


class ZipStorage(Storage):
    def __init__(self, filename, mode: Mode, level: int = 0):
        if level > 0:
            compression = zipfile.ZIP_DEFLATED
        else:
            compression = zipfile.ZIP_STORED
        self.zipfile = zipfile.ZipFile(
            filename, 'r' if mode == Mode.READ else 'w',
            compression=compression, compresslevel=level)

    @staticmethod
    def _join(*cs):
        return '/'.join(cs)

    def save(self, sample_name, key, value, modality):
        if modality == Modality.IMAGE_PNG:
            assert value.ndim == 3
            ret, buf = cv2.imencode('.png', value[:, :, ::-1])
            assert ret
            path = ZipStorage._join(key, sample_name+'.png')
            self.zipfile.writestr(path, buf)
            return path
        elif modality == Modality.IMAGE_JPG:
            assert value.ndim == 3
            ret, buf = cv2.imencode('.jpg', value[:, :, ::-1])
            assert ret
            path = ZipStorage._join(key, sample_name+'.jpg')
            self.zipfile.writestr(path, buf)
            return path
        elif modality in {Modality.IMAGE_LABEL, Modality.IMAGE_GRAY}:
            assert value.ndim == 2
            ret, buf = cv2.imencode('.png', value)
            assert ret
            path = ZipStorage._join(key, sample_name+'.png')
            self.zipfile.writestr(path, buf)
            return path
        else:
            return value

    def load(self, sample_name, key, rep, modality):
        if modality in {Modality.IMAGE_JPG, Modality.IMAGE_PNG}:
            buf = self.zipfile.read(rep)
            return cv2.cvtColor(cv2.imdecode(
                np.frombuffer(buf, dtype=np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        elif modality in {Modality.IMAGE_LABEL, Modality.IMAGE_GRAY}:
            buf = self.zipfile.read(rep)
            return cv2.imdecode(
                np.frombuffer(buf, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        else:
            return rep

    def save_config(self, config):
        buf = pickle.dumps(config)
        self.zipfile.writestr('config.pk', buf)

    def load_config(self):
        buf = self.zipfile.read('config.pk')
        return _compatible_loads(buf)

    def close(self):
        self.zipfile.close()


class Frozen(Dataset):
    def __init__(self, filename, storage_type=None, storage_args=dict()):
        self.filename = filename
        self.storage_type = storage_type
        if self.storage_type is None:
            if os.path.isdir(self.filename):
                self.storage_type = FilesStorage
            elif self.filename.lower().endswith('.zip'):
                self.storage_type = ZipStorage
        self.storage = None

        self.storage_args = storage_args
        config = self.storage_type(
            self.filename, Mode.READ, **storage_args).load_config()
        self.data = config['data']
        self.modal = config['modal']
        self.extra_data_reps = config.get('extra_data', dict())
        self.extra_data_cache = None

    def setup(self):
        if self.storage is None:
            self.storage = self.storage_type(
                self.filename, Mode.READ, **self.storage_args)

    def extra_data(self):
        if self.extra_data_cache is None:
            self.setup()
            self.extra_data_cache = dict()
            for key, rep in self.extra_data_reps.items():
                modality = self.modal.get(key, Modality.CONFIG)
                self.extra_data_cache[key] = self.storage.load(
                    '_extra_data', key, rep, modality)
        return self.extra_data_cache

    def __len__(self):
        return len(self.data)

    def sample_name(self, index):
        return self.data[index]['sample_name']

    def __getitem__(self, index):
        self.setup()
        d = self.data[index]
        results = dict()
        for key, rep in d.items():
            modality = self.modal.get(key, Modality.CONFIG)
            results[key] = self.storage.load(
                d['sample_name'], key, rep, modality)
        return results

    def __del__(self):
        if self.storage is not None:
            self.storage.close()
        self.storage = None


def freeze(dataset: Dataset, filename: str, modal: Mapping[str, Modality],
           storage_type: Type[Storage] = ZipStorage,
           storage_args: Mapping[str, Any] = dict(),
           with_prog: bool = False, raise_errors: bool = False):
    r"""Freeze a dataset into a storage.

    Args:
        dataset: The dataset to freeze
        filename (str): The filename of the storage
        modal (dict): The modalities for each data tags
        storage_type: A subclass of `haya_data.Storage`, e.g `haya_data.ZipStorage`
        storage_args: The arguments for storage construction        
    """
    if with_prog:
        from tqdm.auto import tqdm
        p = tqdm(range(len(dataset)))
    else:
        p = range(len(dataset))

    if len(dataset) == 0:
        return

    with storage_type(filename, Mode.WRITE, **storage_args) as storage:
        assert isinstance(storage, Storage)
        for key in dataset[0].keys():
            storage.allocate_key(key)

        data = []
        for i in p:
            sample_name = dataset.sample_name(i)
            try:
                d = dataset[i]
            except InterruptedError:
                print('user interrupted')
                break
            except Exception as e:
                if raise_errors:
                    raise e
                print(f'error in sample: {sample_name}')
                print(f'error: {str(e)}')
                continue

            datum = {'sample_name': sample_name}
            for key, value in d.items():
                modality = modal.get(key, Modality.CONFIG)
                datum[key] = storage.save(sample_name, key, value, modality)
            data.append(datum)

        extra_data = dict()  # key -> rep
        for key, value in dataset.extra_data().items():
            modality = modal.get(key, Modality.CONFIG)
            extra_data[key] = storage.save('_extra_data', key, value, modality)

        print(
            f'in total {len(data)} out of {len(dataset)} samples will be stored')
        config = {'data': data, 'modal': modal,
                  'extra_data': extra_data}
        storage.save_config(config)
