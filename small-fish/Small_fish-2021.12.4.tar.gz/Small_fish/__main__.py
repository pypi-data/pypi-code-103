import requests
import getopt
from colorama import init, Fore

import datetime
import os
import sys

def get_url_html(_url, _headers=False):
    r=requests.get(url=_url, headers=False)
    return r.text

def get_url_json(_url, _headers=False):
    j=requests.get(url=_url, headers=_headers)
    return j.json()
def Smallfish(self):
    init(autoreset = True)
    opts,args=getopt.getopt(sys.argv[1:], '-v-h', ['version', 'HtmlText=', 'HtmlJson=', 'help'])
    dtime=datetime.datetime.now()
    print(Fore.CYAN+f"Small fish SystemTime:{self.dtime.strftime('%Y-%m-%d %H:%M:%S')} -help查看命令")
    for opt,opt_v in self.opts:
        if opt in ("-v", "--version"):
            print(Fore.BLUE+"Version:0.1")
        if opt in ("--HtmlText"):
            print(f"{opt_v}")
            print(Fore.LIGHTMAGENTA_EX+f"{get_url_html(opt_v)}")
        if opt in ("--HtmlJson"):
            print(f"{opt_v}")
            print(Fore.LIGHTRED_EX+f"{get_url_json(opt_v)}")
        if opt in ("-h", "--help"):
            print(self.opts)
            print(Fore.YELLOW+"""
-------------------------------------------------------------------
Small fish Help:
    Command List:



    
                -v    Version 版本查询
""")
if __name__ in "__main__":
    Smallfish()
