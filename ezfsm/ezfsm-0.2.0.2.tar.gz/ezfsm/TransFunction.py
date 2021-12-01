from ezfsm.TimingSeriesFunction import DataArea
from ezfsm.vessel import Vessel
class UnsupportedTransFuncs(Exception):
    def __init__(self, ss):
        super(UnsupportedTransFuncs, self).__init__("\n\n[Error]:TransFuncs with type<%s> is not a valid transFuncs." % str(type(ss)))


class TransFuncKwargs(object):
    key = None
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return {self.key: self.value}

class IfDoc(TransFuncKwargs):
    key = 'cond_doc'
CondDoc = IfDoc

class DoDoc(TransFuncKwargs):
    key = 'exec_doc'
ExecDoc = DoDoc

class BufTs(TransFuncKwargs):
    key = 'buffer_times'
BufTimes = BufTs
BufferTimes = BufTs

class BufFn(TransFuncKwargs):
    key = 'buffer_execution'
BufDo = BufFn
BufFunc = BufFn
BufExec = BufFn
BufExecution = BufFn
BufferFunc = BufFn
BufferExec = BufFn
BufferExecution = BufFn

class BufDoc(TransFuncKwargs):
    key = 'buffer_doc'
BufferDoc = BufDoc

class ActionBuffer(Vessel):
    def __init__(self, max_times, execution, doc, auto_reset=False):
        super(ActionBuffer, self).__init__(max_times)
        self.exec, self.doc = execution, doc
        self.__ar = auto_reset

    def Use(self):
        self.DoDelta(-1)
        if self.exec:
            self.exec()
        if self.IsEmpty():
            if self.__ar:
                self.Reset()
            return True


    def Reset(self):
        self.Full()


class TransFunc(object):  # 最全面的转移函数
    inst = None
    def __init__(self, srt, dst, trans_condition, trans_execution, priority=0, cond_doc="", exec_doc="", buffer_times=0, buffer_execution=None, buffer_doc=''):
        """

        :param srt: 起点的name, 可以是多个节点
        :param dst: 终点的name, 可以是多个节点
        所有节点间两两相连

        :param trans_condition: 触发该转换的条件, 是一个函数 ()，返回True或False
        :param trans_execution: 转换发生时执行的代码. 是一个函数 ()
        :param priority: 检查优先级，越高越先检查
        :param cond_doc: 允许你添加条件说明文档，用于用户分析流程图
        :param exec_doc: 允许你添加转移说明文档，用于用户分析流程图
        :param buffer_times: 允许你设置进入此转移函数所需的缓冲次数
        缓冲:
            当IF的条件检查通过时，状态机会试图执行转移操作
            但是若是存在n次缓冲，则状态机在使n减少1。且在n <= 0前都不执行转移操作
            以下操作会使n被重置:
                1.n次缓冲完毕、执行转移操作后
                2.该state的另一个分支的转移操作被执行
                3.被StateMachine.ResetBuffer重置.
        :param buffer_execution: 触发buffer后执行的代码
        :param buffer_doc: 允许你添加缓冲函数说明文档，用于用户分析流程图
        """
        assert isinstance(srt, (str, tuple, list)), "[Error]:srt can only be str、tuple or list."
        assert isinstance(dst, (str, tuple, list)), "[Error]:srt can only be str、tuple or list."
        assert isinstance(priority, (int, float)), "[Error]:priority can only be int or float."
        self.srt = [srt] if isinstance(srt, str) else list(srt)
        self.dst = [dst] if isinstance(dst, str) else list(dst)
        self.priority = priority
        self.cond = trans_condition
        self.exec = trans_execution
        self.cond_doc = cond_doc
        self.exec_doc = exec_doc
        self.buffer = ActionBuffer(buffer_times, buffer_execution, buffer_doc)

        self.__args, self.__kwds, self.this = (), {}, DataArea()

    def Enable(self, inst):
        self.inst = inst

    def SetPass(self, *args, **kwargs):
        self.__args, self.__kwds = args, kwargs

    def Trig(self):
        if self.cond(*self.__args, **self.__kwds):
            if self.buffer.Use():
                self.exec(*self.__args, **self.__kwds)
                return True
        return False

    def __call__(self, *args, **kwargs):
        self.Trig()

    def __str__(self):
        return "<TransFunc> <%d> %s -> %s\n\tcond: %s\n\texec: %s\n%s"%(
            self.priority,
            self.srt,
            self.dst,
            self.cond,
            self.exec,
            "" if self.buffer.Max() == 0 else "\tbuffer: %d\n\tbuf_exec: %s"%(self.buffer.Max(), self.buffer.exec)
        )

    trig = Trig
