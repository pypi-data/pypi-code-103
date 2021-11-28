class StateMachine():
    """状態遷移マシーン（State diagram machine）

    Example
    -------
    # Contextクラス、behavior_creator_dictディクショナリー, transition_dictディクショナリー は別途作っておいてください

    context = Context()
    sm = StateMachine(context, behavior_creator_dict=behavior_creator_dict, transition_dict=transition_dict)

    sm.arrive("[Init]") # Init状態は作っておいてください
    """

    def __init__(self, context=None, behavior_creator_dict={}, transition_dict={}):
        """初期化

        Parameters
        ----------
        context : Context
            このステートマシンは、このContextが何なのか知りません。
            外部から任意に与えることができる変数です。 Defaults to None.
        behavior_creator_dict : dict
            状態を作成する関数のディクショナリーです。 Defaults to {}.
        transition_dict : dict
            遷移先の状態がまとめられたディクショナリーです。 Defaults to {}.
        """
        self._context = context
        self._behavior_creator_dict = behavior_creator_dict
        self._transition_dict = transition_dict

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

    def leave(self, line):
        """次の状態の名前と、遷移に使ったキーを返します。
        on_exitコールバック関数を呼び出します。
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

        edge_name = self._state.leave(self._context, line)

        # さっき去ったステートの名前と、今辿っているエッジの名前
        key = f"{self._state.name}{edge_name}"

        if key in self._transition_dict:
            next_state_name = self._transition_dict[key]
        else:
            # Error
            raise ValueError(f"Leave-key [{key}] is not found")

        self._state.on_exit(self._context)
        return next_state_name, key

    def arrive(self, next_state_name):
        """指定の状態に遷移します
        on_entryコールバック関数を呼び出します。

        Parameters
        ----------
        str : next_state_name
            次の状態の名前
        """

        if next_state_name in self._behavior_creator_dict:
            # 次のステートへ引継ぎ
            self._state = self._behavior_creator_dict[next_state_name]()

            self._state.on_entry(self._context)

        else:
            # Error
            raise ValueError(f"Next state [{next_state_name}] is not found")
