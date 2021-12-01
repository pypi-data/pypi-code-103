# -*- coding: utf-8  -*-

from tkinter import *
import platform as p
import getpass
import os

class FileTree():
    def __init__(self, tkinter_attribute, filetypes=[('All Files', '')], path=None, width=200, height=200):
        self.filetypes = filetypes
        self.location = ''
        if p.system() == 'Windows':
            self.done = ['C:\\']
        elif p.system() == 'Darwin':
            self.done = ['/Users/' + getpass.getuser()]
        elif p.system() == 'Linux':
            self.done = ['/home']
        self.redo = []
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk, width=width, height=height)
        # Tkinter
        self.tree = Listbox(self.frame)
        self.tree.place(relx=0.5, rely=0.5, relwidth=0.96, relheight=0.8, anchor='center')
        self.entry = Entry(self.frame)
        self.entry.place(relx=0.5, rely=0.05, relwidth=0.96, relheight=0.1, anchor='center')
        self.undo_btn = Button(self.frame, text='Undo', command=self.undo)
        self.undo_btn.place(relx=0.15, rely=0.95, relwidth=0.3, relheight=0.1, anchor='center')
        lst = []
        for x in filetypes:
            lst.append([])
            if type(x[0]) == type(()):
                lst[-1].append([])
                for y in x[0]:
                    lst[-1][-1].append(y)
            elif type(x[0]) == type('abc'):
                lst.append([x[0]])
            if type(x[1]) == type(()):
                lst[-1].append([])
                for y in x[1]:
                    lst[-1][-1].append(y)
            elif type(x[1]) == type('abc'):
                lst.append([x[1]])
        Spinbox(self.frame, value=lst, wrap=True, state='readonly').place(relx=0.65, rely=0.95, relwidth=0.7, relheight=0.1, anchor='center')
        # Window
        if p.system() == 'Windows':
            if path == None:
                self.location = 'C:\\'
            else:
                self.location = path
        elif p.system() == 'Darwin':
            if path == None:
                self.location = '/Users/' + getpass.getuser()
            else:
                self.location = path
        elif p.system() == 'Linux':
            if path == None:
                self.location = '/home'
            else:
                self.location = path
        else:
            raise SystemExit('System \'%s\' is not supported' % p.system())
        self.entry.insert('end', self.location)
        self.items = os.listdir(self.location)
        # Items
        self.entry.bind('<Any-KeyRelease>', self.relist)
        self.tree.bind('<Double-Button-1>', self.into)
        # Bind
        self.update()
    def get(self):
        return self.frame
    def relist(self, event=None, mode='entry'):
        if mode == 'entry':
            self.location = self.entry.get()
            self.done.append(self.location)
            print(self.done)
        try:
            self.items = os.listdir(self.location)
            if mode == 'into':
                self.entry.delete(0, 'end')
                self.entry.insert('end', self.location)
        except OSError:
            self.entry.delete(0, 'end')
            self.entry.insert('end', self.location)
        self.update()
    def into(self, event=None):
        try:
            os.listdir(self.location)
            if p.system() == 'Windows':
                self.location = self.location + '\\' + self.tree.get('active')
            elif p.system() == 'Darwin' or p.system() == 'Linux':
                self.location = self.location + '/' + self.tree.get('active')
        except OSError:
            pass
        self.relist(mode='into')
    def update(self):
        types = []
        for x in self.filetypes:
            if type(x[1]) == type(()):
                for y in x[1]:
                    types.append(y)
            elif type(x[1]) == type('abc'):
                types.append(x[1])
        self.tree.delete(0, 'end')
        for x in self.items:
            if '' in types or '.*' in types:
                self.tree.insert('end', x)
                continue
            for y in types:
                try:
                    try:
                        open(self.location + '/' + x[:-4] + y)
                    except IndexError:
                        open('Raise Error.raise_error')
                    self.tree.insert('end', x)
                    break
                except OSError:
                    try:
                        os.listdir(self.location + '/' + x)
                        self.tree.insert('end', x)
                        break
                    except OSError:
                        pass
    def undo(self):
        self.entry.delete(0, 'end')
        try:
            self.entry.insert('end', self.done[-1])
        except IndexError:
            if p.system() == 'Windows':
                self.done = ['C:\\']
            elif p.system() == 'Darwin':
                self.done = ['/Users/' + getpass.getuser()]
            elif p.system() == 'Linux':
                self.done = ['/home']
        self.location = self.entry.get()
        del self.done[-1]
        self.done.append(self.location)
        self.relist(mode='undo')
        
    def get(self):
        self.location = self.entry.get()
        try:
            data = os.listdir(self.location)
        except OSError:
            data = self.location
        return data
