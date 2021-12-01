from tkinter import *

class Card():
    def __init__(self, master, **args):
        self.windows_list = []
        self.index = 0
        self.frame = Frame(master, args)
    def update(self):
        for x in self.windows_list:
            x.forget()
        self.windows_list[self.index].pack()
    def get(self, index="frame"):
        if index == "frame":
            return self.frame
        elif index == "index":
            return self.index
        elif index == "windows":
            return self.windows_list
    def set(self, index):
        self.index = index
        self.index %= len(self.windows_list)
        self.update()
    def add(self, window):
        self.windows_list.append(window)
        self.update()
    def delete(self, index):
        self.windows_list.pop(index)
        self.index %= len(self.windows_list)
        self.update()
    def last(self):
        self.index -= 1
        self.index %= len(self.windows_list)
        self.update()
    def next(self):
        self.index += 1
        self.index %= len(self.windows_list)
        self.update()
