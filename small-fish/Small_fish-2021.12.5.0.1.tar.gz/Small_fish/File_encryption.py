import os
import re

class ENC:
    def __init__(self):
        self.cd={
            "a":"0a",
            "b":"0b",
            "c":"0c",
            "d":"0d",
            "e":"0e",
            "f":"0f",
            "g":"0g",
            "h":"0h",
            "i":"0i",
            "y":"0y",
            "j":"0j",
            "k":"0k",
            "l":"0l",
            "m":"0m",
            "n":"0n",
            "o":"0o",
            "p":"0p",
            "q":"0q",
            "r":"0r",
            "s":"0s",
            "t":"0t",
            "u":"0u",
            "v":"0v",
            "w":"0w",
            "x":"0w",
            "y":"0y",
            "z":"0z",
            "none":"/none",
            }
    def enc(self, filepath):
        self.path=filepath
        File_Msg=[]
        count = -1
        for count, lirn in enumerate(open(f'{self.path}', 'r', encoding='utf-8')):
            pass
        count += 1
        line = count
        with open(f"{self.path}", 'r', encoding="utf-8") as p:
            for rea in range(int(line)):
                rea=p.readline()
                File_Msg.append(rea)
        enc=[]
        with open(f"enc.ENC", 'w+', encoding="utf-8") as index:
            for Msg in File_Msg:
                for m in Msg:
                    if m == "a":
                        enc.append(self.cd["a"]+";")
                    elif m == "b":
                        enc.append(self.cd["b"]+";")
                    elif m == "c":
                        enc.append(self.cd["c"]+";")
                    elif m == "d":
                        enc.append(self.cd["d"]+";")
                    elif m == "e":
                        enc.append(self.cd["e"]+";")
                    elif m == "f":
                        enc.append(self.cd["f"]+";")
                    elif m == "g":
                        enc.append(self.cd["g"]+";")
                    elif m == "h":
                        enc.append(self.cd["h"]+";")
                    elif m == "i":
                        enc.append(self.cd["i"]+";")
                    elif m == "y":
                        enc.append(self.cd["y"]+";")
                    elif m == "j":
                        enc.append(self.cd["j"]+";")
                    elif m == "k":
                        enc.append(self.cd["k"]+";")
                    elif m == "l":
                        enc.append(self.cd["l"]+";")
                    elif m == "m":
                        enc.append(self.cd["m"]+";")
                    elif m == "n":
                        enc.append(self.cd["n"]+";")
                    elif m == "o":
                        enc.append(self.cd["o"]+";")
                    elif m == "p":
                        enc.append(self.cd["p"]+";")
                    elif m == "q":
                        enc.append(self.cd["q"]+";")
                    elif m == "r":
                        enc.append(self.cd["r"]+";")
                    elif m == "s":
                        enc.append(self.cd["s"]+";")
                    elif m == "t":
                        enc.append(self.cd["t"]+";")
                    elif m == "u":
                        enc.append(self.cd["u"]+";")
                    elif m == "v":
                        enc.append(self.cd["v"]+";")
                    elif m == "w":
                        enc.append(self.cd["w"]+";")
                    elif m == "x":
                        enc.append(self.cd["x"]+";")
                    elif m == "y":
                        enc.append(self.cd["y"]+";")
                    elif m == "z":
                        enc.append(self.cd["z"]+";")
                    elif m == " ":
                        enc.append(self.cd["none"]+";")
                    elif m not in ('a','b','c','d','e','f','g','h','i','y','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'):
                        enc.append(m+";")
            for en in enc:
                print(en)
                index.write(en)
    def dec(self, file):
        
        File_Msg=[]
        count = -1
        for count, lirn in enumerate(open(rf'{file}', 'r', encoding='utf-8')):
            pass
        count += 1
        line = count
        with open(f"{file}", 'r', encoding="utf-8") as dex:
            File_Msg=dex.read()
        dec=[]
        open(f"dec.txt", 'w', encoding='utf-8')
        with open(f"dec.txt", 'a+', encoding='utf-8') as dexc:
            print(File_Msg)
            for m in File_Msg.split(';'):
                if m == self.cd["a"]:
                    dec.append("a")
                elif m == self.cd["b"]:
                    dec.append("b")
                elif m == self.cd["c"]:
                    dec.append("c")
                elif m == self.cd["d"]:
                    dec.append("d")
                elif m == self.cd["e"]:
                    dec.append("e")
                elif m == self.cd["f"]:
                    dec.append("f")
                elif m == self.cd["g"]:
                    dec.append("g")
                elif m == self.cd["h"]:
                    dec.append("h")
                elif m == self.cd["i"]:
                    dec.append("i")
                elif m == self.cd["y"]:
                    dec.append("y")
                elif m == self.cd["j"]:
                    dec.append("j")
                elif m == self.cd["k"]:
                    dec.append("k")
                elif m == self.cd["l"]:
                    dec.append("l")
                elif m == self.cd["m"]:
                    dec.append("m")
                elif m == self.cd["n"]:
                    dec.append("n")
                elif m == self.cd["o"]:
                    dec.append("o")
                elif m == self.cd["p"]:
                    dec.append("p")
                elif m == self.cd["q"]:
                    dec.append("q")
                elif m == self.cd["r"]:
                    dec.append("r")
                elif m == self.cd["s"]:
                    dec.append("s")
                elif m == self.cd["t"]:
                    dec.append("t")
                elif m == self.cd["u"]:
                    dec.append("u")
                elif m == self.cd["v"]:
                    dec.append("v")
                elif m == self.cd["w"]:
                    dec.append("w")
                elif m == self.cd["x"]:
                    dec.append("x")
                elif m == self.cd["y"]:
                    dec.append("y")
                elif m == self.cd["z"]:
                    dec.append("z")
                elif m == self.cd["none"]:
                    dec.append(" ")
                elif m not in ("0a","0b","0c","0d","0e","0f","0g","0h","0i","0y","0j","0k","0l","0m","0n","0o","0p","0q","0r","0s","0t","0u","0v","0w","0w","0y","0z","/none"):
                    dec.append(m)
            for de in dec:
                dexc.write(de)
