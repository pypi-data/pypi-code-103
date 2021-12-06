from state_machine_py.request import Request


class StateMachine():
    """状態遷移マシーン（State diagram machine）

    Example
    -------
    # Contextクラス、state_creator_dictディクショナリー, transition_dictディクショナリー は別途作っておいてください

    context = Context()
    sm = StateMachine(context, state_creator_dict=state_creator_dict, transition_dict=transition_dict)

    sm._arrive("[Init]") # Init状態は作っておいてください
    """

    def __init__(self, context=None, state_creator_dict={}, transition_dict={}, intermachine=None, name=None):
        """初期化

        Parameters
        ----------
        context : Context
            このステートマシンは、このContextが何なのか知りません。
            外部から任意に与えることができる変数です。 Defaults to None.
        state_creator_dict : dict
            状態を作成する関数のディクショナリーです。 Defaults to {}.
        transition_dict : dict
            遷移先の状態がまとめられたディクショナリーです。 Defaults to {}.
        """
        self._context = context
        self._state_creator_dict = state_creator_dict
        self._transition_dict = transition_dict
        self._verbose = False
        self._edge_path = []
        self._lines_getter = None  # 標準入力とか１個しかないけど
        self._state = None
        self._is_terminate = False  # 永遠に停止
        self._intermachine = intermachine
        self._name = name

    @property
    def context(self):
        """このステートマシンは、このContextが何なのか知りません。
        外部から任意に与えることができる変数です"""
        return self._context

    @context.setter
    def context(self, val):
        self._context = val

    @property
    def state(self):
        """現在の状態"""
        return self._state

    @property
    def edge_path(self):
        """現在の辺"""
        return self._edge_path

    @property
    def lines_getter(self):
        """このステートマシンは、このContextが何なのか知りません。
        外部から任意に与えることができる変数です"""
        return self._lines_getter

    @lines_getter.setter
    def lines_getter(self, val):
        self._lines_getter = val

    @property
    def verbose(self):
        """標準出力にデバッグ情報を出力するなら真"""
        return self._verbose

    @verbose.setter
    def verbose(self, val):
        self._verbose = val

    @property
    def is_terminate(self):
        """永遠に停止"""
        return self._is_terminate

    @is_terminate.setter
    def is_terminate(self, val):
        self._is_terminate = val

    @property
    def name(self):
        """他のステートマシンと区別するためのキーとして使われます"""
        return self._name

    def start(self, next_state_name):
        """まず state_machine._arrive(...) を行い、
        そのあと _leave(...), _arrive(...) のペアを無限に繰り返します。
        _leave(...) に渡す line 引数は _arrive(...) から返しますが、
        代わりに None を返すと self.lines_getter() が実行されます。
        self.lines_getter() は、 line のリストを返す関数です。
        self.lines_getter() が None を返すとループを抜けます
        """
        if self._is_terminate:
            return

        # Arrive と Leave はペアになります
        # Leave が終わったところで IsTerminate を判定します

        # Arrive sequence
        interrupt_line = self._arrive(next_state_name)

        while interrupt_line:
            next_state_name = self._leave(interrupt_line)
            if self._is_terminate:
                return

            interrupt_line = self._arrive(next_state_name)
        #

        # Leave and loop
        if self._is_terminate:
            return

        while True:
            lines = self.lines_getter()
            if lines is None:
                break

            for line in lines:

                self.on_line(line)

                next_state_name = self._leave(line)
                if self._is_terminate:
                    return

                # Arrive sequence

                interrupt_line = self._arrive(next_state_name)

                while interrupt_line:
                    next_state_name = self._leave(interrupt_line)
                    if self._is_terminate:
                        return

                    interrupt_line = self._arrive(next_state_name)
                #
        #

    def _alternate_state_machine_name(self):
        if self.name is None:
            return "[[state_machine]]"
        else:
            return self.name

    def _arrive(self, next_state_name):
        """指定の状態に遷移します
        entryコールバック関数を呼び出します。

        Parameters
        ----------
        str : next_state_name
            次の状態の名前

        Returns
        -------
        object
            ただちに _leave に渡したい引数。無ければ None
        """

        if self._is_terminate:
            return

        if self.verbose:
            edge_path = '.'.join(self._edge_path)
            print(
                f"{self._alternate_state_machine_name()} Arrive to {next_state_name} {edge_path}")

        if next_state_name in self._state_creator_dict:
            # 次のステートへ引継ぎ
            self._state = self._state_creator_dict[next_state_name]()

            req = Request(context=self._context,
                          edge_path=self._edge_path,
                          line=None,
                          intermachine=self._intermachine)
            interrupt_line = self._state.entry(req)
            if interrupt_line and self.verbose:
                print(
                    f"{self._alternate_state_machine_name()} Arrive interrupt_line={interrupt_line}")

            return interrupt_line

        else:
            # Error
            raise ValueError(f"Next state [{next_state_name}] is not found")

    def _leave(self, line):
        """次の状態の名前と、遷移に使ったキーを返します。
        exitコールバック関数を呼び出します。
        stateの遷移はまだ行いません

        Parameters
        ----------
        str : line
            入力文字列（末尾に改行なし）

        Returns
        -------
        str
            次の状態の名前
        """
        if self._is_terminate:
            return

        if self.verbose:
            print(
                f"{self._alternate_state_machine_name()} Leave line={line}")

        req = Request(
            context=self._context,
            edge_path=self.edge_path,
            line=line,
            intermachine=self._intermachine)
        next_edge_name = self._state.exit(req)

        # 例えば [Apple]ステート に居るとき ----Banana----> エッジに去るということは、
        #
        # "[Apple]": {
        #     "----Banana---->" : "[Zebra]"
        # }
        #
        # "[Apple]": {
        #     "----Banana---->" : {
        #         "----Cherry---->" : "[Zebra]"
        #     }
        # }
        #
        # "[Apple]": {
        #     "----Banana---->" : None
        # }
        #
        # といった方法で値を取ってきます。
        # 値は "[Zebra]"文字列かも知れませんし、 "----Cherry---->"ディクショナリーかもしれませんし、
        # None かもしれません。

        # まずはカレントステートを指定してディクショナリーを取ってきましょう
        if self.state.name in self._transition_dict:
            curr_dict = self._transition_dict[self.state.name]
            if curr_dict is None:
                self._is_terminate = True
                self.on_terminate(req)
                return
        else:
            raise ValueError(
                f"Current state is not found. name=[{self.state.name}]")

        # カレントエッジを下りていきましょう
        for i, edge in enumerate(self._edge_path):
            if edge in curr_dict:
                curr_dict = curr_dict[edge]
                if curr_dict is None:
                    self._is_terminate = True
                    self.on_terminate(req)
                    return
            else:
                raise ValueError(
                    f"Edge[{i}] is not found. name=[{edge}] path=[{self._edge_path}]")

        # 最後に、次のエッジへ下りていきましょう
        if next_edge_name == '':
            # （Noneではなく）空文字を指定したら、踏みとどまります
            next_state_name = self.state.name  # まだ現在のステートです

        elif next_edge_name in curr_dict:
            # ディクショナリーか、文字列のどちらかです
            obj = curr_dict[next_edge_name]

            if type(obj) is str:
                # State
                next_state_name = obj
                self._edge_path = []  # 辺パスをクリアーします
            else:
                # Edge
                next_state_name = self.state.name  # まだ現在のステートです
                self._edge_path.append(next_edge_name)  # 辺パスを伸ばします
        else:
            raise ValueError(
                f"Next edge is not found. name=[{next_edge_name}] current state=[{self.state.name}] path=[{self._edge_path}]")

        return next_state_name

    def on_line(self, line):
        pass

    def on_terminate(self, req):
        """永遠に停止

        Parameters
        ----------
        req : Request
            ステートマシンからステートへ与えられる引数のまとまり
        """
        pass
