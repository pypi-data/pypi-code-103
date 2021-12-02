import os


def dir_file():
    _path = os.path.dirname(os.path.dirname(__file__))
    print(_path)
    dest = os.path.join(_path, 'file_test').replace('\\', '/')
    print(dest)
    os.mkdir(dest)