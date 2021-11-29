#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @CreateDate   : 21/11/29 15:53
# @Author       : DBArtist
# @Email        : 1595628527@qq.com
# @ScriptFile   : osinfo.py
# @Project      : PyMonitor
# @Describe     :




"""
采集机器自身信息
1 主机名
2 内存
3 ip与mac地址
4 cpu信息
5 硬盘分区信息
6 制造商信息
7 出厂日期
8 系统版本
"""
import socket

help_text="""
          help text 
          help text 
          help text 
          """

def help():
    """打印帮助文档"""
    print(help_text)


def get_hostname():
    """获取主机名"""
    return socket.gethostname()


# @click.command()
# @click.option("--host", "-h", type = str, prompt=True, help="Name of host.")
def main():
    print(get_hostname())

if __name__ == "__main__":
    main()
