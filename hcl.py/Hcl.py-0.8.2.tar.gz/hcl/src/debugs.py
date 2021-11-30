import json
from inspect import getframeinfo, stack
import os
from hcl import settings

enabled = False

if settings.debugMode == True:
    enabled = True

class DebugMode:
    def colored(self, r, g, b, text, rb : int = None, gb : int = None, bb : int = None):
    # print(colored(200, 20, 200, 0, 0, 0, "Hello World"))
        if rb is None and gb is None and bb is None:
            return "\033[38;2;{};{};{}m{}\033[0m".format(r, g, b, text)
        else:
            return "\033[38;2;{};{};{}m\033[48;2;{};{};{}m{}\033[0m".format(r, g, b, rb, gb, bb, text)

    def __init__(self, data : str, type = str):
        self.caller = getframeinfo(stack()[2][0])
        self.data = data
        self.callercontext = (self.caller.code_context[0]).replace('\n', '')

        if type == "Success":
            print("\n" + self.colored(0, 0, 0, rb=0, gb=199, bb=83, text=f" ❮ SUCCESS ❯ ") + self.colored(166, 249, 163, rb=36, gb=36, bb=36, text=f" {self.caller.filename}, Line = {self.caller.lineno}"))
            print(self.colored(0, 0, 0, rb=0, gb=199, bb=83, text=" FUNCTION     ❯ ") + self.colored(0, 199, 83, f" {self.callercontext}"))
            try:
                self.statuscode =  json.loads(data)["api:statuscode"]
                print(self.colored(0, 0, 0, rb=0, gb=199, bb=83, text=" API CODE     ❯ ") + self.colored(0, 199, 83, f" {self.statuscode}"))
            except:
                pass
            print(self.colored(166, 249, 163, rb=36, gb=36, bb=36, text=f" {self.data}") + "\n")

        if type == "Info":
            print("\n" + self.colored(0, 0, 0, rb=0, gb=135, bb=244, text=f" ❮ INFO ❯ ") + self.colored(163, 206, 249, rb=36, gb=36, bb=36, text=f" {self.caller.filename}, Line = {self.caller.lineno}"))
            print(self.colored(0, 0, 0, rb=0, gb=135, bb=244, text=" FUNCTION     ❯ ") + self.colored(0, 135, 244, f" {self.callercontext}"))
            try:
                self.statuscode =  json.loads(data)["api:statuscode"]
                print(self.colored(0, 0, 0, rb=0, gb=135, bb=244, text=" API CODE     ❯ ") + self.colored(0, 135, 244, f" {self.statuscode}"))
            except:
                pass
            print(self.colored(163, 206, 249, rb=36, gb=36, bb=36, text=f" {self.data}") + "\n")

        if type == "Warning":
            print("\n" + self.colored(0, 0, 0, rb=255, gb=185, bb=52, text=f" ❮ WARNING ❯ ") + self.colored(249, 229, 163, rb=36, gb=36, bb=36, text=f" {self.caller.filename}, Line = {self.caller.lineno}"))
            print(self.colored(0, 0, 0, rb=255, gb=185, bb=52, text=" FUNCTION     ❯ ") + self.colored(255, 185, 52, f" {self.callercontext}"))
            try:
                self.statuscode =  json.loads(data)["api:statuscode"]
                print(self.colored(0, 0, 0, rb=255, gb=185, bb=52, text=" API CODE     ❯ ") + self.colored(255, 185, 52, f" {self.statuscode}"))
            except:
                pass
            print(self.colored(249, 229, 163, rb=36, gb=36, bb=36, text=f" {self.data}") + "\n")
