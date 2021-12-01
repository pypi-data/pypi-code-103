"""
允许为用户的函数提供额外的可供访问的运行环境:
    mach: 当前正在运行的状态机 的运行环境
    inst: 当前状态节点 的运行环境
    dest: 目标状态节点 的运行环境
    this: 转移函数自身 的运行环境

    性能测试:(测试用函数见尾部)(单位s)
    传统1: 0.10
    委托1: 0.29
    传统2: 0.16
    委托2: 3.81
    委托2(快速模式): 1.9
    委托2(单次全局设置): 0.34

"""
from ezfsm.DataArea import *

_base_machine, _base_inst, _base_dest, _base_this = DataArea(), DataArea(), DataArea(), DataArea()

_proxy_binds = {}

class Proxy:
    def __init__(self):
        _proxy_binds[self] = None

    def _proxy_bind(self, obj):
        _proxy_binds[self] = obj

    def __getattr__(self, item):
        return getattr(_proxy_binds[self], item)

    def __setattr__(self, key, value):
        setattr(_proxy_binds[self], key, value)


mach, inst, dest, this = Proxy(), Proxy(), Proxy(), Proxy()
mach._proxy_bind(_base_machine)
inst._proxy_bind(_base_inst)
dest._proxy_bind(_base_dest)
this._proxy_bind(_base_this)
GlobalArea = DataArea()

def ChangeGlobal(area, _machine: DataArea, _inst: DataArea, _dest: DataArea, _this: DataArea):
    area.rec_machine, area.rec_inst, area.rec_dest, area.rec_this = mach._proxy_obj, inst._proxy_obj, dest._proxy_obj, this._proxy_obj
    mach._proxy_bind(_machine)
    inst._proxy_bind(_inst)
    dest._proxy_bind(_dest)
    this._proxy_bind(_this)

def ChangeGlobal_Machine(area, _machine: DataArea):
    area.rec_machine = _proxy_binds[mach]
    mach._proxy_bind(_machine)

def ChangeGlobal_Inst(area, _inst: DataArea):
    area.rec_inst = _proxy_binds[inst]
    inst._proxy_bind(_inst)

def ChangeGlobal_Dest(area, _dest: DataArea):
    area.rec_dest = _proxy_binds[dest]
    dest._proxy_bind(_dest)

def ChangeGlobal_This(area, _this: DataArea):
    area.rec_this = _proxy_binds[this]
    this._proxy_bind(_this)

def ChangeGlobalBack(area):
    if getattr(area, 'rec_machine') and getattr(area, 'rec_inst') and getattr(area, 'rec_dest') and getattr(area, 'rec_this'):
        mach._proxy_bind(area.rec_machine)
        inst._proxy_bind(area.rec_inst)
        dest._proxy_bind(area.rec_dest)
        this._proxy_bind(area.rec_this)
    else:
        raise Exception("\n\n[Error]: This DataArea Doesn't contain needy attributes.")

def ChangeGlobalBack_NoCheck(area):
    mach._proxy_bind(area.rec_machine)
    inst._proxy_bind(area.rec_inst)
    dest._proxy_bind(area.rec_dest)
    this._proxy_bind(area.rec_this)

def OuterAreaCall(func, _machine: DataArea, _inst: DataArea, _dest: DataArea, _this: DataArea, *args, **kwargs):
    """
    允许在运行特定代码期间修改machine、 inst、 this, 使其重新临时委托绑定到新的对象
    :param func: 待调用的函数
    :param _machine: 运行期间特定的machine
    :param _inst: 运行期间特定的inst
    :param _dest: 运行期间特定的dest
    :param _this: 运行期间特定的this
    :param args: 待调用的函数(func) 的*args参数
    :param kwargs: 待调用的函数(func) 的**kwargs参数
    :return: 待调用的函数(func) 的返回值
    """
    area = DataArea()
    ChangeGlobal(area, _machine, _inst, _dest, _this)  # DataArea doesn't need some attrs in the first step
    _return = func(*args, **kwargs)
    ChangeGlobalBack_NoCheck(area)
    return _return


def GlobalOuterAreaCall(func, _machine: DataArea, _inst: DataArea, _dest: DataArea, _this: DataArea, *args, **kwargs):
    """
    使用全局GlobalArea，其余同上
    """
    ChangeGlobal(GlobalArea, _machine, _inst, _dest, _this)  # DataArea doesn't need some attrs in the first step
    _return = func(*args, **kwargs)
    ChangeGlobalBack_NoCheck(GlobalArea)
    return _return


def QuickOuterAreaCall(func, _machine: DataArea, _inst: DataArea, _dest: DataArea, _this: DataArea, *args, **kwargs):
    """
    允许在运行特定代码期间修改machine、 inst、 this, 使其重新委托绑定到新的对象
    :param func: 待调用的函数
    :param _machine: 运行期间特定的machine
    :param _inst: 运行期间特定的inst
    :param _dest: 运行期间特定的dest
    :param _this: 运行期间特定的this
    :param args: 待调用的函数(func) 的*args参数
    :param kwargs: 待调用的函数(func) 的**kwargs参数
    :return: 待调用的函数(func) 的返回值
    """
    mach._proxy_bind(_machine)
    inst._proxy_bind(_inst)
    dest._proxy_bind(_dest)
    this._proxy_bind(_this)
    _return = func(*args, **kwargs)
    return _return



"""
from TimingSeriesFunction import *
import time

my_this = DataArea()


def test():
    this.a = 10


def test2():
    my_this.a = 10


this.a = 999
my_this.a = 114.514

a = time.time()
for i in range(921600):
    my_this.a = 10
print("传统赋值耗时: {}s".format(time.time() - a))

a = time.time()
for i in range(921600):
    this.a = 10
print("包装赋值耗时: {}s".format(time.time() - a))

a = time.time()
for i in range(921600):
    test2()
print("传统赋值耗时(函数): {}s".format(time.time() - a))

a = time.time()
for i in range(921600):
    OuterAreaCall(test, mach, inst, my_this)
print("包装赋值耗时(函数): {}s".format(time.time() - a))

a = time.time()
for i in range(921600):
    QuickOuterAreaCall(test, mach, inst, my_this)
print("包装赋值耗时(函数)(快速): {}s".format(time.time() - a))

a = time.time()
ChangeGlobal(GlobalArea, mach, inst, my_this)
for i in range(921600):
    test()
ChangeGlobalBack(GlobalArea)
print("包装赋值耗时(函数)(单次): {}s".format(time.time() - a))
exit()
"""
