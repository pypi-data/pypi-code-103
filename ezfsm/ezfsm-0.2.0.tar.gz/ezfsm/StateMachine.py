from ezfsm.TimingSeriesFunction import *
from ezfsm.TransFunction import *
from ezfsm.StateNode import *
from ezfsm.StateSet import *

class StateNotInSets(Exception):
    def __init__(self, name):
        super(StateNotInSets, self).__init__("\n\n[Error]: state <{}> doesn't exist in state sets.".format(name))

class NotImplementBuildUp(Exception):
    def __init__(self):
        super(NotImplementBuildUp, self).__init__("\n\n[Error]: StateMachine need build first.")

class StateMachine_const(object):
    RAW = 0
    READY = 1
    BUSY = 2
    FINISH = 3


class StateMachine_cb(StateMachine_const):
    end_cb = None
    trans_cb = None
    start_cb = None
    def SetWhenEnd(self, end_func):
        """
        设置结束回调
        :param end_func: end_func(self), None表示关闭回调
        :return:
        """
        self.end_cb = end_func

    def SetWhenTrans(self, trans_func):
        """
        设置转移结束回调
        :param trans_func: trans_func(self, srt, dest, tf), None表示关闭回调
        :return:
        """
        self.trans_cb = trans_func

    def SetWhenStart(self, start_func):
        """
        设置启动回调
        :param start_func: start_func(self), None表示关闭回调
        :return:
        """
        self.start_cb = start_func

class StateMachine_area(StateMachine_const):
    machine_area = DataArea()
    inst_areas = {}  # 编译前不可使用
    this_areas = {}  # 编译前不可使用
    ready = 0
    st = {}
    def ResetAreas(self):
        if self.ready < self.READY:
            raise NotImplementBuildUp()
        self.machine_area = DataArea()
        self.inst_areas = {}  # 编译前不可使用
        self.this_areas = {}  # 编译前不可使用

        for k in self.st:
            self.inst_areas[k] = DataArea()
            self.this_areas[k] = []
            for item in self.st[k]:
                self.this_areas[k] += [DataArea()]


