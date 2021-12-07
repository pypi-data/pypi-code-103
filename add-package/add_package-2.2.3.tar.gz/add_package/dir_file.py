import os


def dir_file():
    _path = os.path.dirname(os.path.dirname(__file__))
    real_path = os.path.realpath(__file__)
    abspath = os.path.abspath(__file__)
    cwd = os.getcwd()
    print('_path:', _path)
    print('real_path:', real_path)
    print('real_dir', os.path.dirname(real_path))
    print('abspath:', abspath)
    print('cwd:', cwd)
    dest = os.path.join(abspath, 'file_test').replace('\\', '/')
    print(dest)
    os.mkdir(dest)


dir_file()
