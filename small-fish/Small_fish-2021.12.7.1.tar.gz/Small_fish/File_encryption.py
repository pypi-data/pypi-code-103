import os
import re

def get_dict_key(dic, value):
        keys = list(dic.keys())
        values = list(dic.values())
        idx = values.index(value)
        key = keys[idx]
        return key

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
            "x":"0x",
            "y":"0y",
            "z":"0z",
            "none":"/none",
            "A":"/-\\",
            "B":"|))",
            "C":"(c",
            "D":"|)",
            "E":"|~-_",
            "F":"|~-",
            "G":"(-|",
            "H":"|-|",
            "I":"~|_",
            "J":"-|_!",
            "K":"|/\\",
            "L":"|_",
            "M":"|^\/^|",
            "N":"|\|",
            "O":"0xO()",
            "P":"||)",
            "Q":"()_",
            "R":"|)\\",
            "S":"(\)",
            "T":"-+|",
            "U":"~+|_|+~",
            "V":"+\/+",
            "W":"\/\/",
            "X":"\+/",
            "Y":"`|`",
            "Z":"~/_+",
            "`":"*`",
            "~":"*~",
            "!":"*!",
            "@":"*@",
            "#":"*#",
            "$":"*$",
            "%":"*%",
            "^":"*^",
            "&":"*&",
            "*":"**",
            "(":"*(",
            ")":"*)",
            "_":"*_",
            "-":"*-",
            "+":"*+",
            "=":"*=",
            "{":"*{",
            "}":"*}",
            "[":"*[",
            "]":"*]",
            ":":"*:",
            ";":"*;",
            "0":"0x0000",
            "1":"0x0001",
            "2":"0x0002",
            "3":"0x0003",
            "4":"0x0004",
            "5":"0x0005",
            "6":"0x0006",
            "7":"0x0007",
            "8":"0x0008",
            "9":"0x0009",
            "PYmili":"(世界上最帅的男人)",
            }
        self.x=[]
        self.y=[]
        for x,y in self.cd.items():
            self.x.append(x)
            self.y.append(y)
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
        path,file=os.path.split(filepath)
        file_s = f"{file}"
        enc=[f"FILE_S-->{file_s};\n"]
        with open(f"{file_s}.ENC", 'w+', encoding="utf-8") as index:
            print("读取文件内容——————》")
            for Msg in File_Msg:
                for m in Msg:
                    if m in self.cd.keys():
                        enc.append(self.cd[f'{m}']+";")
                    elif m not in self.x:
                        enc.append(m+";")
            for en in enc:
                print("加密后：",en)
                index.write(en)
    def dec(self, file):
        
        File_Msg=[]
        count = -1
        for count, lirn in enumerate(open(rf'{file}', 'r', encoding='utf-8')):
            pass
        count += 1
        line = count
        with open(f"{file}", 'r', encoding="utf-8") as dex:
            File_S=dex.readline()
            File_Msg=dex.read()
        dec=[]
        files=re.search("FILE_S-->(.*?);", File_S, re.S)
        if not files:
            filep="XXX.txt"
        else:
            filep=files.group(1)
        open(f"{filep}", 'w', encoding='utf-8')
        with open(f"{filep}", 'a+', encoding='utf-8') as dexc:
            print("解密内容：",File_Msg)
            for m in File_Msg.split(';'):
                if m in self.y:
                    dec.append(str(get_dict_key(self.cd, f"{m}")))
                elif m not in self.y:
                    dec.append(m)
            for de in dec:
                dexc.write(de)
            print("解密成功！")