class StateMachine_data(object):
    NOT = 0
    MAYBE = 1
    SURE = 2
    def __init__(self, *args, start=None, end=None):
        """
        用户可以只传trans_funcs这个参数，PyState会自动提取节点名
        :param arg1: 可以为state sets (记做sets tfs 正常模式)， 也可以是tfs (记做auto-sets tfs 自动补全模式)
        :param arg2: 正常模式时: tfs; 自动补全模式时: start(可省略)
        :param arg3: 正常模式时: start(可省略); 自动补全模式时: end(可省略)
        :param arg4: 正常模式时: end(可省略); 自动补全模式时: 不需要该参数，传入会产生歧义，可能会导致程序产生Exception

        当start和end通过kwargs传递时，可以忽略args中的start和end
        """
        self.raw_ss, self.raw_tfs = None, None
        self.start, self.end, self.now = None, None, None

        self.ParseArgs(args)
        if start:
            self.start = start
        if end:
            self.end = end
        self.dis_rec_log_flag = True
        self.show_log_flag = True
        self.raw_ss_auto_fill_flag = False


        self.log = []

    def ParseArgs(self, args):
        """
        解析用户的参数，判断类别
        :param args:
        :return:
        """
        _len = len(args)
        if not _len:  # _len == 0:
            raise Exception("\n\n[Error]: Get nothing from the params. ")
        elif _len == 1:  # tfs mode
            self.raw_ss, self.raw_tfs = None, args[0]
        elif _len == 2:  # sets-tfs mode | tfs mode + start
            if self.CanBeTransFuncs(args[0]):
                self.raw_ss, self.raw_tfs, self.start = None, args[0], args[1]
            elif self.CanBeStateSets(args[0]):
                self.raw_ss, self.raw_tfs = args
            else:
                raise Exception("\n\n[Error]: Unsupported Pass params. Please check your params.")
        elif _len == 3:  # sets-tfs mode + start | tfs mode + start + end
            if self.CanBeTransFuncs(args[0]):
                self.raw_ss, self.raw_tfs, self.start, self.end = None, args[0], args[1], args[2]
            elif self.CanBeStateSets(args[0]):
                self.raw_ss, self.raw_tfs, self.start = args
            else:
                raise Exception("\n\n[Error]: Unsupported Pass params. Please check your params.")
        elif _len == 4:  # sets-tfs mode + start + end
            self.raw_ss, self.raw_tfs, self.start, self.end = args
        else:
            raise Exception("\n\n[Error]: Expected params up to 4, but got " + str(_len))

    def CanBeStateSets(self, item):
        """
        state sets 只能是非空一维可变可迭代对象

        注意: item必须是可以变动内容值的容器(不可变动值的容器只支持tuple)
        注意: trans funcs能通过此检查
        :param item:
        :return:
        """
        try:
            iter(item)
            if not isinstance(item, tuple):
                item[0] = item[0]
            try:
                iter(item)
                item[0][0] = item[0][0]
                return self.NOT
            except:
                return self.SURE
        except:
            return self.NOT


    def CanBeTransFuncs(self, item):
        """
        trans funcs
            可以是非空一维TF对象， SURE
            可以是非空二维可变可迭代对象， SURE
            可以是字符串对象 MAYBE

        注意: item必须是可以变动内容值的容器(不可变动值的容器只支持tuple)
        注意: state sets不能通过此检查
        :param item:
        :return:
        """
        if isinstance(item, str):
            return self.MAYBE

        try:
            iter(item)
            if not isinstance(item, tuple):
                item[0] = item[0]
            try:
                iter(item[0])
                if not isinstance(item[0], tuple):
                    item[0][0] = item[0][0]
                try:
                    iter(item[0][0])
                    item[0][0][0] = item[0][0][0]
                    return self.NOT
                except:
                    return self.SURE
            except:
                if isinstance(item[0], TransFunc):
                    return self.SURE
                else:
                    return self.NOT

        except:
            return self.NOT

    def TidyStateSets(self, ss):
        """
        标准化用户传入的state sets
        因为这些ss可能不是标准的状态集
        在BuildUp前都不做转化，允许用户修改它们的源参数
        :param ss:
        :return:
        """
        if isinstance(ss, StateSet):
            return ss
        elif isinstance(ss, (tuple, list)):
            return StateSet(ss)
        else:
            try:
                iter(ss)
                print("[Warning]: %s is an unusual iterable object<type: %s>. It may cause Exception in running. "%(str(ss), str(type(ss))))
                self.Log("Trans an unusual iterable object<type: {}> to general StateSet.".format(type(ss)))
                return StateSet(list(ss))
            except:
                raise UnsupportedStateSet(ss)


    def TidyTransFuncs(self, tfs):
        """
        标准化用户传入的trans funcs
        因为这些tfs可能不是标准的转移集
        在BuildUp前都不做转化，允许用户修改它们的源参数
        :param tfs:
        :return:
        """
        if isinstance(tfs, str):
            return self.ParseStringTransFuncs(tfs)
        else:
            try:
                iter(tfs)
                if not tfs: raise Exception("\n\n[Error]: transFuncs can not be empty.")
                if isinstance(tfs[0], TransFunc):
                    return list(tfs)
                try:
                    iter(tfs[0])
                    # 在初始化时已经检查过了，不应该是三维的
                    return self.Parse2DTransFuncs(tfs)
                except:
                    raise UnsupportedTransFuncs(tfs)
            except:
                raise UnsupportedTransFuncs(tfs)

    @staticmethod
    def Parse2DTransFuncs(params_tfs):
        try:
            tfs = []
            for _args in params_tfs:
                args, kwargs = [], {}
                for arg in _args:
                    if isinstance(arg, TransFuncKwargs):
                        kwargs.update(arg())
                    else:
                        args += [arg]

                tfs += [TransFunc(*args, **kwargs)]
            return tfs
        except:
            raise Exception("\n\n[Error]: Try parse 2DTransFunc, but failed. Please check your params.")

    def ParseStringTransFuncs(self, str_tfs):
        """
        将字符串格式的转移描述 转换为 TF描述
        :param str_tfs:
        :return:
        """
        raise Exception("\n\n[Error]:暂未开放. It will be available later.")

    def Log(self, add=None):
        if add is None:
            return self.log
        else:
            if self.dis_rec_log_flag:
                self.log += [add]
                if self.show_log_flag: print(add)

    def EnableLogRecord(self, value=True):
        self.dis_rec_log_flag = value

    def EnableLogPrint(self, value=True):
        self.show_log_flag = value

    def AddState(self, *states):
        self.raw_ss += list(states)
        for state in states:
            self.Log("User add state: <%s>"%state)

    def AddTransFunc(self, *tfs):
        self.raw_tfs += list(tfs)
        for tf in tfs:
            self.Log("User add transFunc: <%s>" % tf)

    def Config(self, start=None, end=None):
        """
        设置起点和终点
        :param start: str, None时不修改此项
        :param end: str, None时不修改此项
        :return:
        """
        if start is not None:
            if self.raw_ss and start not in self.raw_ss:
                raise StateNotInSets(start)
            self.start = start
        if end is not None:
            if self.raw_ss and end not in self.raw_ss:
                raise StateNotInSets(end)
            self.end = end

    def ResetBuffer(self, srt, dst):
        """
        重置指定连接的缓冲
        :param srt:
        :param dst:
        :return:
        """
        if not self.st.get(srt): raise StateNotInSets(srt)
        if not self.st.get(dst): raise StateNotInSets(dst)
        for _srt, _dst, _tf in self.st[srt]:
            if _dst == dst:
                _tf.buffer.Reset()

    def GetTidiedInputParams(self):
        ss, tfs = [], []
        if self.raw_ss is None:
            self.raw_ss_auto_fill_flag = True
        else:
            ss = self.TidyStateSets(self.raw_ss)
        
        if self.raw_tfs is None: 
            raise Exception("\n\n[Error]:TransFuncs can not be empty.")
        else:
            tfs = self.TidyTransFuncs(self.raw_tfs)
        
        return ss, tfs

    def TidyStartAndEnd(self, raw_ss, raw_tfs):
        if self.start is None or self.end is None:
            if self.raw_ss_auto_fill_flag:
                if self.start is None and self.end is None and len(raw_tfs) >= 1:
                    self.start, self.end = raw_tfs[0].srt[0], raw_tfs[-1].dst[-1]
                    self.Log("No set <start> <end>, Auto Set : {start <- %s, end <- %s}" % (self.start, self.end))
                elif self.start is None and self.end is not None and len(raw_tfs) >= 1:
                    self.start = raw_tfs[0].srt[0]
                    self.Log("No set <start>, Auto Set : {start <- %s}" % self.start)
                elif self.start is not None and self.end is None and len(raw_tfs) >= 1:
                    self.end = raw_tfs[-1].dst[-1]
                    self.Log("No set <end>, Auto Set : {end <- %s}" % self.end)
                else:
                    raise Exception(
                        "\n\n[Error]: StateMachine must have a start-node and a end-node.\n\t--At least, you need pass transFuncs which length >= 1 while you don't pass stateSets.")

            else:
                if self.start is None and self.end is None and len(raw_ss) >= 2:
                    self.start, self.end = raw_ss[0], raw_ss[-1]
                    self.Log("No set <start> <end>, Auto Set : {start <- %s, end <- %s}"%(self.start, self.end))
                elif self.start is None and self.end is not None and len(raw_ss) >= 1:
                    self.start = raw_ss[0]
                    self.Log("No set <start>, Auto Set : {start <- %s}" % self.start)
                elif self.start is not None and self.end is None and len(raw_ss) >= 1:
                    self.end = raw_ss[-1]
                    self.Log("No set <end>, Auto Set : {end <- %s}" % self.end)
                else:
                    raise Exception("\n\n[Error]: StateMachine must have a start-node and a end-node.\n\t--At least, you need pass stateSet which length >= 2.")


    def Build(self):  # 编译
        """
        编译状态机
        在启用状态机前必须至少编译一次
        状态机运行时会执行最近一次的编译结果
        :return:
        """
        def cross_chain_iter(_tf):  # 转移函数展开 迭代器
            for _srt in _tf.srt:
                for _dst in _tf.dst:
                    yield _srt, _dst, _tf,   # srt, dst, tf

        # ------------- 子函数 区域 -------------------
        raw_ss, raw_tfs = self.GetTidiedInputParams()

        # 检查start和end
        self.TidyStartAndEnd(raw_ss, raw_tfs)

        self.state_table = {}
        self.st = self.state_table  # 别名

        # 生成keys for 'state table'
        if not self.raw_ss_auto_fill_flag:
            for sta in raw_ss:
                self.st[sta] = []  # name: []

        # 考虑优先级，分配这些函数
        for bundled_tf in raw_tfs:
            tf_iter = cross_chain_iter(bundled_tf)  # 获取传递函数迭代器(解除交叉参数)
            for srt, dst, tf in tf_iter:  # 对一次TransFunc所设定的所有link 按优先级排布
                added_flag = False   # 如果在排序中没有添加此项，那么应当在末尾添加此项
                if self.raw_ss_auto_fill_flag:
                    if srt not in self.st:
                        self.st[srt] = []
                        self.Log("[Auto] Add srt<%s> to state table." % srt)
                    if dst not in self.st:
                        self.st[dst] = []
                        self.Log("[Auto] Add dst<%s> to state table." % dst)
                else:
                    if self.st.get(srt) is None:
                        raise Exception("\n\n[Error]: This <TransFunc>'s srt: <{}> doesn't exist in state sets.\n\n{}".format(srt, "srt:\n\t{},\ndst:\n\t{}".format(bundled_tf.srt, bundled_tf.dst)))
                if self.st[srt]:  # 按priority进行排序，高优先级的在前
                    for index in range(len(self.st[srt])):
                        _srt, _dst, _tf = self.st[srt][index]
                        if tf.priority <= _tf.priority: continue
                        else:
                            self.st[srt].insert(index, (srt, dst, tf))
                            added_flag = True

                if not added_flag:  # 在排序中没有添加此项，那么应当在末尾添加此项
                    self.st[srt] += [(srt, dst, tf)]



        # Build完成
        self.ready = self.READY

        self.ResetAreas()  # 重置各级运行环境


