import os
import tkinter as tk
from tkinter import *

__all__=['Lolita']

class loltia:
    def __init__(self):
        self.Loltia="0.1"
        self.tk=tk.Tk()

    def title(self, msg="Lolita"):
        """窗口标题，参数：msg:str（默认Lolita）"""
        self.tk.title(msg)
    
    def size(self, sizes="200x200", x=0, y=0):
        """
        窗口比例及位置
        参数：sizes是窗口比例，默认200x200， x为电脑屏幕x轴，y为电脑屏幕y轴
        """
        self.tk.geometry(f'{sizes}+{x}+{y}')

    def minsize(self, wide=0, high=0):
        """
        窗口最小化限制，设置wide和high比例限制窗口最小比例
        参数：wide：int(宽) high:str(高)
        
        """
        self.tk.minsize(wide, high)

    def maxsize(self, wide=0, high=0):
        """
        窗口最大化限制，设置wide和high比例限制窗口最大化例
        参数：wide:int（宽）high:int（高）
        """
        self.tk.maxsize(wide, high)
    
    def ico(self, image=rf"{os.path.dirname(__file__)}\gui_logo.ico"):
        """
        窗口图标(.ico)：必须用.ico文件
        参数：image:PATH 文件路径
        """
        self.tk.iconbitmap(image)
    
    def overr(self, whether=False):
        """窗口边框设置:1为无边框"""
        self.tk.overrideredirect(whether)
    
    def loltia_bg(self, bg="black"):
        """窗口背景颜色"""
        self.tk['bg']=f"{bg}"

    def attributes(self, types='-toolwindow', sums=0):
        """窗口边框样式"""
        self.tk.attributes(types, sums)
    
    def Label(self, text="Label_None/*", bg="white", fg="black", font=False, width=False, height=False, textvariable=False):
        """
        Label标签：设置窗口标签：可用.pack()结束，也可用.palce(x=电脑屏幕x轴, y=电脑屏幕y轴)结束(必填)
        参数：text显示内容，bg背景颜色，fg=前景颜色，font字体，width宽，height高,textvariable获取StrVar参数
        """
        if text == "Label_None/*":
            self.label=None
        else:
            self.label=tk.Label(self.tk, text=text, bg=bg, fg=fg, font=font, width=width, height=height, textvariable=textvariable)
        return self.label

    def Button(self, text="Button_None/*", width=False, height=False, command=False):
        """
        Button按钮：设置窗口按钮：可用.pack()结束，也可用.palce(x=电脑屏幕x轴, y=电脑屏幕y轴)结束(必填)
        参数：text显示内容，width宽，height高,commmand指定并执行任意函数
        """
        if text=="Button_None/*":
            self.button=None
        else:
            self.button=tk.Button(self.tk, text=text, width=width, height=height, command=command)
            return self.button

    def Input_Box(self, show=None, font=None, width=None, bg=None, fg=None, bd=2, relief="groove", text=None):
        """
        输入框获取输入内容
        参数:show:将内容换一个字符串显示出来，font：设置字体，width:宽，bg:背景颜色，fg:前景颜色，relief:边框样式,text:获取StrVar参数
        """
        self.Entry=tk.Entry(self.tk, show=show, font=font, width=width, bg=bg, fg=fg, bd=bd, relief=relief, textvariable=text)
        return self.Entry

    def Text_Box(self, font=False, width=None, height=False, bg=None, fg=None, bd=2, relief="groove", text=None):
        """
        文本框获取输入内容
        参数:font：设置字体，width:宽，bg:背景颜色，fg:前景颜色，relief:边框样式,text:获取StrVar参数
        """
        self.Text=tk.Text(self.tk, font=font, width=width, height=height, bg=bg, fg=fg, bd=bd, relief=relief, textvariable=text)
        return self.Text
    
    def run(self):
        """无限运行"""
        self.tk.mainloop()

class StrVar(tk.StringVar):
    """
    使用tkinter库的StringVar类函数
    """
    def __init__(self, master=None, value=None, name=None):
        tk.StringVar.__init__(self, master, value, name)

class IntVar(tk.IntVar):
    """
    使用tkinter库的IntVar类函数
    """
    def __init__(self, master=None, value=None, name=None):
        tk.IntVar.__init__(self, master, value, name)

"""
新建时窗口时的默认窗口
"""
def Loltia():
    global l
    l=loltia()
    l.title()
    l.size()
    l.minsize()
    l.maxsize()
    l.ico()
    l.overr()
    l.loltia_bg()
    l.attributes()
    l.Label()
    l.Button()
    l.Text_Box()
    l.Input_Box()
    return l

def run():
    global l
    l.run()
