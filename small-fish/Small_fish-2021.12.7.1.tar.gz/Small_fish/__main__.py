import socket
import requests
import getopt
from colorama import init, Fore

import datetime
import os
import sys

from .import File_encryption as ENC

def get_url_html(_url, _headers=False):
    r=requests.get(url=_url, headers=False)
    return r.text

def get_url_json(_url, _headers=False):
    j=requests.get(url=_url, headers=_headers)
    return j.json()

def get_IP(domain, _http):
    data = socket.getaddrinfo(domain, f'{_http}')
    IP=data[0][4][0]
    return IP

cwd=False
def Smallfish():
    global cwd
    init(autoreset = True)
    dtime=datetime.datetime.now()
    opts,args=getopt.getopt(sys.argv[1:], '-a-v-e:-d:-h', ['author','version', 'Enc=', 'Dec=', 'help'])
    for opt,opt_v in opts:
        """
        Version 版本查询
        """
        if opt in ("-v", "--version"):
            print(Fore.BLUE+"Version:2021.12.7.1")
            cwd=True

        """
        --ENC ENC加密文件
        """
        if opt in ("-e", "--Enc"):
            e=ENC.ENC()
            e.enc(opt_v)
            cwd=True

        """
        --DEC 解密文件
        """
        if opt in ("-d", "--Dnc"):
            d=ENC.ENC()
            d.dec(opt_v)
            cwd=True

        """author"""
        if opt in ("-a", "--author"):
            print(Fore.GREEN+"author(作者)：\nPYmili Eail邮件：2097632843@qq.com")
            cwd=True
        """--help"""
        if opt in ("-h", "--help"):
            print(Fore.YELLOW+"""
-------------------------------------------------------------------
Small fish Help:
    Command List:
    
            -v 或者 --version              Version 版本查询
            -e 或者 --Enc                  使用ENC加密文件方法加密文件 格式: -e [要加密文件]
            -d 或者 --Dec                  解密ENC加密后的文件 格式: -d [要解密的文件]
            
""")
            cwd=True

    """没有参数时"""
    if cwd == False:
        print(Fore.CYAN+f"Small fish SystemTime:{dtime.strftime('%Y-%m-%d %H:%M:%S')} -h查看命令")
if __name__ in "__main__":
    Smallfish()
