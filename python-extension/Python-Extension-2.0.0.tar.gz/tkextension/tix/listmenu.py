from tkinter import *

class ListMenu():
    def __init__(self, master, **args):
        self.widget_list = []
        self.frame = Frame(master, args)
    def get(self, index="frame"):
        if index == "frame":
            return self.frame
        elif index == "widget":
            return self.widget_list
    def add(self, master, window_type, do="", **args):
        """
        Frame, LabelFrame,
        Label, Message,
        Button, Checkbutton, Radiobutton,
        Listbox, OptionMenu, Scale,
        Entry, Text, Canvas,
        Menubutton,
        """
        if window_type == "frame" or window_type == "Frame":
            w = Frame(master, **args)
        elif window_type == "labelframe" or window_type == "LabelFrame":
            w = LabelFrame(master, **args)
        elif window_type == "label" or window_type == "Label":
            w = Label(master, **args)
        elif window_type == "message" or window_type == "Message":
            w = Message(master, **args)
        elif window_type == "button" or window_type == "Button":
            w = Button(master, **args)
        elif window_type == "checkbutton" or window_type == "Checkbutton":
            w = Checkbutton(master, **args)
        elif window_type == "radiobutton" or window_type == "Radiobutton":
            w = Radiobutton(master, **args)
        elif window_type == "listbox" or window_type == "Listbox":
            w = Listbox(master, **args)
        elif window_type == "optionmenu" or window_type == "OptionMenu":
            w = OptionMenu(master, **args)
        elif window_type == "scale" or window_type == "Scale":
            w = Scale(master, **args)
        elif window_type == "entry" or window_type == "Entry":
            w = Entry(master, **args)
        elif window_type == "text" or window_type == "Text":
            w = Text(master, **args)
        elif window_type == "canvas" or window_type == "Canvas":
            w = Canvas(master, **args)
        elif window_type == "menubutton" or window_type == "Menubutton":
            w = Menubutton(master, **args)
        else:
            raise AttributeError("Window type %s not found or not supported." % window_type)
        exec(do)
        self.widget_list.append(w)