class StateMachine(StateMachine_cb, StateMachine_area, StateMachine_data):  # 状态机
    def __init__(self, *args, start=None, end=None):
        """
        用户可以只传trans_funcs这个参数，PyState会自动提取节点名
        :param arg1: 可以为state sets (记做sets tfs 正常模式)， 也可以是tfs (记做auto-sets tfs 自动补全模式)
        :param arg2: 正常模式时: tfs; 自动补全模式时: start(可省略)
        :param arg3: 正常模式时: start(可省略); 自动补全模式时: end(可省略)
        :param arg4: 正常模式时: end(可省略); 自动补全模式时: 不需要该参数，传入会产生歧义，可能会导致程序产生Exception

        当start和end通过kwargs传递时，可以忽略args中的start和end
        """
        StateMachine_data.__init__(self, *args, start=start, end=end)

        self.Loading()


    def Loading(self, *args, **kwargs):
        ...

    """
    def Build(self):  # 编译
        
    编译状态机
    在启用状态机前必须至少编译一次
    状态机运行时会执行最近一次的编译结果
    :return:
    """


    def Stop(self):
        """
        停止当前状态机，进入finish状态
        注意：停止后无法继续Execute。
            如果希望重新Execute，请在finish状态下调用Reset方法
        :return:
        """
        if self.ready < self.READY:
            raise NotImplementBuildUp()
        self.ready = self.FINISH
        if self.end_cb:
            self.end_cb(self)

    def __exec(self):
        """
        底层状态机执行函数
        :return:
        """
        ChangeGlobal_Machine(self.machine_area, self.machine_area)
        ChangeGlobal_Inst(self.machine_area, self.inst_areas[self.now])
        for i in range(len(self.st[self.now])):  # 按照优先级执行
            srt, dst, tf = self.st[self.now][i]
            ChangeGlobal_Dest(self.machine_area, self.inst_areas[dst])
            ChangeGlobal_This(self.machine_area, self.this_areas[self.now][i])
            sta = tf.Trig()

            if sta:  # 转移
                for _srt, _dst, _tf in self.st[self.now]: tf.buffer.Reset()  # 重置所有缓冲
                self.now = dst  # 状态转移
                self.log += [srt + " -> " + dst]
                if self.trans_cb:
                    self.trans_cb(self, srt, dst, tf)

                if self.now == self.end:
                    self.Log("FSM Touch End<%s>."%self.end)
                    self.Stop()
                break
        ChangeGlobalBack_NoCheck(self.machine_area)

    def Execute(self):
        """
        执行一步状态机
        :return:
        """
        if self.ready < self.READY:
            raise NotImplementBuildUp()
        elif self.ready >= self.FINISH:
            raise Exception("\n\n[Error]: you must .Reset() before restarting it.")
        if self.ready < self.BUSY:
            self.now = self.start
            self.ready = self.BUSY
            self.log = []
            if self.start_cb:
                self.start_cb(self)

        if self.ready == self.BUSY:
            self.__exec()

    def Reset(self):
        """
        重置结束标志符(finish)，以便可以重新开始执行

        :return:
        """
        if self.ready <= self.READY:
            raise NotImplementBuildUp()
        self.ready = self.READY

    def IsFinish(self):
        """
        是否执行完成
        执行到<end>节点或是用户手动调用Stop()都会进入Finish状态
        进入Finish状态后需要手动调用Reset()来重新使用该状态机
        :return:
        """
        return self.ready >= self.FINISH

    def IsBuildUp(self):
        """
        是否编译完成
        只要编译过一次，便始终为True
        :return:
        """
        return self.ready >= self.READY

    def IsRunning(self):
        """
        是否正在运行
        注意: 至少需要执行一次Execute才会进入Running状态
        :return:
        """
        return self.ready >= self.BUSY

    def GetNodeArea(self, name):
        if self.ready < self.READY:
            raise NotImplementBuildUp()
        get = self.inst_areas[name]
        if get is None:
            raise StateNotInSets(name)
        return get

    def StateGraph(self):
        if not self.ready:
            raise NotImplementBuildUp()
        try:
            from graphviz import Digraph
        except ImportError:
            raise ImportError("\n\n[Error]: Unable to import graphviz, please install them.")
        # ------------------- 子函数 --------------------
        # ------------------- 子函数 --------------------

        graph = Digraph(comment='State Table Graph', graph_attr={"labeljust":'l'})
        # build nodes first
        for k in self.st:
            if self.start == k: graph.node(k, k + "<In>", {'fontsize':'16', 'margin': '0.2'}, color='red', fontname="Microsoft YaHei")
            elif self.end == k: graph.node(k, k + "<Out>", {'fontsize':'16', 'margin': '0.2'}, color='blue', fontname="Microsoft YaHei")
            else: graph.node(k, k, {'fontsize':'20', 'margin': '0.2'}, fontname="Microsoft YaHei")
        # build links second
        for k in self.st:
            for srt, dst, tf in self.st[k]:
                # build doc
                doc = ""
                if tf.priority:
                    doc += "[{}]".format(tf.priority)
                if tf.buffer.Max():
                    doc += "<buf[%d]>: "%tf.buffer.Max() + tf.buffer.doc + '\n'
                if tf.cond_doc:
                    doc += "<if>: " + tf.cond_doc + '\n'
                if tf.exec_doc:
                    doc += "<do>: " + tf.exec_doc + '\n'
                # add link
                graph.edge(srt, dst, doc, {"labeldistance":"0.5", "decorate":"True", "labelfontsize":"20", "minlen":"4"}, fontname="Microsoft YaHei")
        return graph

    def ShowLog(self, if_show=False):
        """
        启动/停止 日志的控制台输出.
        :param if_show: 启动/停止
        :return:
        """
        self.show_log_flag = if_show

TF = TransFunc
SM = StateMachine



