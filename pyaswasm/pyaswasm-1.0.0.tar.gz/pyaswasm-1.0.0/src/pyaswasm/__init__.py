from wasmer import engine, Store, Memory, Module, Instance, ImportObject, Function, Type, FunctionType, Global, GlobalType, Uint8Array, Uint16Array, Uint32Array  # type: ignore
from wasmer_compiler_cranelift import Compiler  # type: ignore
from typing import Dict, Any, Union, List, Tuple
import random
import struct
import functools

ID_OFFSET = -8
SIZE_OFFSET = -4

ARRAYBUFFER_ID = 0
STRING_ID = 1

ARRAYBUFFERVIEW = 1 << 0
ARRAY = 1 << 1
STATICARRAY = 1 << 2
VAL_ALIGN_OFFSET = 6
VAL_SIGNED = 1 << 11
VAL_FLOAT = 1 << 12
VAL_MANAGED = 1 << 14

ARRAYBUFFERVIEW_BUFFER_OFFSET = 0
ARRAYBUFFERVIEW_DATASTART_OFFSET = 4
ARRAYBUFFERVIEW_DATALENGTH_OFFSET = 8
ARRAYBUFFERVIEW_SIZE = 12
ARRAY_LENGTH_OFFSET = 12
ARRAY_SIZE = 16

STRING_DECODE_THRESHOLD = 32

class ASObject:
    '''Wrapper of the classes from the imported AS module

    this class used when we obtain pointer form the module mamory and wrap it inside some class
    it automatically pin pointer when it created and unpin it, when it should be deleted
    so, it does not require any additional control of the life cycle
    '''
    _module = None  # add this for mypy
    _ptr = 0

    def __del__(self):
        self._module.unpin(self._ptr)

    def __repr__(self):
        return f"<{type(self).__name__}@{self._ptr}>"

    def __eq__(self, other: Any):
        if isinstance(other, ASObject):
            return self._ptr == other._ptr
        return False

    @classmethod
    def create(cls, ptr: int):
        obj = object.__new__(cls)
        obj._ptr = ptr
        obj._module.pin(ptr)
        return obj

    def __init__(self, *arg, **kwarg):
        raise TypeError("Use .create()")

def convert_arguments(args: List[Any]):
    '''this method needs when we pass arguments to the exported function
    if argument is a primitive type (int or float) then it can be passed as it
    but if the argument is an object then we need pass pointer to this object
    '''
    return [v._ptr if isinstance(v, ASObject) else v for v in args]

def make_method(f: Function):
    '''change function in such a way that instead of raw arguments it use pointers to objects or primitive values
    '''
    @functools.wraps(f)
    def wrapped(*args):
        value = f(*convert_arguments(args))
        return value
    return wrapped

def make_class(class_name: str, class_exports: Dict[str, Function], module) -> Union[type, None]:
    if not "constructor" in class_exports:
        return None
    ctor = class_exports.pop("constructor")
    attrs = {}
    props: Dict[str, Dict[str, Function]] = {}
    for name, func in class_exports.items():
        if ":" in name:
            op, propname = name.split(":")
            if op in ("set", "get"):
                props.setdefault(propname, {})[op] = func
                continue
        attrs[name] = make_method(func)
    for name, definition in props.items():
        attrs[name] = property(make_method(definition["get"]), make_method(definition["set"]) if "set" in definition else None, )
    
    def __new__(cls, *args):
        _ptr = ctor(0, *convert_arguments(args))
        module.pin(_ptr)
        obj = object.__new__(cls)
        obj._ptr = _ptr
        return obj

    def __init__(self, *arg, **kwarg):
        # object initialized in the WASM side by calling ctor() method
        pass

    def wrap(cls, ptr: int):
        # when we call wrap, then the object alreay initialized on WASM side and we need only references to it methods
        return cls.create(ptr)

    # setup class attributes
    attrs.update({
        "_module": module,  # store reference to the module, it allows to use it in the base class (for pin-ing and unpin-ing)
        "__new__": __new__,  # we does not need __del__ method, because it implemented in the base class ASObject
        "__init__": __init__,  # this is dummy method, because we initialize data by usin exported "construction" method (ctor) 
        "wrap": classmethod(wrap)
    })

    return type(class_name, (ASObject,), attrs)

