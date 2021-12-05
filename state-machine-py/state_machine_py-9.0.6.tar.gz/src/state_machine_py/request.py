class Request():
    """ステートマシンからステートへ与えられる引数のまとまり"""

    def __init__(self, context, edge_path=[], line=None, intermachine=None):
        self._context = context
        self._edge_path = edge_path
        self._line = line
        self._intermachine = intermachine

    @property
    def context(self):
        """このステートマシンは、このContextが何なのか知りません。
        外部から任意に与えることができる変数です。 Defaults to None."""
        return self._context

    @property
    def edge_path(self):
        """辺パス
        Examples
        --------
        list
            ["this","is","a","edge","path"]
        """
        return self._edge_path

    @property
    def line(self):
        """外部から与えられる入力文字列

        Examples
        --------
        コマンドライン文字列"""
        return self._line

    @property
    def intermachine(self):
        """ステートマシン間の通信手段"""
        return self._intermachine
