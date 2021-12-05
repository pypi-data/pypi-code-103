# Project ft
#
#   ftmain9.py      oct21
#
# V910: changes to setup.py
# V900: now as a package

# Import Modules 
import os
import pathlib
import argparse
import webbrowser
import tkinter as tk
from   tkinter import ttk

if __name__ == '__main__':
    from ftdb2 import *
else:
    from ftsim.ftdb2 import *

# Definitionen

class Gui(thr.Thread):
    """ Auch der grafische Teil der Anwendung muss als Thread laufen !"""
    def __init__(self, verbose, dbabout):
        thr.Thread.__init__(self)
        log.setVerbose(verbose)
        root = tk.Tk()
        app = App(root, dbabout)
        root.mainloop()


class App(ttk.Frame):
    """ Main Projekt Ft """

    # x, y, pad -> windowinfo()
    dlgsize = (832, 627, 20)

    def __init__(self, parent, dbabout, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.grid(row=0, column=0, padx=40, pady=5)

        self.parent = parent
        self.gitter = {}
        self.exitFlg = False
        self.auto = False       # Automatik

        self.threads = []
        self.wsdict = {}
        self.wspos = {}

        self.dbname, self.prjid, self.autorun = dbabout
        self.autokp = self.autorun # automatischer Abtransport am K-Platz

        # Hier wird nur die Konfiguration aus der DB gelesen
        with Db_connect(self.dbname, self.prjid) as dbinfo:
            if dbinfo:
                self.db = Ftdb(dbinfo)
                self.prjid = dbinfo[1]
                log.log(9,"DB\tRUN - OK - weiter gehts {0} {1} ".format(
                    dbinfo, self.prjid))
                self.createwidgts()
                self.createMenus()

                # Anlage / Projekt konfigurieren
                self.wslfa = self.db.prjconfig()
            else:
                try:
                    raise ValueError
                except ValueError:
                    log.log(1,"ERROR: DB-Name <{0}> oder prjid <{1}> ungültig!".format(
                        self.dbname, self.prjid))
                exit(0)

        parent.title("FTSIM - Warehouse with Transport Units - Version 0.9.1")

        # Workstations in eigenen Fenstern rechts von der Visualisierung anzeigen.
        winpos= self.getGeometry()
        self.parent.geometry(winpos)

        # Bestimmt die Gesamt-Geschwindigkeit im System (siehe ft.step())
        self.changeSpeed()

        # Erstellt und zeichnet alle LFer
        self.ftIni()

        # Automatikbetrieb
        if self.autorun:
            self.startThreads()

        # Tastatur Events auswerten
        parent.bind("<KeyPress>", self.keyb)

        # ! Einen eigenen Event registrieren
        # https://stackoverflow.com/questions/48862213/using-queue-with-tkinter-threading-python-3#48943101
        parent.bind("<<Tues>>", self.tues)


    def getGeometry(self):
        # 'geometry()', die sich aus createwidgts() ergeben hat, ermitteln.
        # Wird nur gebraucht, wenn sich an Grösse und Widgets was geändert hat.
        # self.windowinfo()

        posy = 196
        appx, appy, pad = App.dlgsize
        wsx,   wsy, pad = Ws.dlgsize
        screenx = self.parent.winfo_screenwidth()
        posx = screenx - 2*pad - appx - wsx
        winpos= "{0}x{1}+{2}+{3}".format(appx,appy, posx,posy)

        return winpos


    def windowinfo(self):
        """ aktuelle Werte als Argument für geometry() ermitteln [,py,TKWIN]

            Wenn die Fenstergröße nicht gesetzt wurde, sondern vom Displaymanager
            aus den Wiedgets ermittelt wurde, lassen sich die für  'geometry'
            notwendigen Werte folgendermassen ermitteln:
        """
        screen_x = self.parent.winfo_screenwidth()
        screen_y = self.parent.winfo_screenheight()

        # https://stackoverflow.com/questions/10448882/how-do-i-set-a-minimum-window-size-in-tkinter
        self.parent.update_idletasks()
        self.parent.after_idle(lambda: self.parent.minsize(
            self.parent.winfo_width(), self.parent.winfo_height()))
        wiegross = self.parent.geometry()
        l1 = wiegross.split("x")
        l2 = l1[1].split("+")
        print("W/H", screen_x, screen_y, wiegross, l1[0],l2[0])
        # ->  W/H 1920 1080 832x627+524+196 832 627


    def tues(self, *args):
        queue = Ft.guiqueue
        while queue.qsize() > 0:
            info = queue.get()
            self.moveLe(*info)

            # V76: Automatischer K-Platz mit zufälligen Abtransportzeiten
            if self.autokp and info[4] == "TRP":
                self.talkAuto(info[3])

    def moveLe(self, lfFromxy, lfToxy, leid, lfTo, kp=None):
        # App::moveLe

        r,t =  self.gitter[lfFromxy]
        self.sp.itemconfig(t, text="")
        if kp and kp != "TRP" :
            # clear entryfield
            self.talk(kp)

        r,t =  self.gitter[lfToxy]
        self.sp.itemconfig(t, text=leid)
        lfTo.talk()


    def startkp(self, wsid=None):
        # App::startkp
        """ Starte die angeforderte oder die erste Workstation """
        requested = wsid
        # gegebenenfalls die erste Ws
        if not wsid and len(self.wslfa):
            wsid = self.wslfa[0].lfname

        if wsid in self.wsdict:
            return
        
        # K-Platz muss erstellt werden
        for lf in self.wslfa:
            txt = "\t WS {0} LF {1}".format( wsid, lf.lfname)
            if wsid == lf.lfname:
                ws =  Ws(self, lf)
                self.wsdict[lf.lfname] = ws
                txt = "{0} requested {1}".format(txt, ws.always)
                # die unspezifische Ws schliesst sich nicht automatisch
                if not requested:
                    ws.setAlways(True)

                # jetzt scheint es zu gehen - d.h. Focus in entry
                self.talk(wsid)
                log.log(9,txt)


    def browser(self):
        #print("browser")
        url = 'https://ftsim.readthedocs.io/'
        webbrowser.open_new(url)


    def talk(self, wsid):
        # App::talk()
        """ LE am KP-Platz anzeigen und Focus setzen """

        if wsid in self.wsdict:
            ws = self.wsdict[wsid]
            lf = Lf.lfdict[wsid]
            ws.setLeid(lf)
            ws.focus_set()

            onCombo = True if lf.le else False
            # print("focus_choice *2* {0} <{1}>".format(onCombo, ws.lf))
            ws.focus_choice(onCombo)

    def talkAuto(self, lfTo):
        # App::talkAuto()
        if  lfTo.lfname in self.wsdict:
            # Automatischer Abtransport
            self.wsdict[lfTo.lfname].autotransport()

    def createMenus(self):
        # App::createMenus()
        # https://stackoverflow.com/questions/56041280/accelerators-not-working-in-python-tkinter-how-to-fix#56042178
        menubar = tk.Menu(self.parent, relief=tk.FLAT)
        self.parent.config(menu=menubar)

        fileMenu = tk.Menu(menubar, tearoff=0)
        self.kpvar = tk.IntVar()
        self.kpvar.set(bool(self.autokp))
        self.setautokp()
        fileMenu.add_checkbutton(label="Automatic Picking",
            variable=self.kpvar, onvalue=1, offvalue=0, command=self.setautokp,
            accelerator = 'F4')

        fileMenu.add_command(label="Start/Stop", command=self.startThreads,
            accelerator = 'F5')
        fileMenu.add_command(label="Exit", command=self.ende,
            accelerator='Ctrl+Q')
        menubar.add_cascade( label="File", menu=fileMenu, underline=0)

        optMenu = tk.Menu(menubar, tearoff=0)
        self.speedvar = tk.IntVar()
        optMenu.add_radiobutton(label="Speed 1", variable=self.speedvar,
            value=0, command=self.changeSpeed)
        optMenu.add_radiobutton(label="Speed 2", variable=self.speedvar,
            value=1, command=self.changeSpeed)
        optMenu.add_radiobutton(label="Speed 3", variable=self.speedvar,
            value=2, command=self.changeSpeed)
        menubar.add_cascade( label="Speed", menu=optMenu, underline=0)

        helpMenu = tk.Menu(menubar, tearoff=0)
        helpMenu.add_command(label="Help", command=self.browser)
        menubar.add_cascade( label="Help", menu=helpMenu, underline=0)


    def createwidgts(self):
        # App::createwidgts()

        # Größenangaben zum Spielfeld
        spparas = self.db.spconfig()

        # Spielfeld erstellen
        if spparas:
            fx,fy,fpx = spparas
            width  = fx*fpx
            height = fy*fpx + 1*fpx

        self.lb1 = ttk.Label(self, width=20, text="Projekt-Id <{}>".format(
            self.prjid))
        self.lb1.grid(row=0, column=1) 

        self.sp = tk.Canvas(self, width=width, height=height)
        self.sp.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E)

        self.initSp(fx,fy,fpx)
        px = "50"
        py = "20"

        self.kp1 = tk.Button(self, text='Workstation', command=self.startkp)
        self.kp1.grid(row=2, column=0, padx=px, ipady=0, pady=py,sticky=tk.W+tk.E)

        self.bstart = tk.Button(self, text='Start/Stop', command=self.startThreads)
        self.bstart.grid(row=2, column=1, padx=px, ipady=0, pady=py,sticky=tk.W+tk.E)

        self.bstop = tk.Button(self, text='Quit', command=self.ende)
        self.bstop.grid(row=2, column=2, padx=px, ipady=0, pady=py,sticky=tk.W+tk.E)

        #self.btest = tk.Button(self, text='Talk', command=self.browser)
        #self.btest.grid(row=3, column=0, padx=px, ipady=0, pady=py,sticky=tk.W+tk.E)


    def initSp(self, x, y, pix):
        """ Zeichenbrett malen """
        for spalte in range(x):
            for zeile in range(y):
                x0 = 0 + spalte * pix
                y0 = 0 + zeile  * pix
                y0 = 0 + (y-zeile)  * pix
                x1 = x0 + pix
                y1 = y0 + pix
                r = self.sp.create_rectangle(x0, y0, x1, y1,fill="orange")
                t = self.sp.create_text(x0+3, y0+12, text="", anchor = "w")
                self.gitter[(spalte,zeile)] = (r,t)

    def ftIni(self):
        Ft.app = self
        for n in Ft.fta:
            ft = Ft.fta[n]
            self.setBez(ft)
            for lf in ft.lfa:
                self.setRect(lf, "grey")

    def setBez(self,ft):
        """ Die Bezeichnung für den FT-Bereich anzeigen """
        xy = ft.xy
        if xy:
            r,t =  self.gitter[xy]
            self.sp.itemconfig(t, text=ft.name)


    def setRect(self, lf, color):
        # App::setRect
        r,t =  self.gitter[lf.xy]
        self.sp.itemconfig(r, fill=color)
        if lf.le:
            self.sp.itemconfig(t, text=lf.le.leid)

    def changeSpeed(self):
        """ Ändert die Laufgeschwindigkeit der LE's auf der FT. Damit die
            die Änderung wirksam wird, müssen die Threads neu gestartet werden.
        """
        speedarr = [0.4, 0.2, 0.05]
        speedvar = self.speedvar.get()
        self.speed = speedarr[speedvar]

        log.log(1, "Speed {0} gesetzt.".format(speedvar+1))
        if self.auto:
            self.auto = False
            # Erneut starten kann man sie hier nicht, sonst müßte geprüft
            # werden, ob die Threads alle gestoppt waren.

    def startThreads(self):
        # App::startThreads()
        """ start/stop the threads """
        self.auto = False if self.auto else True
        if not self.auto:
            log.log(1, "THREADS gestoppt !")
            return

        # DB-Operation bei Bewegungdaten
        orders = Orders()

        for ftname in Ft.fta:
            log.log(5, "TH {0:2s} gestartet".format(ftname))
            thread = Step(self, ftname, orders)
            thread.setDaemon(True)
            self.threads.append(thread)
            thread.start()


    def ende(self, destroy=True):
        # App::ende()
        self.auto = False
        self.exitFlg = True

        time.sleep(0.5)
        log.log(5, "THREAD es sind {} aktiv.".format(thr.active_count()))
        for i in range(6):
            alive = True
            for thread in self.threads:
                alive = alive and thread.is_alive()
                log.log(5, "\t {0} check {1} {2}".format(thread.name,
                    thread.is_alive(), alive))

            if not alive:
                break

        log.log(5, "Main THREAD closing.")
        if destroy:
            self.parent.destroy()


    def setautokp(self):
        self.autokp = self.kpvar.get()
        log.log(1, "Automatischer K-Platz ist <{0}>".format(bool(self.autokp)))

    def keyb(self, event):
        # App::keyb()
        key = event.keysym
        log.log(4, "APP\t Taste <{0}>".format(key))

        if key == "q" or key == "F3":
            self.ende()
        elif event.keysym == "F4":
            self.setautokp()
        elif event.keysym == "F5":
            self.startThreads()
        elif event.keysym == "k":
            self.startkp()
        else:
            # Für K-Plätze
            if key.isnumeric():
                key = 'k'+str(key)
            if key in Ft.fta:
                ft = Ft.fta[key]
                ft.step()


