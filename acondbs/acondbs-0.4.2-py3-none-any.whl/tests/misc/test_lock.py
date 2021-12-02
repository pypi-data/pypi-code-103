from pathlib import Path


import pytest
import unittest.mock as mock

from acondbs.misc.lock import lock
from acondbs.misc.lock import TimeOutAcquiringLock

##__________________________________________________________________||
def test_acquire_release(tmpdir_factory):
    folder = Path(tmpdir_factory.mktemp('lock'))
    lock_file = folder.joinpath('.lock')

    l = lock(lock_file)
    assert not l.locked
    l.acquire()
    assert l.locked
    assert lock_file.exists()
    l.release()
    assert not l.locked
    assert not lock_file.exists()

##__________________________________________________________________||
def test_release_when_not_lockded(tmpdir_factory):
    folder = Path(tmpdir_factory.mktemp('lock'))
    lock_file = folder.joinpath('.lock')

    l = lock(lock_file)
    assert not l.locked
    l.release()
    assert not l.locked
    assert not lock_file.exists()

##__________________________________________________________________||
def test_release_not_delete_when_not_lockded(tmpdir_factory):
    folder = Path(tmpdir_factory.mktemp('lock'))
    lock_file = folder.joinpath('.lock')

    lock_file.touch()

    l = lock(lock_file)
    assert not l.locked
    l.release()
    assert not l.locked
    assert lock_file.exists()

##__________________________________________________________________||
def test_acquire_timeout(tmpdir_factory):
    timeout = 0.1 # sec

    folder = Path(tmpdir_factory.mktemp('lock'))
    lock_file = folder.joinpath('.lock')

    lock_file.touch()

    l = lock(lock_file, timeout=timeout)

    with pytest.raises(TimeOutAcquiringLock):
        l.acquire()

##__________________________________________________________________||
def test_with_success(tmpdir_factory):
    folder = Path(tmpdir_factory.mktemp('lock'))
    lock_file = folder.joinpath('.lock')

    with lock(lock_file) as l:
        assert l.locked
        assert lock_file.exists()
    assert not l.locked
    assert not lock_file.exists()

##__________________________________________________________________||
