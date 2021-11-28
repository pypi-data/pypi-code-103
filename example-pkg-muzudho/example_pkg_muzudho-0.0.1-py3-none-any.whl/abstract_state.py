class AbstractState():
    """状態"""

    def __init__(self):
        def on_none(context):
            """何もしません"""
            pass

        self._on_entry = on_none
        self._on_exit = on_none

    @property
    def on_entry(self):
        """この状態に遷移したときに呼び出されるコールバック関数"""
        return self._on_entry

    @on_entry.setter
    def on_entry(self, func):
        self._on_entry = func

    @property
    def on_exit(self):
        """この状態から抜け出たときに呼び出されるコールバック関数。ただし初期化時、アボート時は呼び出されません"""
        return self._on_exit

    @on_exit.setter
    def on_exit(self, func):
        self._on_exit = func
