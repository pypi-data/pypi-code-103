# -*- coding: utf-8  -*-

import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    raise SystemExit('This module needs Python 3.4 or more later')

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from pyextension import *
import tkextension as tix
import platform
import pickle
import time
import os

def askvalue(title='', msg='', args=(0, 100)):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    frame = tix.AskValue(tk, msg, args)
    frame.pack()
    Button(tk, text='OK', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = frame.get()
    tk.destroy()
    return get
# Askvalue
def askitem(title='', msg='', items=[], number=1, normal=0):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    frame = tix.AskItem(tk, msg, items, number, normal)
    frame.pack()
    Button(tk, text='OK', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = frame.get()
    tk.destroy()
    return get
# Askitem
def controlboard(title='', msg='', item=[('scale', '', 1, 100), ('listbox', '', [1, 2, 3])]):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    frame = tix.ControlBoard(tk, msg, item)
    frame.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = frame.get()
    tk.destroy()
    return get
# Controlboard
def singlechoices(title='', msg='', args=(('a', 'b', 'c'), ('e', 'f', 'g'))):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    a = tix.SingleChoices(tk, msg=msg, args=args)
    a.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = a.get()
    tk.destroy()
    return get
# Singlechoices
def answersheet(title='', msg='', args=[('a', 'b', 'c')], answer=['a'], points=[1]):
    tk = Tk()
    tk.title(title)
    tk.resizable(0, 0)
    # Tkinter
    a = tix.AnswerSheet(tk, msg=msg, args=args, answer=answer, points=points)
    a.pack()
    Button(tk, text='Finish', command=tk.quit).pack()
    # Window
    tk.mainloop()
    # Mainloop
    get = a.get()
    tk.destroy()
    return get
# Answersheet
def create(tkinter_attribute, mode='menu', args=[('1', '<function>')], AddToTkinter=(False, 'grid', 0, 0, 0, 0, 'center'), note='''Args of option menu only takes strings, likes: arg=['a', 'b', 'c']'''):
    tk = tkinter_attribute
    if mode == 'menu':
        a = Menu(tk)
        for x in args:
            a.add_command(label=x[0], command=x[1])
        if AddToTkinter[0] == True:
            tk.config(menu=a)
        return a
    elif mode == 'option menu':
        v = StringVar()
        a = 'OptionMenu(tk, v, '
        for x in arg:
            a = a + '\'' + x + '\''
            if x != args[-1]:
                a = a + ', '
        a = a + ')'
        b = exec(a)
        if AddToTkinter[0] == True:
            if AddToTkinter[1] == 'pack':
                b.pack()
            elif AddToTkinter[1] == 'grid':
                if AddToTkinter[4] == 0:
                    AddToTkinter[4] = 1
                if AddToTkinter[5] == 0:
                    AddToTkinter[5] = 1
                if AddToTkinter[6] == 'center':
                    AddToTkinter[6] = 'w'
                b.grid(column=AddToTkinter[2], row=AddToTkinter[3],
                       columnspan=AddToTkinter[4], rowspan=AddToTkinter[5],
                       sticky=AddToTkinter[6])
            elif AddToTkinter[1] == 'place':
                if AddToTkinter[4] != 0 and AddToTkinter[5] != 0:
                    b.place(relx=AddToTkinter[2], rely=AddToTkinter[3],
                            relwidth=AddToTkinter[4], relheight=AddToTkinter[5],
                            anchor=AddToTkinter[6])
                elif AddToTkinter[4] == 0 and AddToTkinter[5] == 0:
                    b.place(relx=AddToTkinter[2], rely=AddToTkinter[3],
                            anchor=AddToTkinter[6])
                else:
                    raise ValueError('Both relwidth and relheight must be 0 or not 0')
        return b
# Create