class Ws(tk.Toplevel):
    """ WS (Workstation) oder auch K-Platz """
    # x, y, pad -> windowinfo()
    dlgsize = (240, 135, 20)

    def __init__(self, master, lf):
        log.log(9,"\t WS {0} erstellen.".format(lf))

        self.farbe = "#98c3ec"
        tk.Toplevel.__init__(self, bg=self.farbe)

        self.lf = lf
        self.always = False # False = close dialog after transport

        self.master = master
        self.title("Workstation " + lf.ft.name)

        # Dialoggrösse und Position festlegen
        if self.lf.lfname in self.master.wspos:
            winpos = self.master.wspos[self.lf.lfname]
        else:
            wsx, wsy, pad = Ws.dlgsize
            screen_x = self.master.winfo_screenwidth()
            posx = screen_x - wsx - pad
            ftn = lf.ft.name
            #print("GEO:", screen_x, ftn[1:], winpos)
            posy =  int(ftn[1:]) * (wsy + 2*pad)
            winpos= "{0}x{1}+{2}+{3}".format(wsx,wsy,posx,posy)

        self.geometry(winpos)
        self.master.wspos[self.lf.lfname] = self.geometry()

        self.createwidgts()

        # Lagerfachsuche
        self.suche = Suche()

        # Tastatur Events auswerten
        self.bind("<KeyPress>", self.keyb)

        self.protocol("WM_DELETE_WINDOW", self.ende)

    def focus_choice(self, onCombo):
        if onCombo:
            self.cb1.focus_set()
        else:
            self.ent1.focus()

    def createwidgts(self):
        # Ws::createwidgts()
        # Widgets:  ~python/tk/grid/tktmpl_06.py 

        # https://stackoverflow.com/questions/54476511/setting-background-color-of-a-tkinter-ttk-frame

        ftnames = []
        for ftname in Ft.fta:
            ftnames.append(ftname)

        # Initialize style
        s = ttk.Style()
        s.configure('Lbl1.TLabel', background='orange')
        s.configure('Lbl2.TLabel', background=self.farbe)
        s.configure('Kp.TFrame'  , background=self.farbe)
        s.configure('Lbl3.TLabel' , foreground='green')
        s.configure('Lbl4.TLabel' , foreground='black', background=self.farbe)
        s.configure('Kp2.TFrame'  , foreground=self.farbe, background=self.farbe)

        self.basefr = ttk.Frame(self, style='Kp.TFrame', borderwidth=1)
        self.basefr.grid(row=0, column=0, padx=0, pady=0)

        # -1-
        self.fr1 = ttk.Frame(self.basefr, style='Kp2.TFrame')
        self.fr1.grid(row=0, column=0, padx=3, pady=2, sticky=tk.W)

        self.lb1 = ttk.Label(self.fr1, width=11, text="LE:", style='Lbl4.TLabel')
        self.lb1.grid(row=0, column=0) 

        self.leidvar = tk.StringVar()
        self.ent1 =  ttk.Entry(self.fr1, textvariable=self.leidvar, width=5)
        self.ent1.grid(row=0, column=1,  sticky=tk.W)

        leid = self.leidvar.get()
        self.leidvar.set(leid.upper())

        self.lb2 = ttk.Label(self.fr1, text="Target Area:", style='Lbl4.TLabel')
        self.lb2.grid(row=1, column=0, sticky=tk.W, pady=10)

        self.txtvar = tk.StringVar()
        self.cb1 =  ttk.Combobox(self.fr1, width=10, state="readonly",
                textvariable=self.txtvar)
        self.cb1.grid(row=1, column=1, sticky=tk.W)

        self.txtvar.set(ftnames[0])
        self.cb1.configure(values=ftnames)

        # Anzeige von Kommentaren und Fehlern
        self.msgvar = tk.StringVar()
        self.lb3 = ttk.Label(self.fr1, width=30, textvariable=self.msgvar,
                            anchor="center", style='Lbl4.TLabel')
        self.lb3.grid(row=2, column=0, columnspan=2, pady=5)
        self.msgvar.set("")

        # -2-
        self.fr2 = ttk.Frame(self.basefr, style='Kp.TFrame')
        self.fr2.grid(row=2, column=0)

        self.btp = tk.Button(self.fr2, text='New LE', command=self.newLe, width=5)
        self.btp.grid(row=0, column=0, padx=2, ipadx=1)

        self.btp = tk.Button(self.fr2, text='Transport', command=self.transport, width=5)
        self.btp.grid(row=0, column=1,  padx=2, ipadx=1)

        self.bquit = tk.Button(self.fr2, text='Quit', command=self.ende, width=5)
        self.bquit.grid(row=0, column=2,  padx=2, ipadx=1)


    def createwidgtsX(self):
        # Ws::createwidgts()
        # Widgets:  ~python/tk/grid/tktmpl_06.py 

        # https://stackoverflow.com/questions/54476511/setting-background-color-of-a-tkinter-ttk-frame
        ftnames = []
        for ftname in Ft.fta:
            ftnames.append(ftname)

        # Initialize style
        s = ttk.Style()
        s.configure('Lbl1.TLabel', background='orange')
        s.configure('Lbl2.TLabel', background=self.farbe)
        s.configure('Kp.TFrame'  , background=self.farbe)

        self.basefr = ttk.Frame(self, style='Kp.TFrame', borderwidth=1)
        self.basefr.grid(row=0, column=0, padx=0, pady=2)

        # -1-
        self.fr1 = ttk.Frame(self.basefr, style='Fr1.TFrame')
        self.fr1.grid(row=0, column=0, padx=3, pady=2, sticky=tk.W)

        # self.lb1 = ttk.Label(self.fr1, width=11, text="LE:", style='Lbl1.TLabel')
        self.lb1 = ttk.Label(self.fr1, width=11, text="LE:", style='Lbl1.TLabel')
        self.lb1.grid(row=0, column=0) 

        self.leidvar = tk.StringVar()
        self.ent1 =  ttk.Entry(self.fr1, textvariable=self.leidvar, width=5)
        self.ent1.grid(row=0, column=1)

        leid = self.leidvar.get()
        self.leidvar.set(leid.upper())

        # -2-
        # Alle Widgets sind jetzt nach links ausgerichtet (egal was man macht)
        self.fr2 = ttk.Frame(self.basefr, style='Kp.TFrame')
        self.fr2.grid(row=1, column=0, padx=2, pady=2)

        self.lb2 = ttk.Label(self.fr2, width=10, text="Target Area:", style='Lbl1.TLabel')
        self.lb2.grid(row=0, column=0, sticky=tk.W)

        #self.lb22 = ttk.Label(self.fr2, width=6, text="Area:", style='Lbl1.TLabel')
        #self.lb22.grid(row=1, column=0, sticky=tk.W)

        self.txtvar = tk.StringVar()
        self.cb1 =  ttk.Combobox(self.fr2, width=10, state="readonly",
                textvariable=self.txtvar)
        self.cb1.grid(row=0, column=1, sticky=tk.W)

        self.txtvar.set(ftnames[0])
        self.cb1.configure(values=ftnames)

        # Anzeige von Kommentaren und Fehlern
        self.msgvar = tk.StringVar()
        self.lb3 = ttk.Label(self.fr2, width=30, textvariable=self.msgvar,
                            anchor="center", style='Lbl2.TLabel')
        self.lb3.grid(row=1, column=0, columnspan=2, pady=10)
        self.msgvar.set("")

        # -3-
        self.fr3 = ttk.Frame(self.basefr, style='Kp.TFrame')
        self.fr3.grid(row=2, column=0)

        self.btp = tk.Button(self.fr3, text='New LE', command=self.newLe, width=5)
        self.btp.grid(row=0, column=0, padx=2, ipadx=1)

        self.btp = tk.Button(self.fr3, text='Transport', command=self.transport, width=5)
        self.btp.grid(row=0, column=1,  padx=2, ipadx=1)

        self.bquit = tk.Button(self.fr3, text='Quit', command=self.ende, width=5)
        self.bquit.grid(row=0, column=2,  padx=2, ipadx=1)

    def setAlways(self, wert):
        # Set always
        self.always = wert

    def keyb(self, event):
        # print("WS Taste <", event.keysym, ">")
        if event.keysym == "q":
            self.ende()
        # elif event.keysym == "t" or event.keysym == "Return":
        elif event.keysym == "Return":
            self.transport()
        elif event.keysym == "i":
            pass
            # logles()

    def __str__(self):
        return self.lf.lfname

    def __del__(self):
        #  Um die WS erneut öffnen zu koennen
        if self.lf.lfname in self.master.wsdict:
            del  self.master.wsdict[self.lf.lfname]

    def ende(self):   
        # Ws::ende()
        # https://stackoverflow.com/questions/41378577/closing-a-toplevel-tkinter-window?rq=1
        self.master.wspos[self.lf.lfname] = self.geometry()
        self.master.focus_set()
        self.destroy()
        self.__del__()


    def autotransport(self):
        """ LE automatisch vom K-Platz abtransportieren """
        # warte = randint(3000,8000)  jetzt mal speed
        warte = random.randint(self.master.speed * 7500, self.master.speed * 19000)
        log.log(4, "* {0:2s} * wait {1:2.1f} sec".format(
            self.lf.ft.name, warte/1000 ))
        self.lb1.after(warte, self.transport)


    def setLeid(self, lf):
        """ LE und Ziel in Combobox anzeigen """
        # Ws::setLeid ()
        leid = lf.le.leid if lf.le else ""
        self.leidvar.set(leid)

        if leid:
            ziel = self.suche.findLb()
            if ziel:
                self.txtvar.set(ziel)
            else:
                ziel = "--"

            log.log(4, "* {0:2s} * {1}: into Storeage Area to location {2:2s} ({3:2d})".format(
                lf.ft.name, leid, ziel, lf.le.lestat))

    def transport(self):
        # Ws::transport()
        leid = self.leidvar.get().upper()
        msg  = ""
        if leid in Le.lea:
            le = Le.lea[leid]
            # Soll eine LE, die ihr aktuelles Ziel noch nicht erreicht hat,
            # auch schon umgeroutet werden ?
            newziel= self.txtvar.get()
            log.log(9, "* {0:2s} * {1}: now has the target <{2}>".format(
                self.lf.ft.name, leid, newziel))

            if le.ziel != newziel:
                msg = "Transport of <{0}>  !".format(leid)
                le.ziel = newziel
                self.leidvar.set("")
                Ft.dbqueue.put((le, 60))

        elif leid:
            msg = "LE <{0}> does not exist !".format(leid)
        else:
            msg = "Please Enter LE!"

        self.msgvar.set(msg)
        self.setLeid(self.lf)

    def tell(self, txt):
        self.msgvar.set(txt)

    def newLe(self):
        """ Erstellt und setzt eine LE auf UEP """
        # Ws::newLe()

        leid = self.leidvar.get().upper()
        self.leidvar.set(leid)

        if not leid:
            self.tell("Please enter LE!")
            return
        elif  self.lf.le:
            self.tell("Locations is occupied with LE {0} !".format(self.lf.le))
            return
        elif leid not in Le.lea:
            ziel = self.lf.ft.name
            log.log(4, "* {0:2s} * {1}: New LE at location <{2}>!".format(
                ziel, leid, self.lf))

            # Das Ziel der LE muss die akt. FT sein
            le = Le(leid, ziel)

            self.lf.setLe(le)
            self.lf.ft.moveLe(self.lf, self.lf)
        else:
            self.tell("LE {0} does exist !".format(leid))


def ftmain():

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="ft.db", help="Database-name")
    parser.add_argument("--id", default=None, help="Projektnummer in der DB")
    parser.add_argument("--verbose", "-v",  type=int,  default=0,
            help="show Debug info (0,1,2,3)")
    parser.add_argument("--auto", help="Starts and Stops automatically ",
            action="store_true")
    args = parser.parse_args()

    dbpath = pathlib.Path(__file__).parent.resolve()
    dbname = os.path.join(dbpath, args.db)
    print("Database-name <{0}> \nProjet-Id <{1}> Verbose <{2}>".format(
        dbname, args.id, args.verbose))

    dbabout = (dbname, args.id, args.auto)
    guiThread = Gui(args.verbose, dbabout)
    guiThread.start()


###
### Hauptprogramm
###

if __name__ == '__main__':
    ftmain()

print("ENDE")
