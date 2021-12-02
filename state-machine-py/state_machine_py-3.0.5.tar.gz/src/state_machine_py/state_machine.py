class StateMachine():
    """状態遷移マシーン（State diagram machine）

    Example
    -------
    # Contextクラス、state_creator_dictディクショナリー, transition_dictディクショナリー は別途作っておいてください

    context = Context()
    sm = StateMachine(context, state_creator_dict=state_creator_dict, transition_dict=transition_dict)

    sm.arrive("[Init]") # Init状態は作っておいてください
    """

    def __init__(self, context=None, state_creator_dict={}, transition_dict={}):
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
    def verbose(self):
        """標準出力にデバッグ情報を出力するなら真"""
        return self._verbose

    @verbose.setter
    def verbose(self, val):
        self._verbose = val

    def on_line(line):
        pass

    def leave_and_loop(self, lines_getter):
        """まず state_machine.leave(...) を行い、
        そのあと arrive(...), leave(...) のペアを無限に繰り返します。
        leave(...) に渡す line 引数は、
        lines_getter() を実行することでリストで取得できるようにしてください。
        lines_getter() が None を返すとループを抜けます"""
        while True:
            lines = lines_getter()
            if not lines:
                break

            for line in lines:

                self.on_line(line)

                next_state_name, transition_key = self.leave(
                    line)
                self.arrive_sequence(next_state_name)

    def arrive_sequence(self, next_state_name):
        """arrive(next_state_name) の拡張版。
        このステートを通り過ぎる指定があったなら、次の leave(...) まで行います。
        通り過ぎる指定がなくなるまで続けます

        Parameters
        ----------
        str : next_state_name
            次の状態の名前
        """
        interrupt_line = self.arrive(next_state_name)

        # interrupt_line の指定があったら、次の leave をすぐ行います
        while interrupt_line:
            next_state_name, transition_key = self.leave(
                interrupt_line)

            interrupt_line = self.arrive(
                next_state_name)

    def arrive(self, next_state_name):
        """指定の状態に遷移します
        entryコールバック関数を呼び出します。

        Parameters
        ----------
        str : next_state_name
            次の状態の名前

        Returns
        -------
        object
            ただちに leave に渡したい引数。無ければ None
        """

        if self.verbose:
            print(f"[state_machine] Arrive to {next_state_name}")

        if next_state_name in self._state_creator_dict:
            # 次のステートへ引継ぎ
            self._state = self._state_creator_dict[next_state_name]()

            interrupt_line = self._state.entry(self._context)
            if interrupt_line and self.verbose:
                print(
                    f"[state_machine] Arrive interrupt_line={interrupt_line}")

            return interrupt_line

        else:
            # Error
            raise ValueError(f"Next state [{next_state_name}] is not found")

    def leave(self, line):
        """次の状態の名前と、遷移に使ったキーを返します。
        exitコールバック関数を呼び出します。
        stateの遷移はまだ行いません

        Parameters
        ----------
        str : line
            入力文字列（末尾に改行なし）

        Returns
        -------
        str, str
            次の状態の名前、遷移に使ったキー
        """

        if self.verbose:
            print(f"[state_machine] Leave line={line}")

        edge_name = self._state.leave(self._context, line)

        # さっき去ったステートの名前と、今辿っているエッジの名前
        key = f"{self._state.name}{edge_name}"

        if key in self._transition_dict:
            next_state_name = self._transition_dict[key]

            if self.verbose:
                print(f"[state_machine] Leave {key}{next_state_name}")

        else:
            # Error
            raise ValueError(f"Leave-key [{key}] is not found")

        self._state.exit(self._context)
        return next_state_name, key
