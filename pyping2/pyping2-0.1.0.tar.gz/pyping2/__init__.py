#PyPing2
#By awesomelewis2007

import requests
import time
import sys
def ping(ip):
    if "https://" in ip:
        pass
    else:
        ip = "https://"+ip
    time_start = time.time()
    request = requests.get(ip)
    time_end = time.time()
    pingtime = time_end - time_start
    code = request.status_code
    return pingtime,code
def multiping(ips):
    pingtimes = []
    codes = []
    for i in ips:
        if "https://" in i:
            pass
        else:
            i = "https://"+i
        time_start = time.time()
        request = requests.get(i)
        time_end = time.time()
        pingtime = time_end - time_start
        code = request.status_code
        pingtimes.append(pingtime)
        codes.append(code)
    return pingtimes,codes
def demo():
    print("Demo of PyPing2")
    print("Ping time of google.com:"+str(ping("www.google.com")[0]))
    print("Multiping of google.com and github.com:"+str(multiping(["www.google.com","www.github.com"])[0]))