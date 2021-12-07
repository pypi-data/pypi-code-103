#!/usr/bin/env python3
# coding=UTF-8

def restart() :
    print("EXAMPLE START: nbasenumber")
    for i in [
    "from nbasenumber import Base",
    "adecimal = Base(10)",
    "abinary = Base(2)",
    "aoctal = Base(8)",
    "aternary = Base(3)",
    "ahexadecimal = Base(16)",
    "aduodecimal = Base(12)",
    "print(adecimal, abinary, aoctal, aternary, ahexadecimal, aduodecimal)",
    "print(adecimal+185037)",
    "print(abinary+185037)",
    "print(aoctal+185037)",
    "print(aternary+185037)",
    "print(ahexadecimal+185037)",
    "print(aduodecimal+185037)",
    "print((adecimal+185037).format_to_str())",
    "print((abinary+185037).format_to_str())",
    "print((aoctal+185037).format_to_str())",
    "print((aternary+185037).format_to_str())",
    "print((ahexadecimal+185037).format_to_str(_10='A', _11='B', _12='C', _13='D', _14='E', _15='F'))",
    "print((aduodecimal+185037).format_to_str(_10='A', _11='B'))",
    "print(adecimal+abinary)",
    """\
class basefoo(object) :
    def __init__(self, num=0) :
        self.num = num
    def __Base__(self) :
        return Base(10) + int(self.num)""",
    "print(Base(basefoo(1073281)))",
    "print(Base(12, (11, 10, 8, 5)).to_bytes(Base(11, (10,)), 'big'))",
    "print(Base.from_bytes(b'This will be converted to a Base', 'big'))",
    "print(Base.from_bytes(b'This will be converted to a Base', 'little'))"
    ] :
        print(">>> "+"\n... ".join(i.split("\n")))
        exec("global Base\n"+i)

restart()
