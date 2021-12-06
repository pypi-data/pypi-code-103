import os
import sys
import logging
from pathlib import Path
import time
from pypinyin import pinyin, lazy_pinyin, Style
import argparse
import random

CHARACTERS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

__VERSION__ = '0.1.3'

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

TIME = lambda: int(time.time() * 1000)

file_extensions = '.DS_Store', '.ini'


def get_parser():
    parser = argparse.ArgumentParser(
        description='批量修改文件md5',
    )

    parser.add_argument(
        'path',
        metavar='PATH',
        type=str,
        help='文件或者文件夹路径',
    )

    parser.add_argument(
        '-tp', '--topinyin', action='store_true',
        help='是否将文件名转为拼音'
    )
    parser.add_argument(
        '-rv', '--reverse', action='store_true',
        help='是否将文件名反转'
    )
    parser.add_argument('-v', '--version',
                        action='version', version=__VERSION__, help='显示当前版本号')

    return parser


def checkIsNotIncludeFile(file):
    for extension in file_extensions:
        if extension in file:
            return False
    else:
        return True


def fileAppend(filename):
    random_str = ''.join(random.choice(CHARACTERS))
    temp = open(filename, 'a')

    temp.write(random_str)

    temp.close()
    print(filename + " ---> 处理完成")


def reversed_string(a_string):
    return a_string[::-1]


def changeMd5(path, topinyin, reverse):
    if Path(path).exists():

        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):

                for file in files:
                    filename = os.path.join(root, file)
                    fileAppend(filename)
                    if checkIsNotIncludeFile(file) and topinyin:
                        os.renames(filename, "".join(lazy_pinyin(filename)))
                        print('新文件：' + "".join(lazy_pinyin(filename)))
                    if checkIsNotIncludeFile(file) and reverse:
                        (base_path, realfilename) = os.path.split(filename)
                        (file, ext) = os.path.splitext(filename)
                        os.renames(filename, os.path.join( base_path,(reversed_string(realfilename.replace(ext, "")))+ext))
                        print('新文件反转文件名：' +os.path.join( base_path,(reversed_string(realfilename.replace(ext, "")))+ext))
                else:
                    for directory in dirs:
                        changeMd5(root + "/" + directory, topinyin,reverse)
        else:
            fileAppend(path)
            if checkIsNotIncludeFile(path) and topinyin:
                os.renames(path, "".join(lazy_pinyin(path)))
                print('新文件转拼音：' + "".join(lazy_pinyin(path)))
            if checkIsNotIncludeFile(path) and reverse:
                (base_path, filename) = os.path.split(path)
                (file, ext) = os.path.splitext(path)
                os.renames(path, os.path.join(base_path,reversed_string(filename.replace(ext, ""))+ext))
                print('新文件反转文件名：' + os.path.join(base_path,reversed_string(filename.replace(ext, ""))+ext))

    else:
        if path is not None:
            logging.error('路径不存在:' + path)
        else:
            logging.error('请出入路径:')


def cli():
    args = vars(get_parser().parse_args())
    path = os.path.abspath(args.get('path', None))
    topinyin = args.get('topinyin', False)
    reverse = args.get('reverse', False)
    begin = TIME()
    changeMd5(path, topinyin, reverse)
    print("用时：" + str(TIME() - begin) + '毫秒')


if __name__ == '__main__':
    cli()
