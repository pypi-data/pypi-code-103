from tkinter import *
from time import sleep
import threading
import random

class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    def run(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.root.geometry('400x240')
        self.root.title('Tekstas')
        self.root.resizable(False, False)
        self.text = Text(self.root, height=100, width=100)
        self.clipboard = ''
        self.cursor = '1.0'
        self.anchor = None
        self.selecting = False
        self.key_sink = None
        self.bind_key_sink()
        self.text.pack()
        self.text.focus()
        self.root.mainloop()

    def select(self, low, high):
        self.selecting = True
        [low, high] = sorted([low, high], key=lambda x: tuple(map(int, x.split('.'))))
        self.anchor = low if low != app.text.index(INSERT) else high
        self.text.tag_remove(SEL, '1.0', END)
        self.text.tag_add(SEL, low, high)

    def unselect(self):
        self.text.tag_remove(SEL, '1.0', END)
        self.selecting = False   

    def unbind_key_sink(self):
        if self.key_sink:
            self.text.unbind('<Key>', self.key_sink)

    def bind_key_sink(self):
        self.key_sink = app.text.bind('<Key>', lambda e: 'break')

    def store_cursor(self):
        self.cursor = self.text.index(INSERT)
        self.ensure_selection()
        self.text.see(INSERT)

    def ensure(self):
        sleep(0.025)
        while 'text' not in dir(self):
            sleep(0.01)
        self.text.mark_set(INSERT, self.cursor)
        self.ensure_selection()
    
    def ensure_selection(self):
        if self.selecting:
            print(self.anchor, self.text.index(INSERT))
            self.select(self.anchor, self.text.index(INSERT))

    def get_selection(self):
        try:
            result = self.text.selection_get()
        except TclError:
            return ''
        return result

def atsitiktinai(*funkcijos):
    random.choice(funkcijos)()

def at_random(*functions):
    random.choice(functions)()


def nebežymėti():
    app.ensure()
    app.unselect()
    app.store_cursor()

def unselect():
    nebežymėti()


def žymėti():
    app.ensure()
    app.selecting = True
    app.anchor = app.text.index(INSERT)
    app.store_cursor()

def select():
    žymėti()


def žymėti_viską():
    nebežymėti()
    į_pradžią()
    žymėti()
    į_pabaigą()

def select_all():
    žymėti_viską()


def pirmyn():
    app.ensure()
    position = app.text.index(INSERT)
    line, offset = map(int, position.split('.'))
    if app.text.index(END) == position:
        return
    if app.text.index('%s lineend' % position) == position:
        app.text.mark_set(INSERT, '%d.%d' % (line + 1, 0))
    else:     
        adjust = 1 if app.text.get(INSERT) else 2
        app.text.mark_set(INSERT, '%d.%d' % (line, offset + adjust))
    app.store_cursor()

def forward():
    pirmyn()


def atgal():
    app.ensure()
    position = app.text.index(INSERT)
    line, offset = map(int, position.split('.'))
    if position == '1.0':
        return
    if app.text.index('%s linestart' % position) == position:
        app.text.mark_set(INSERT, '%d lineend' % (line - 1))
    else:
        adjust = 1 if app.text.get('insert -1c') else 2
        app.text.mark_set(INSERT, '%d.%d' % (line, offset - adjust))
    app.store_cursor()

def back():
    atgal()


def rašyti(ką):
    app.ensure()
    if app.text.tag_ranges(SEL):
        app.text.delete(SEL_FIRST, SEL_LAST)
    app.unselect()
    app.text.insert(INSERT, ką)
    app.store_cursor()

def write(text):
    rašyti(text)


def pažymėta(kas):
    app.ensure()
    return app.get_selection() == kas

def selection_equals(text):
    return pažymėta(text)


def dėti_tarpą():
    rašyti(' ')

def space():
    dėti_tarpą()


def į_ankstesnę_eilutę():
    app.ensure()
    position = app.text.index(INSERT)
    line = int(position.split('.')[0])
    if line == 1:
        app.text.mark_set(INSERT, '%d.%d' % (1, 0))
    else:
        app.text.mark_set(INSERT, '%d.%d' % (line - 1, 0))
    app.store_cursor()

def to_previous_line():
    į_ankstesnę_eilutę()


def į_kitą_eilutę():
    app.ensure()
    line = int(app.text.index(INSERT).split('.')[0])
    if app.text.index(END) == '%d.%d' % (line + 1, 0):
        app.text.insert(END, '\n')    
    app.text.mark_set(INSERT, '%d.%d' % (line + 1, 0))
    app.store_cursor()

def to_next_line():
    į_kitą_eilutę()


def į_eilutės_pradžią():
    app.ensure()
    app.text.mark_set(INSERT, '%s linestart' % app.text.index(INSERT))
    app.store_cursor()

def to_beginning_of_line():
    į_eilutės_pradžią()


def į_eilutės_pabaigą():
    app.ensure()
    app.text.mark_set(INSERT, '%s lineend' % app.text.index(INSERT))
    app.store_cursor()

def to_end_of_line():
    į_eilutės_pabaigą()


def į_pradžią():
    app.ensure()
    app.text.mark_set(INSERT, '1.0')
    app.store_cursor()

def to_beginning():
    į_pradžią()


def į_pabaigą():
    app.ensure()
    app.text.mark_set(INSERT, app.text.index(END))
    app.store_cursor()

def to_end():
    į_pabaigą()


def klausti():
    nebežymėti()
    app.unbind_key_sink()
    stop_waiting = False
    offset_line, offset = map(int, app.text.index(INSERT).split('.'))
    span = 0
    def handle_return(event):
        nonlocal stop_waiting
        stop_waiting = True
        return 'break'
    def sink(event):
        return 'break'
    def handle_key(event):
        nonlocal span, offset_line, offset
        line, char = map(int, app.text.index(INSERT).split('.'))
        if line != offset_line or char < offset or char > offset + span:
            return 'break'
        span += 1
    def handle_backspace(event):
        nonlocal span, offset_line, offset
        line, char = map(int, app.text.index(INSERT).split('.'))
        if line != offset_line or char <= offset or char > offset + span:
            return 'break'
        span -= 1
    def handle_delete(event):
        nonlocal span, offset_line, offset
        line, char = map(int, app.text.index(INSERT).split('.'))
        if line != offset_line or char < offset or char >= offset + span:
            return 'break'
        span -= 1
    bindings = [
        ('<Return>', app.text.bind('<Return>', handle_return)),
        ('<Left>', app.text.bind('<Left>', sink)),
        ('<Right>', app.text.bind('<Right>', sink)),
        ('<ButtonPress>', app.text.bind('<ButtonPress>', sink)),
        ('<Key>', app.text.bind('<Key>', handle_key)),
        ('<BackSpace>', app.text.bind('<BackSpace>', handle_backspace)),
        ('<Delete>', app.text.bind('<Delete>', handle_delete)),
    ]
    app.text.focus_set()
    app.text.mark_unset(*app.text.mark_names())
    while not stop_waiting:
        sleep(0.1)
    app.select('%d.%d' % (offset_line, offset), '%d.%d' % (offset_line, offset + span))
    for sequence, binding in bindings:
        app.text.unbind(sequence, binding)
    app.bind_key_sink()
    app.store_cursor()

def read():
    klausti()


def eilutės_pradžia():
    app.ensure()
    return app.text.index(INSERT, '%s linestart' % app.text.index(INSERT)) == app.text.index(INSERT)

def at_beginning_of_line():
    return eilutės_pradžia()


def eilutės_pabaiga():
    app.ensure()
    return app.text.index(INSERT, '%s lineend' % app.text.index(INSERT)) == app.text.index(INSERT)

def at_end_of_line():
    return eilutės_pabaiga()


def pradžia():
    app.ensure()
    return app.text.index(INSERT) == '1.0'

def at_beginning():
    return pradžia()


def pabaiga():
    app.ensure()
    position = app.text.index(INSERT)
    line = int(position.split('.')[0])
    return app.text.index(END) == '%d.%d' % (line + 1, 0) and app.text.index('%s lineend' % position) == position

def at_end():
    return pabaiga()
    

def kopijuoti():
    app.ensure()
    app.clipboard = app.get_selection()

def copy():
    kopijuoti()


def trinti():
    rašyti('')

def delete():
    trinti()


def kirpti():
    kopijuoti()
    trinti()

def cut():
    kirpti()


def įklijuoti():
    rašyti(app.clipboard)

def paste():
    įklijuoti()


def pažymėta_spaudos_ženklų(kiek):
    app.ensure()
    return len(app.get_selection()) == kiek

def selection_consists_of_characters(n):
    return pažymėta_spaudos_ženklų(n)


def pažymėtas_tekstas_prasideda(kuo):
    app.ensure()
    return app.get_selection().startswith(kuo)

def selection_starts_with(what):
    return pažymėtas_tekstas_prasideda(what)


def pažymėtas_tekstas_baigiasi(kuo):
    app.ensure()
    return app.get_selection().endswith(kuo)

def selection_ends_with(what):
    return pažymėtas_tekstas_baigiasi(what)


def pažymėtame_tekste_yra(kas):
    app.ensure()
    return kas in app.get_selection()

def selection_contains(what):
    return pažymėtame_tekste_yra(what)


def pažymėtas_tekstas_yra_tekste(kokiame):
    app.ensure()
    return app.get_selection() in kokiame

def selection_contained_in(what):
    return pažymėtas_tekstas_yra_tekste(what)


def pažymėtas_tekstas_lygus_nukopijuotam():
    app.ensure()
    return app.get_selection() == app.clipboard

def selection_equal_clipboard():
    return pažymėtas_tekstas_lygus_nukopijuotam()

app = App()
