import re
from abc import ABC
from markupsafe import Markup
from deta import Deta
from typing import Dict, Any
import contextlib
from collections import ChainMap

from .utils import json_encode, Variable, is_defined, exist

    
class AbstractField(ABC):
    __positional__ = 'required hidden disabled multiple readonly'.split()
    __keyvalue__ = 'placeholder value max min minlength maxlength step pattern'.split()
    __config__ = [*'transform fsize fclass tag default factory'.split(), *__positional__, *__keyvalue__]
    __config_defaults__ = dict(required=True, fsize=(12,6,3), tag='input:text')
    
    def __init__(self, *args, **kwargs) -> None:
        
        if len(args) > 0:
            if type(args[0]) == str:
                self.owner = None
                self.owner_name = args[0]
            else:
                self.owner = args[0]
                self.owner_name = self.owner.__name__
        else:
            self.owner = Variable.UNDEFINED
            self.owner_name = Variable.UNDEFINED
    
        for key, val in kwargs.items():
            if key in self.__config__:
                setattr(self, key, val)
        for key in self.__config__:
            if not hasattr(self, key):
                if key in self.__config_defaults__.keys():
                    setattr(self, key, self.__config_defaults__[key])
                else:
                    setattr(self, key, Variable.UNDEFINED)


    def get_form_attrs(self):
        result = ''
        for k,v in vars(self).items():
            if is_defined(v):
                if k in self.__keyvalue__:
                    result += f' {k}="{v}"'
                elif k in self.__positional__ and v == True:
                    result += f' {k}'
        return result
        
    def __set_name__(self, obj, name):
        self.public_name = name 
        self.private_name = f'_{name}'

    def pre_validation(self, obj, value):
        if not exist(value):
            if is_defined(self.factory):
                value = self.factory()
            elif is_defined(self.default):
                value = self.default           
        return value
    
    def check_required(self, obj, value):
        if is_defined(self.required):
            if not exist(value):
                raise ValueError(f'{type(obj).__name__}.{self.public_name} cannot be "{value}"')
            
    def post_validation(self, obj, value):
        if exist(value):
            if is_defined(self.transform):
                if not issubclass(type(self), (EnumField, ReferenceField)):
                    return self.transform(value)
        return value
            
            
    def validate(self, obj, value):
        self.check_required(obj, value)
        if exist(value):
            if is_defined(self.min):
                if float(self.min) > value:    
                    raise ValueError(f'{self._name_} of {type(obj).__name__} is "{value}" and cannot be lesser then {self.min}')
            if is_defined(self.max):
                if float(self.max) < value:    
                    raise ValueError(f'{self._name_} of {type(obj).__name__} is "{value}" and cannot be greater then {self.max}')
            if is_defined(self.minlength):
                if float(self.minlength) > len(value):    
                    raise ValueError(f'{self._name_} of {type(obj).__name__} is "{value}" and cannot has length lesser then {self.minlength}')
            if is_defined(self.maxlength):
                if float(self.maxlength) < value:    
                    raise ValueError(f'{self._name_} of {type(obj).__name__} is "{value}" and cannot be greater then {self.maxlength}')
            if is_defined(self.pattern):
                if not re.match(self.pattern, value):
                    raise ValueError(f'{self._name_} of {type(obj).__name__} is "{value}" does not match {self.pattern}')
                    
    def __set__(self, obj, value):
        pre = self.pre_validation(obj, value)
        self.validate(obj, pre)
        post = self.post_validation(obj, pre)
        setattr(obj, self.private_name, post)
        
    def parse(self, obj, value):
        return value 
    
    def __get__(self, obj, owner=None):
        value = getattr(obj, self.private_name)
        return self.parse(obj, value)
    

class  RegularField(AbstractField):
    pass 


class  EnumField(AbstractField):
    pass 

        
class ReferenceField(AbstractField):
    pass 


