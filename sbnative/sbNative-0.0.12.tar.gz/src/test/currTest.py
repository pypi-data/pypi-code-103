
from pathlib import Path
import sys
from functools import lru_cache

sys.path.append(
    r"D:\AA_CODING\python\Projects\codebases\sbNative\src\sbNative")

import runtimetools

# import debugtools

# tmr = debugtools.timePlotter(debugtools.tPlotArgs.TIME, trackArgs=[0])

# @tmr.timer
# def startfib(n):
#     fib(n)

# # @lru_cache(maxsize=100)
# def fib(n):
#    if n <= 1:
#        return n
#    else:
#        return fib(n-1) + fib(n-2)

# for i in range(14,26):
#     startfib(i)

# tmr.show()


# d = runtimetools.bidirectionalDict(
#     Richard = ["Dick", "Rick"],
#     Annamarie = ["Marie", "Anna", "Ann"]
# )

# print(d.Richard, d["Richard"])
# print(d.Rick, d["Rick"])
# print(d.Dick, d["Dick"])

# print(d.Annamarie, d["Annamarie"])
# print(d.Marie, d["Marie"])
# print(d.Anna, d["Anna"])
# print(d.Ann, d["Ann"])

myIter = [
            ["be", "was", "were", "been"],
            ["stay", "stood", "have stood"]
        ]

print(runtimetools.LanguageFormatter.enumerateCollection(myIter, recursive=True))