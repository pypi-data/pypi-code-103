
import yaml
import pickle
import base64
import gzip
import hashlib
import json
from typing import Any, Union, Type
from .utils import get_path, get_logger, Path
from uuid import uuid4


class Json:

    @classmethod
    def dumps(cls, obj, path: Union[str, Path] = None, *args, **kwargs):
        data = json.dumps(obj, *args, **kwargs)
        if path: 
            path = get_path(path)
            path.write_text(data, encoding='UTF-8')
        return data

    @classmethod
    def loads(cls, obj = None, path: Union[str, Path] = None, *args, **kwargs):
        if path and not obj:
            path = get_path(path)
            obj = path.read_text(encoding='UTF-8')
        return json.loads(obj, *args, **kwargs)

    @classmethod
    def decode(cls, obj, *args, **kwargs):
        if isinstance(obj, dict): return obj
        if isinstance(obj, Type[Any]): 
            try: return obj.dict()
            except: return obj.__dict__
        if isinstance(obj, (str, bytes)): return Json.loads(obj)
        raise ValueError



class Yaml:
    @classmethod
    def dumps(cls, obj, path: Union[str, Path] = None, *args, **kwargs):
        data = yaml.dump(obj, *args, **kwargs)
        if path: 
            path = get_path(path)
            path.write_text(data, encoding='UTF-8')
        return data

    @classmethod
    def loads(cls, obj = None, path: Union[str, Path] = None, *args, **kwargs):
        if path and not obj:
            path = get_path(path)
            obj = path.read_text(encoding='UTF-8')
        return yaml.load(obj, Loader=yaml.Loader, *args, **kwargs)


class Pkl:
    @classmethod
    def dumps(cls, obj, path: Union[str, Path] = None, *args, **kwargs):
        data = pickle.dumps(obj=obj, protocol=pickle.HIGHEST_PROTOCOL, *args, **kwargs)
        if path: 
            path = get_path(path)
            path.write_bytes(data)
        return data


    @classmethod
    def loads(cls, obj = None, path: Union[str, Path] = None, *args, **kwargs):
        if path and not obj:
            path = get_path(path)
            obj = path.read_bytes()
        return pickle.loads(obj, *args, **kwargs)

class Base:
    encoding: str = "UTF-8"
    hash_method: str = "sha256"

    @classmethod
    def b64_encode(cls, text: str) -> str:
        return base64.b64encode(text.encode(encoding=cls.encoding)).decode(encoding=cls.encoding)

    @classmethod
    def b64_decode(cls, data: Union[str, bytes]) -> str:
        if isinstance(data, str): data = data.encode(encoding=cls.encoding)
        return base64.b64decode(data).decode(encoding=cls.encoding)

    @classmethod
    def b64_gzip_encode(cls, text: str) -> str:
        return base64.b64encode(gzip.compress(text.encode(encoding=cls.encoding))).decode(encoding=cls.encoding)

    @classmethod
    def b64_gzip_decode(cls, data: Union[str, bytes]) -> str:
        if isinstance(data, str): data = data.encode(encoding=cls.encoding)
        return gzip.decompress(base64.b64decode(data)).decode(encoding=cls.encoding)

    @classmethod
    def hash_encode(cls, text: str, method: str = 'sha256') -> str:
        encoder = getattr(hashlib, method)
        return encoder(text.encode(encoding=cls.encoding)).hexdigest()

    @classmethod
    def hash_compare(cls, text: str, hashtext: str, method: str = 'sha256') -> bool:
        return bool(cls.hash_encode(text, method) == hashtext)

    @classmethod
    def hash_b64_encode(cls, text: str, method: str = 'sha256') -> str:
        return cls.hash_encode(cls.b64_encode(text), method=method)

    @classmethod
    def hash_b64_gzip_encode(cls, text: str, method: str = 'sha256') -> str:
        return cls.hash_encode(cls.b64_gzip_encode(text), method=method)

    @classmethod
    def hash_b64_compare(cls, hashtext: str, data: Union[str, bytes], method: str = 'sha256') -> bool:
        if isinstance(data, str): return bool(cls.hash_b64_encode(text=data, method=method) == hashtext)
        return bool(cls.b64_decode(data) == hashtext)

    @classmethod
    def hash_b64_gzip_compare(cls, hashtext: str, data: Union[str, bytes], method: str = 'sha256') -> bool:
        if isinstance(data, str): return bool(cls.hash_b64_gzip_encode(text=data, method=method) == hashtext)
        return bool(cls.b64_gzip_decode(data) == hashtext)

    @classmethod
    def hash_b64_compare_match(cls, text: str, data: Union[str, bytes], method: str = 'sha256') -> bool:
        if isinstance(data, str): data = data.encode(encoding=cls.encoding)
        return bool(cls.b64_decode(data) == cls.hash_encode(text, method=method))

    @classmethod
    def hash_b64_gzip_compare_match(cls, text: str, data: Union[str, bytes], method: str = 'sha256') -> bool:
        if isinstance(data, str): data = data.encode(encoding=cls.encoding)
        return bool(cls.b64_gzip_decode(data) == cls.hash_encode(text, method=method))

    @staticmethod
    def get_uuid(*args, **kwargs):
        return str(uuid4(*args, **kwargs))

__all__ = [
    'Json',
    'Yaml',
    'Pkl',
    'Base'
]