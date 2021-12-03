#!/usr/bin/env python
# -*-coding:utf-8-*-


def bigfile_read(filename, process_line=None, line_start=0, line_count=10000,
                 mode='r', encoding='utf8'):
    """
    filename 要处理的文件名
    process_line 每一行的处理函数 默认打印动作 默认传入第一个参数 当前行数 第二个参数 具体行内容
    line_start 从哪一行开始处理 默认0
    line_count 总计要处理多少行
    mode 文件打开模式 默认 'r'
    encoding 文件打开编码 默认 'utf8'

    :return:
    """
    if process_line is None:
        process_line = lambda x, y: print(f'{x}: {y}')

    with open(filename, mode=mode, encoding=encoding) as f:
        inblock = False
        count = 0
        for index, line in enumerate(f):
            if index == line_start:
                inblock = True

            if inblock:
                process_line(index, line)
                count += 1

            if count >= line_count:
                break