class AbstractDB(ABC):
    def __init__(self, key=None):
        self.key = key

    
    def sync_connect(self, table: str):
        return Deta(str(self.key)).Base(table)

    async def connect(self, table: str):
        return Deta(str(self.key)).Base(table)

    
    @contextlib.asynccontextmanager
    async def Count(self, table):
        db = await self.connect(table)
        count = 0
        try:
            count = len(db.fetch().items)
        finally:
            yield count
            db.client.close()

    @contextlib.asynccontextmanager
    async def Update(self, table: str, updates: dict, key: str):
        db = await self.connect(table)
        update_dict = {}
        for k, v in updates.items():
            if k == 'set':
                for k1, v1 in v.items():
                    update_dict[k1] = v1
            elif k == 'increment':
                for k1, v1 in v.items():
                    update_dict[k1] = db.util.increment(v1)
            elif k == 'append':
                for k1, v1 in v.items():
                    update_dict[k1] = db.util.append(v1)
            elif k == 'prepend':
                for k1, v1 in v.items():
                    update_dict[k1] = db.util.prepend(v1)
            elif k == 'trim':
                for k1 in v:
                    update_dict[k1] = db.util.trim()
        result = None
        try:
            result = db.update(updates, key)
            yield result
        except BaseException as e:
            print(e.__dict__)
            yield e
        finally:
            db.client.close()

    @contextlib.asynccontextmanager
    async def ListAll(self, table):
        db, result = await self.connect(table), []
        try:
            result = db.fetch().items
        except BaseException as e:
            print(e.__dict__)
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def CheckCode(self, table, code):
        db = await self.connect(table)
        result = None
        try:
            result = db.fetch({'meta.code': code}).items[0]
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def Insert(self, table, data):
        key = data.get("key")
        if not key:
            raise AttributeError("a key is necessary")
        db = await self.connect(table)
        result = None
        try:
            result = db.insert(data)
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def Delete(self, table, key):
        db = await self.connect(table)
        result = None
        try:
            yield db.delete(key=key)
            result = True
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def Put(self, table, data):
        db = await self.connect(table)
        result = None
        try:
            result = db.put(data)
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def Get(self, table, key):
        db = await self.connect(table)
        result = None
        try:
            result = db.get(key=key)
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def SearchPersonByName(self, table, name):
        db = await self.connect(table)
        result = []
        try:
            result = db.fetch({'fullname?contains': name}).items
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def Search(self, table, query=None):
        query = query or {}
        db = await self.connect(table)
        result = []
        try:
            result = db.fetch(query).items
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def First(self, table, query=None):
        query = query or {}
        db = await self.connect(table)
        result = None
        try:
            result = db.fetch(query).items
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def Last(self, table, query={}):
        db = await self.connect(table)
        result = None
        try:
            result =  db.fetch(query).last
        finally:
            yield result
            db.client.close()

    @contextlib.asynccontextmanager
    async def GetOrCreate(self, table: str, data: Dict[ str, Any ]):
        code = data.get('meta', {}).get('code', None) 
        assert code != None, 'CODE could not be found'
        exist, created = None, None
        base = await self.connect(table)
        result = base.fetch({'meta.code': code}).items
        if len(result) >= 1:
            exist = result[0]
        else:
            exist = None
            result = base.put(json_encode(data))
            if result:
                created = result
        try:
            yield exist, created
        finally:
            base.client.close()


class AbstractModel(ABC):
    __objname__ = ''
    __table__ = ''
    __singular__ = ''
    __plural__ = ''
    
    def __init__(self, *args, **kwargs) -> None:
        self._args_ = args 
        self._kwargs_ = kwargs
        for k in self.fields().keys():
            if k in self._kwargs_.keys():
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, None)
                
    @classmethod
    async def list_all(cls, db: AbstractDB):
        db_objects = []
        async with db.ListAll() as result:
            for item in result:
                data = ChainMap({}, item)
                for k in cls.fields().keys():
                    data.update({k: data.get(k)})    
                db_objects.append(cls(**data))
        return db_objects       

    def __extra_fields__(self):
        extra_fields = dict()
        for k,v in self._kwargs_.items():
            if not k in self.fields().keys():
                extra_fields.update({k:v}) 
        return extra_fields
    
    @classmethod
    def __regular_fields__(cls):
        return {k:v for (k,v) in cls.fields().items() if isinstance(v, RegularField)}
    
    @classmethod
    def __reference_fields__(cls):
        return {k:v for (k,v) in cls.fields().items() if isinstance(v, ReferenceField)}
    
    @classmethod
    def __enum_fields__(cls):
        return {k:v for (k,v) in cls.fields().items() if isinstance(v, EnumField)}
    
    def __str_html__(self) -> str:
        return Markup(f'<h3>{str(self)}</h3>')  
        
    def __str__(self) -> str:
        return ', '.join([str(v.__get__(self)) for v in self.fields().values() if exist(v.__get__(self))])
                
    def __repr__(self) -> str:
        return f'{type(self).__name__}({", ".join([f"{k}={str(v.__get__(self))}" for k, v in self.fields().items()])})' 
    
    def __json__(self) -> dict:
        result = {}
        for k,v in self.fields():
            result[k] = json_encode(v.__get__(self))
        return result
    
    @property
    def json(self) -> dict:
        return self.__json__()
    
    @classmethod
    def fields(cls):
        return {k:v for (k,v) in vars(cls).items() if isinstance(v, AbstractField)}

    def defaults(self):
        defaults = {}
        for k,v in self.fields().items():
            if is_defined(v.factory):
                defaults.update({k: v.factory()})  
            elif is_defined(v.default):
                defaults.update({k: v.default})
        return defaults


class AbstractManager(ABC):
    
    @classmethod 
    def parse_to_db(cls, instance: AbstractModel):
        return instance.json
        
    @classmethod
    async def create(cls, instance: AbstractModel, db: AbstractDB):
        async with db.Put(instance.__table__, ) as created:
            if created:
                return type(instance)(**created)
            return 