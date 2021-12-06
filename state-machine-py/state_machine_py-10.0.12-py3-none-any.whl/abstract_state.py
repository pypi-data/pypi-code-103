class AbstractState():
    """状態"""

    def __init__(self):
        pass

    def entry(self, req):
        """この状態に遷移したときに呼び出されます

        Parameters
        ----------
        req : Request
            ステートマシンからステートへ与えられる引数のまとまり

        Returns
        -------
        str
            ただちに state_machine._leave(...) に渡す引数です。
            None を指定すると、たたちに次の状態に遷移することはしません
        """
        self.on_entry(req)
        return None

    def on_entry(self, req):
        """この状態に遷移したときに呼び出されます

        Parameters
        ----------
        req : Request
            ステートマシンからステートへ与えられる引数のまとまり
        """
        pass

    def exit(self, req):
        """この状態から抜け出たときに呼び出されます。ただし初期化時、アボート時は呼び出されません

        Parameters
        ----------
        req : Request
            ステートマシンからステートへ与えられる引数のまとまり

        Returns
        -------
        str
            次（下位）の辺の名前
        """
        self.on_exit(req)

        return None

    def on_exit(self, req):
        """この状態から抜け出たときに呼び出されます。ただし初期化時、アボート時は呼び出されません

        Parameters
        ----------
        req : Request
            ステートマシンからステートへ与えられる引数のまとまり
        """
        pass
