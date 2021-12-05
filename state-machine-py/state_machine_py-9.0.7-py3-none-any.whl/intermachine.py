class Intermachine():
    """マシーン間で値を受け渡しするのに使います

    誰に投げるかは指定できますが、誰から投げられたかは指定できません
    """

    def __init__(self, owner_maltiple_state_machine, machine_key):
        self._owner = owner_maltiple_state_machine
        self._machine_key = machine_key

    def put(self, destination_machine_key, item, block=True, timeout=None):
        self._owner.input_queues[destination_machine_key].put(item=item,
                                                              block=block,
                                                              timeout=timeout)

    def get(self, block=True, timeout=None):
        return self._owner.input_queues[self._machine_key].get(block=block,
                                                               timeout=timeout)

    def join(self):
        return self._owner.input_queues[self._machine_key].join()

    def task_done(self):
        return self._owner.input_queues[self._machine_key].task_done()
