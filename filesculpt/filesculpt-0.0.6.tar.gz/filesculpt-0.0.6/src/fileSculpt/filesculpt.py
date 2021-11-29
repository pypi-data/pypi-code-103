import re
import os

class Sculptfile:
    def __init__(self, findregex: re, replace: str, inpath: str, outpath=None):
        self.findregex = findregex
        self.replace = replace
        try:
            self.inpath = inpath
            if outpath == None:
                self.outpath = inpath
            else:
                try:
                    self.outpath = outpath
                except:
                    print("!!!! ------- Invalid Output path was specified ------- !!!!")
        except:
            print("!!!! ------- No Input path was specified ------- !!!!")

    def __str__(self):
        return f"{self.findregex} {self.replace} {self.inpath} {self.outpath}"

    def cleanpath(self,path):
        return path[1:] if path[0]=='/' else path

    def scuttle(self):
        output_set = None

        self.inpath=self.cleanpath(self.inpath)

        if self.inpath.count("/") < 1:
            self.inpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),self.inpath)

        with open(self.inpath, "r", encoding="UTF-8") as file:
            content = file.read()

            regexset = re.compile(self.findregex + r"()")
            output_set = re.findall(regexset, content)

        return output_set

    def sculpt(self):
        scuttled = self.scuttle()
        output_string = ""
        for entry in scuttled:
            for item in self.replace:
                if type(item) is int:
                    output_string += entry[item]
                else:
                    output_string += item
        
        self.outpath=self.cleanpath(self.outpath)

        if self.outpath.count("/") < 1:
            self.outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),self.outpath)

        with open(self.outpath, "w", encoding="UTF-8") as file:
            file.write(output_string)

