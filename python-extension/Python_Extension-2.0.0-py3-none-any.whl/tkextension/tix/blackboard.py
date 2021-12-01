# -*- coding: utf-8  -*-

from tkinter import *
from tkinter.colorchooser import *
from tkextension.tix.dialog import *

class BlackBoard():
    def __init__(self, tkinter_attribute, width=400, height=200, bg='#ffffff'):
        self.sqrite_type = 'line' # Sqrite
        self.color = 'black' # Color
        self.width = 1 # R
        self.x = width // 2 # Line
        self.y = height // 2 # Line
        self.on_slide = ['off'] # Slide
        self.do = [] # Undo
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        self.canvas = Canvas(self.frame, width=width, height=height, bg=bg)
        self.canvas.pack()
        lb = LabelFrame(self.frame, text='')
        lb.pack()
        self.sqriteset_btn = Button(lb, text='Sqrite', command=self.sqriteset)
        self.sqriteset_btn.grid(column=0, row=0, columnspan=2)
        self.colorchoose_btn = Button(lb, text='A', command=self.colorchoose)
        self.colorchoose_btn.grid(column=0, row=1)
        self.width_btn = Button(lb, text='Width ( W )', command=self.widthset)
        self.width_btn.grid(column=0, row=2)
        self.motion_on_btn = Button(lb, text='Turn on slide painting ( O )', command=self.onslide, state='normal')
        self.motion_on_btn.grid(column=1, row=1)
        self.motion_off_btn = Button(lb, text='Turn off slide painting ( F )', command=self.offslide, state='disabled')
        self.motion_off_btn.grid(column=1, row=2)
        self.undo_btn = Button(lb, text='Undo ( Z )', command=self.undo)
        self.undo_btn.grid(column=0, row=3)
        self.clean_btn = Button(lb, text='Clear', command=self.clean)
        self.clean_btn.grid(column=1, row=3)
        # Window
        self.canvas.bind_all('<KeyRelease>', self.key)
        self.canvas.bind('<Button-2>', self.sqrite_x)
        self.canvas.bind('<ButtonRelease-2>', self.sqrite_y)
        self.canvas.bind('<Button-1>', self.onslide)
        self.canvas.bind('<ButtonRelease-1>', self.offslide)
        self.canvas.bind('<Motion>', self.draw)
        # Bind
    def get(self):
        return self.frame
    def key(self, event):
        if event.char == 'A' or event.char == 'a':
            self.colorchoose(event)
        elif event.char == 'W' or event.char == 'w':
            self.widthset(event)
        elif event.char == 'O' or event.char == 'o':
            self.onslide(event)
        elif event.char == 'F' or event.char == 'f':
            self.offslide(event)
        elif event.char == 'Z' or event.char == 'z':
            self.undo(event)
        elif event.char == 'C' or event.char == 'c':
            self.clean(event)
    def draw(self, event):
        if self.on_slide[-1] == 'on':
            x1, y1 = (event.x - self.width), (event.y - self.width)
            x2, y2 = (event.x + self.width), (event.y + self.width)
            try:
                self.do[-1].append(self.canvas.create_oval(x1, y1, x2, y2, fill=self.color))
            except IndexError:
                self.do.append([])
                self.do[-1].append(self.canvas.create_oval(x1, y1, x2, y2, fill=self.color))
    def sqriteset(self, event=None):
        self.sqrite_type = askvalue('', 'Sqrite Choose', ['line', 'rectangle', 'oval', 'polygon'])
    def sqrite_x(self, event):
        self.x = event.x
        self.y = event.y
    def sqrite_y(self, event):
        if self.sqrite_type == 'line':
            self.do.append([self.canvas.create_line(self.x, self.y, event.x, event.y, fill=self.color)])
        elif self.sqrite_type == 'rectangle':
            self.do.append([self.canvas.create_rectangle(self.x, self.y, event.x, event.y, fill=self.color)])
        elif self.sqrite_type == 'oval':
            self.do.append([self.canvas.create_oval(self.x, self.y, event.x, event.y, fill=self.color)])
        elif self.sqrite_type == 'polygon':
            self.do.append([self.canvas.create_polygon(self.x, self.y, event.x, event.y, fill=self.color)])
    def onslide(self, event=None):
        self.on_slide.append('on')
        self.motion_on_btn.config(state='disabled')
        self.motion_off_btn.config(state='normal')
        self.do.append([])
    def offslide(self, event=None):
        self.on_slide.append('off')
        self.motion_on_btn.config(state='normal')
        self.motion_off_btn.config(state='disabled')
    def colorchoose(self, event=None):
        self.color = askcolor()
        self.color = self.color[1]
        self.colorchoose_btn.config(text='A', fg=self.color)
    def widthset(self, event=None):
        self.width = int(askanswer('', 'Width'))
    def undo(self, event=None):
        try:
            for x in self.do[-1]:
                self.canvas.delete(x)
            del self.do[-1]
        except IndexError:
            pass
    def clean(self, event=None):
        self.canvas.delete('all')
