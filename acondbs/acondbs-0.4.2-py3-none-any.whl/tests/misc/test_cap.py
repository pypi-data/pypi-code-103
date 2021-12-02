import time
from acondbs.misc.cap import cap_exec_rate
from acondbs.misc.cap import State

import pytest
import unittest.mock as mock

##__________________________________________________________________||
class Task:
    def __init__(self):
        self.counter = 0

    def __call__(self):
        self.counter += 1

def test_init():
    task = Task()
    cap = cap_exec_rate(func=task, pause_time=0.1)
    assert cap.func is task
    assert 0.1 == cap.pause_time
    assert not cap.daemon
    cap.end()
    assert 0 == task.counter

def test_daemon():
    task = Task()
    cap = cap_exec_rate(func=task, pause_time=0.1, daemon=True)
    assert cap.daemon
    # end() doesn't need to be called
    assert 0 == task.counter

def test_call():
    task = Task()
    cap = cap_exec_rate(func=task, pause_time=0.1)
    cap()
    time.sleep(0.05)
    assert 1 == task.counter
    cap.end()

def test_call_2():
    task = Task()
    cap = cap_exec_rate(func=task, pause_time=0.05)
    cap()
    time.sleep(0.2)
    cap()
    time.sleep(0.05)
    assert 2 == task.counter
    cap.end()

def test_call_3():
    task = Task()
    cap = cap_exec_rate(func=task, pause_time=0.1)
    cap() # executed immediately
    cap() # not executed
    cap() # not executed
    cap() # not executed
    cap() # executed after the pause
    time.sleep(0.05)
    assert 1 == task.counter
    time.sleep(0.1)
    assert 2 == task.counter
    cap.end()

def test_call_4():
    task = Task()
    cap = cap_exec_rate(func=task, pause_time=10)
    cap() # executed immediately
    cap() # not executed
    cap() # not executed
    cap() # not executed
    cap() # executed at the end
    time.sleep(0.05)
    assert 1 == task.counter
    cap.end()
    assert 2 == task.counter

##__________________________________________________________________||
def test_state_raise():
    config = mock.Mock()
    config.queue.get().return_value = 'unknown message'
    state = State(config)
    with pytest.raises(ValueError):
        state()

##__________________________________________________________________||
