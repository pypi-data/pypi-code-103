import compileall
import os
import shutil
import argparse


def substitute(path):
    for i in os.listdir(path):
        if os.path.isdir(os.path.join(path, i)):
            substitute(os.path.join(path, i))
    if os.path.exists(os.path.join(path, '__pycache__')):
        for name in os.listdir(os.path.join(path, '__pycache__')):
            file_name = name.split('.')[0] + '.py'
            if os.path.exists(os.path.join(path, file_name)):
                print(os.path.join(path, file_name))
                os.remove(os.path.join(path, file_name))  # 删除py文件，慎重
            shutil.move(os.path.join(path, '__pycache__', name), os.path.join(path, name.replace('cpython-36.', '')))
        os.removedirs(os.path.join(path, '__pycache__'))


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--path', type=str, help='path name')
    args = parser.parse_args()
    path = args.path
    compileall.compile_dir(path)
    substitute(path)