class ASModule():
    clz32 = lambda n:35-len(bin(-n))&~n>>32

    def __init__(self, wasm_file: str, imports=None, engine=None):
        store = Store() if engine is None else Store(engine)
        module = Module(store, open(wasm_file, "rb").read())
        import_object = ImportObject()
        if imports is None:
            imports = {}
        for k, v in imports.items():
            v.module = self
        # add default callbacks
        if ("env", "abort") not in imports:
            imports[("env", "abort")] = self._abort
        if ("env", "seed") not in imports:
            imports[("env", "seed")] = self._seed
        if ("env", "trace") not in imports:
            imports[("env", "trace")] = self._trace

        # prepare names of import groups
        import_groups = []
        for k in imports:
            if k[0] not in import_groups:
                import_groups.append(k[0])

        # import functions for each group
        for group in import_groups:
            import_group_dict: Dict[str, Function] = {}
            for k, v in imports.items():
                if k[0] == group:
                    import_group_dict[k[1]] = Function(store, v)
            import_object.register(group, import_group_dict)

        self.instance = Instance(module, import_object)
        self._exports = self.instance.exports

        # check is module contains runtime
        self._is_runtime = True
        try:
            self.new
            self._is_runtime = True
        except Exception as e:
            self._is_runtime = False

        # check memory in the module
        try:
            self.memory = self.instance.exports.memory
            self._is_memory = True
        except Exception as e:
            self._is_memory = False

        # next parse methods and classes
        self.global_names = []
        class_dict = {}  # store here all functions from the module
        self.functions_dict = {}
        self.classes_dict: Dict[str, Dict[str, Function]] = {}  # store here data about exported classes: class name and it methods
        for i in range(len(self._exports)):
            exp = module.exports[i]
            e_name = exp.name
            e_type = exp.type
            if isinstance(e_type, FunctionType):
                # functions
                if '#' in e_name:
                    classname, funcname = e_name.split('#', 1)
                    self.classes_dict.setdefault(classname, {})
                    self.classes_dict[classname][funcname] = getattr(self._exports, e_name)
                elif e_name.startswith('__'):
                    # do nothing
                    pass
                else:
                    class_dict[e_name] = make_method(getattr(self._exports, e_name))  # override function, and all ASObject arguments convert to it pointers
                    self.functions_dict[e_name] = getattr(self._exports, e_name)
            elif isinstance(e_type, GlobalType):
                # globals
                self.global_names.append(e_name)
            else:
                pass

        for class_name, class_exports in self.classes_dict.items():
            class_dict[class_name] = make_class(class_name, class_exports, self)

        self.__dict__.update(class_dict)

    def __getattr__(self, item: str):
        if item in self.global_names:
            return getattr(self.instance.exports, item).value
        else:
            return getattr(self.instance.exports, item)

    # runtime methods
    @property
    def rtti_base(self):
        if not self._is_runtime:
            raise Exception("module does not contains runtime, __rtti_base is None")
        return getattr(self.instance.exports, "__rtti_base")

    @property
    def new(self):
        if not self._is_runtime:
            raise Exception("module does not contains runtime, allocating is impossible")
        return getattr(self.instance.exports, "__new")

    @property
    def pin(self):
        if not self._is_runtime:
            raise Exception("module does not contains runtime")
        return getattr(self.instance.exports, "__pin")

    @property
    def unpin(self):
        if not self._is_runtime:
            raise Exception("module does not contains runtime")
        return getattr(self.instance.exports, "__unpin")

    @property
    def collect(self):
        if not self._is_runtime:
            raise Exception("module does not contains runtime, garbage collection is inaccessible")
        return getattr(self.instance.exports, "__collect")

    # default callbacks
    def _abort(self, message_ptr: int, file_name_ptr: int, line: int, colum: int):
        msg_str: str = self.get_string(message_ptr)
        file_str: str = self.get_string(file_name_ptr)
        raise RuntimeError(f"abort: {msg_str} at {file_str}:{line}:{colum}")

    def _trace(self, message_ptr: int, n: int):
        msg_str: str = self.get_string(message_ptr)
        raise RuntimeError(f"trace: {msg_str}")

    def _seed(self)-> float:
        return random.random()

    # internal methods
    def _get_rtti_count(self, view: Uint32Array) -> int:
        return view[self.rtti_base.value // 4]

    def _get_info(self, id: int) -> int:
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        view_32: Uint32Array = self.memory.uint32_view()
        count: int = self._get_rtti_count(view_32)
        if id >= count:
            raise ValueError(f"invalid id: {id}")
        return view_32[((self.rtti_base.value + 4) // 4) + id * 2]

    def _get_array_info(self, id: int) -> int:
        type_info: int = self._get_info(id)
        if not(type_info & (ARRAYBUFFERVIEW | ARRAY | STATICARRAY)):
            raise TypeError(f"not an array: {id}, flags={type_info}")
        return type_info

    def _get_base(self, id: int) -> int:
        view_32: Uint32Array = self.memory.uint32_view()
        count: int = self._get_rtti_count(view_32)
        if id >= count:
            raise ValueError("invalid id: {id}")
        return view_32[((self.rtti_base.value + 4) // 4) + id * 2 + 1]

    def _get_value_align(self, info: int) -> int:
        return 31 - ASModule.clz32((info // (2**VAL_ALIGN_OFFSET)) & 31)

    def _get_view(self, align_log_2: int, is_signed: bool, is_float: bool) -> Union[Uint8Array, Uint16Array, Uint32Array]:
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        if is_float:
            if align_log_2 == 2:
                # float32
                return self.memory.uint8_view()
            elif align_log_2 == 3:
                # float64
                return self.memory.uint8_view()
        else:
            if align_log_2 == 0:
                return self.memory.int8_view() if is_signed else self.memory.uint8_view()
            elif align_log_2 == 1:
                return self.memory.int16_view() if is_signed else self.memory.uint16_view()
            elif align_log_2 == 2:
                return self.memory.int32_view() if is_signed else self.memory.uint32_view()
        raise ValueError(f"unsupported align: {align_log_2}")

    def _get_string_impl(self, ptr: int) -> str:
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        view_32: Uint32Array = self.memory.uint32_view()
        view_8: Uint8Array =self. memory.uint8_view()
        string_length: int = view_32[int((ptr + SIZE_OFFSET) / 4)]
        if string_length:
            string_bytes: List[int] = view_8[ptr:ptr+string_length]
            return bytes(string_bytes).decode('utf-16')
        else:
            return ""

    # output methods
    def new_string(self, string: str) -> int:
        '''write input string to WASM memory and return pointer to corresponding data block
        '''
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        length: int = len(string)
        ptr: int = self.new(length * 2, STRING_ID)
        view_8: Uint8Array = self.memory.uint8_view(ptr)
        string_bytes: bytes = string.encode("utf-16le")
        view_8[:len(string_bytes)] = string_bytes
        return ptr

    def get_string(self, ptr: int) -> str:
        '''convert pointer to the string in the WASM memory to actual Python string
        '''
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        view: Uint32Array = self.memory.uint32_view()
        type_id: int = view[int((ptr + ID_OFFSET) / 4)]
        if type_id != STRING_ID:
            raise TypeError(f"not a string {ptr}, the type is {type_id}")
        else:
            return self._get_string_impl(ptr)

    def get_array_view(self, ptr: int) -> Tuple[Union[Uint8Array, Uint16Array, Uint32Array], int, int]:
        '''return memory view, start and finish index in this view

        works only with integer types, because wasmer has only int views
        for float array return bytes view and the difference (finish - start) is equal to the number of elements times size of an each element (3 or 4 bytes)
        '''
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")

        view_32: Uint32Array = self.memory.uint32_view()
        type_id: int = view_32[(ptr + ID_OFFSET) // 4]
        type_info: int = self._get_array_info(type_id)
        type_bytes: int = self._get_value_align(type_info)
        array_start: int = ptr if (type_info & STATICARRAY) else view_32[(ptr + ARRAYBUFFERVIEW_DATASTART_OFFSET) // 4]
        length: int = view_32[(ptr + ARRAY_LENGTH_OFFSET) // 4] if (type_info & ARRAY) else view_32[(array_start + SIZE_OFFSET) // 4] // (2**type_bytes)
        is_float: bool = bool(type_info & VAL_FLOAT)
        is_signed: bool = bool(type_info & VAL_SIGNED)
        start_ptr: int = array_start if is_float else array_start // 2**type_bytes
        return self._get_view(type_bytes, is_signed, is_float), start_ptr, start_ptr + ((4 if type_bytes == 2 else 8) * length if is_float else length)

    def new_array(self, id: int, values: List[Union[int, float, ASObject]]) -> int:
        '''write down array values to the WASM memory and retrun pointer to the corresponding data block
        '''
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        type_info: int = self._get_array_info(id.value if isinstance(id, Global) else id)
        align: int = self._get_value_align(type_info)
        length: int = len(values)
        array_start: int = self.new(length * 2**align, id if bool(type_info & STATICARRAY) else ARRAYBUFFER_ID)
        result: int
        if bool(type_info & STATICARRAY):
            result = array_start
        else:
            self.pin(array_start)
            arr: int = self.new(ARRAY_SIZE if bool(type_info & ARRAY) else ARRAYBUFFERVIEW_SIZE, id.value if isinstance(id, Global) else id)
            self.unpin(array_start)
            view_32: Uint32Array = self.memory.uint32_view()
            view_32[(arr + ARRAYBUFFERVIEW_BUFFER_OFFSET) // 4] = array_start
            view_32[(arr + ARRAYBUFFERVIEW_DATASTART_OFFSET) // 4] = array_start
            view_32[(arr + ARRAYBUFFERVIEW_DATALENGTH_OFFSET) // 4] = length * 2**align
            if bool(type_info & ARRAY):
                view_32[(arr + ARRAY_LENGTH_OFFSET) // 4] = length
            result = arr
        view: Union[Uint8Array, Uint16Array, Uint32Array] = self._get_view(align, bool(type_info & VAL_SIGNED), bool(type_info & VAL_FLOAT))
        if bool(type_info & VAL_FLOAT):
            # set values of the float array
            if align == 2:
                view[array_start:array_start + 4*length] = struct.pack("%sf" % len(values), *values)
            elif align == 3:
                view[array_start:array_start + 8*length] = struct.pack("%sd" % len(values), *values)
            else:
                raise ValueError(f"unsupported align: {align}")
        else:
            # set integer array
            for i in range(length):
                v: Union[int, float, ASObject] = values[i]
                if isinstance(v, ASObject):
                    view[(array_start // 2**align) + i] = v._ptr
                else:
                    view[(array_start // 2**align) + i] = v
        return result

    def get_array(self, ptr: int) -> List[Union[int, float]]:
        '''convert pointer to the array in the WASM memory to actual Python array

        if values of the array are float or int, then it returns these values
        if values are objects, then it returns pointers to these objects in the WASM memory

        this method return copy of the data in the momory
        if you wuold like to change array values inside WASM memory, use the method get_array_view(ptr)
        '''
        if not self._is_memory:
            raise Exception("memory is inaccessible in the module")
        view_32: Uint32Array = self.memory.uint32_view()
        type_id: int = view_32[(ptr + ID_OFFSET) // 4]
        type_info: int = self._get_array_info(type_id)
        if bool(type_info & VAL_FLOAT):
            # this is float array
            align: int = self._get_value_align(type_info);  # 2 - f32, 3 - f64
            array_start: int = ptr if (type_info & STATICARRAY) else view_32[(ptr + ARRAYBUFFERVIEW_DATASTART_OFFSET) // 4]
            length: int = view_32[(ptr + ARRAY_LENGTH_OFFSET) // 4] if (type_info & ARRAY) else view_32[(array_start + SIZE_OFFSET) // 4] // (2**align)
            start_ptr: int = array_start // 2**align
            if length == 0:
                return []
            view_8: Uint8Array = self.memory.uint8_view()
            if align == 2:
                return list(struct.unpack("%sf" % length, bytes(view_8[array_start:array_start+4*length])))
            elif align == 3:
                return list(struct.unpack("%sd" % length, bytes(view_8[array_start:array_start+8*length])))
            else:
                raise ValueError(f"unsupported align: {align}")
        else:
            view, start, finish = self.get_array_view(ptr)
            if finish <= start:
                return []
            return view[start:finish]

    def is_instance(self, ptr: int, base_id: int) -> bool:
        '''return True if data in the WASM memory with ptr address has base_id type and False otherwise

        base_id is values which should be exported in the module and can be obtained from global module values
        '''
        view_32: Uint32Array = self.memory.uint32_view()
        type_id: int = view_32[(ptr + ID_OFFSET) // 4]
        if (type_id <= self._get_rtti_count(view_32)):
            while type_id:
                if type_id == base_id:
                    return True
                type_id = self._get_base(type_id)
        return False

    def description(self) -> str:
        '''return string description of the module, i.e. exported global values, functions and classes
        '''
        def id_to_type(id: int) -> str:
            if id == 1:
                return "int32"
            elif id == 2:
                return "int64"
            elif id == 3:
                return "float32"
            elif id == 4:
                return "float64"
            else:
                return "unknown"

        to_return = []
        if len(self.global_names) > 0:
            to_return.append("Globals:")
            for gn in self.global_names:
                to_return.append("\t" + gn)
        if len(self.functions_dict) > 0:
            to_return.append("Functions:")
            for item, value in self.functions_dict.items():
                f_in_params: List[int] = value.type.params
                f_out_params: List[int] = value.type.results
                to_return.append("\t" + item + "(" + ", ".join([id_to_type(v) for v in f_in_params]) + ") -> " + ("void" if len(f_out_params) == 0 else ", ".join([id_to_type(v) for v in f_out_params])))
        if len(self.classes_dict) > 0:
            to_return.append("Classes:")
            for item, value in self.classes_dict.items():
                to_return.append("\t" + item + ":")
                for f_name, f in value.items():
                    if (not "get:" in f_name) and (not "set:" in f_name):
                        in_params: List[int] = f.type.params
                        out_params: List[int] = f.type.results
                        to_return.append("\t\t" + f_name + "(" + ", ".join([id_to_type(v) for v in in_params]) + ") -> " + ("void" if len(out_params) == 0 else ", ".join([id_to_type(v) for v in out_params])))
        if len(to_return) == 0:
            return "module is empty"
        return "\n".join(to_return)
