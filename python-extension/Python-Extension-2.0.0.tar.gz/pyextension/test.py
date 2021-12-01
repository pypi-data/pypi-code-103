# -*- coding: utf-8 -*-

try:
    from mathematics import *
    from password import *
    from unicode import *
    from word_bank import *
    import __init__ as pyex
except (ImportError, ModuleNotFoundError) as msg:
    from pyextension.mathematics import *
    from pyextension.password import *
    from pyextension.unicode import *
    from pyextension.word_bank import *
    import pyextension as pyex
import os

def _clear():
    try:
        for root, dirs, files in os.walk('__pycache__', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('__pycache__')
    except OSError:
        pass
    try:
        for root, dirs, files in os.walk('word_bank/__pycache__', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('word_bank/__pycache__')
    except OSError:
        pass
    try:
        os.remove('word bank.dat')
    except OSError:
        pass
    return True

def _test_pyextension():
    pyex.computer
    pyex.computer()
    pyex.python
    pyex.python()
    pyex.opensource('pyextension')
    pyex.opensource('mathematics')
    pyex.opensource('password')
    pyex.opensource('unicode')
    pyex.opensource('word bank')
    pyex.opensource('word bank data')
    pyex.message()
    pyex.description()
    pyex.GNU_General_Public_License()
    pyex.GPL()
    pyex.license()
    pyex.word_bank()
    _clear()
    return True

def _test_math():
    return _test_mathematics()

def _test_mathematics():
    floatdd(1.23)
    fibo(5)
    fibo(found=5)
    fibo(to=5)
    arithmetic_sequence('all', '12345')
    _clear()
    return True

def _test_password():
    string = '''
_test_password :

testing undo
testing set
testing reset
testing reverse
testing caesar
testing vigenere
testing get
'''
    __test__ = Encrypt('abc')
    __test__.set('abcdefghijklmnopqrstuvwxyz')
    __test__.reset()
    __test__.undo()
    __test__.get()
    a = Encrypt(string)
    a.reverse()
    a.caesar(3)
    a.vigenere_cipher('sky')
    string1 = a.get()
    b = Decrypt(string1)
    b.vigenere_cipher('sky')
    b.caesar(3)
    b.reverse()
    string2 = b.get()
    _clear()
    if string2 != string:
        return False
    else:
        return True

def _test_unicode():
    search(1)
    search('a')
    table(64, 8)
    table(64, 8, True)
    listcode(64)
    listcode(64, True)
    return True

def _test_wordbank():
    import time
    location = '_test_wordbank--' + str(time.time()) + '.dat'
    install(location, get())
    a = Word(location)
    a.search('a')
    a.get()
    uninstall(location)
    _clear()
    return True

def _test(module='all'):
    if module == 'all':
        return (
            _test_pyextension(),
            _test_mathematics(),
            _test_password(),
            _test_unicode(),
            _test_wordbank()
            )
    elif module == 'pyextension':
        return _test_pyextension()
    elif module == 'mathematics' or module == 'math':
        return _test_mathematics()
    elif module == 'password':
        return _test_password()
    elif module == 'unicode':
        return _test_unicode()
    elif module == 'word bank' or module == 'word_bank':
        return _test_wordbank()
