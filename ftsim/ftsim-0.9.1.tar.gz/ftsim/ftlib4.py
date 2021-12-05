#
#   Project ft
#   ftlib4   enthält die allgemeinen Klassen
#

import  random
import  time
import  queue
from    math import sqrt
from    datetime import datetime

# Definitionen

class Le():
    lea = {}
    # Kontrolliert Bewegungen in einem FT Zyklus bereichsübergreifend
    moved = {}

    def __init__(self, leid, ziel = None):
        self.leid = leid
        self.ziel = ziel
        self.lestat = 0     # nicht in DB

        Le.lea[leid] = self
        Le.moved[leid] = None

    def __str__(self):
        return "{0:3s}".format(self.leid) 

    def setStatus(self, lf):
        ft = lf.ft
        # print("LEEEE {} {}".format(self, ft.typ))
        if ft.typ != 'LB':
            self.lestat = 20


class Ft():
    """
    Die Fördertechnik (Ft) ist das eigentliche Grundelement. 
    Eine Fördertechnik enthält eine Sequenz von
    Plätzen (class Lf).
    Auf der Ft fahren Ladeeinheiten (Le) von einem
    Platz zum nächsten.
    Jeder Ft-Bereich läuft in einem eigenen Thread
    """

    fta = {}    # Fördertechnik Array
    typen = ['FT', 'LB', 'KP', 'DB']

    locks = []
    wait = True

    guiqueue = queue.Queue()
    dbqueue  = queue.Queue()

    app = None
    orders = None

    def __init__(self, felder):
        name, typ, xbez, ybez = felder
        if name not in Ft.fta:
            if typ not in Ft.typen:
                raise KeyError("Ft Typ <" + typ + "> gibt es nicht !")

            log.log(3, "Fördertechnik {0:4s} mit Typ {1} erstellt.".format(name,typ))
            self.name = name
            Ft.fta[name] = self
            self.lfa = []
            self.typ = typ
            self.itest = 0
            self.randomlf = None

            # Bezeichnung der FT (Position (0,0) wäre unten !)
            self.xy = None if xbez==0 and ybez==0 else (xbez,ybez)
        else:
            raise KeyError("Ft Element <" + name + "> gibt es schon!")

    def setLfa(self, lfa):
        """ Die Lagerfächer in die FT einhängen """
        self.lfa = lfa


    def initrandomLf(self):
        # Ft::randomLf

        if self.typ == "LB":
            self.randomlf = Randomlf(self)


    def tidy(self):
        # Ft::tidy
        """ nach jedem FT Zyklus moved zurücksetzen"""
        for leid in Le.moved:
            if self.name == Le.moved[leid]:
                log.log(9, "* {0:2s} * {1}: Tidy for FT = {2} ".format(
                    self.name, leid, Le.moved[leid]))
                Le.moved[leid] = None


    def step(self, speed=0.6):
        # Ft::step
        """ Ein FT Zyklus """

        if self.typ == "FT":
            self.stepFT()
        elif self.typ == "KP":
            self.stepKP()
        elif self.typ == "LB":
            self.stepLB()
        elif self.typ == "DB":
            self.stepDB()

        self.tidy()

        # Entscheidet über die Geschwindigkeit der LE's
        time.sleep(speed)


    def stepDB(self):
        # Ft::stepDB

        if Ft.dbqueue.qsize() > 0:
            le, status = Ft.dbqueue.get()
            log.log(6,"QUEUE get {0} status {1} ".format(le, status))
            if status == 95:
                # self.closeTask(le)
                le.lestat = 0
            elif status == 60:
                Ft.orders.taskAtKp(le, self.name)
                Ft.orders.closeTask(le, self.name)
        else:
            self.itest += 1
            # log.log(6,"I {0:8d} {1:4d}".format(self.itest, self.itest % 4))
            # erst nach jedem 4ten Step nach neuen Tasko's suchen
            if self.itest%4 == 0:
                Ft.orders.findtasko(self.name)
                # self.findtasko()

    def sleepLB(self, x, lf, le):
        """ V64: Verzögerung im Regal simulieren """
        # x += 4
        x = x * (1.5) + 3   # V72
        faktor = sqrt(x)
        res = faktor * Ft.app.speed
        # log.log(9,"x={0:2d} faktor {1:5.2f} -> {2:4.1f}".format(x, faktor, res))
        log.log(1, "* {0:2s} * {1}: Fahrzeit im Regal <{2:3.1f}>!".format(
                lf.ft.name, le, res ))
        time.sleep(res)

    def stepLB(self):
        """ vom ersten LF (Übergabeplatz) zu einem freien LF """
        # Ft::stepLB

        # UEP - Übergabeplatz
        ueplf = self.lfa[0]

        # 1) Steht auf dem UEP eine LE, die raus will ?
        le = self.lfa[0].le
        if le and le.ziel != self.name:
            # altlf = self.lfa[0].altLf 
            if not ueplf.altLf.le:
                self.moveLe(ueplf, ueplf.altLf)
                return

        # 2) Ist der UEP leer und will eine LE raus?
        if not ueplf.le:
            for i in range(1, len(self.lfa)):
                le = self.lfa[i].le
                if le and le.ziel:
                    if Ft.wait:
                        self.sleepLB(i, self.lfa[i],le)
                        Ft.wait = False
                    else:
                        self.moveLe(self.lfa[i], ueplf)
                        Ft.wait = True
                    return

        # 3) am UEP steht eine LE, die eingelagert werden will!
        gefunden = False
        le = ueplf.le
        if le and le.ziel == self.name: 

            wait, i = self.randomlf.waitandmove()
            if i > 0:   # LF gefunden
                res = False
                if wait:
                    self.sleepLB(i, self.lfa[i],le)
                else:
                    res = self.moveLe(ueplf, self.lfa[i])

                if res:
                    le.ziel = None
                    le.lestat = 0

                gefunden = True

            # Ist das Lager voll gehts zum NIO
            if not gefunden:
                ft = None
                if len(Ft.app.wslfa):
                    # der erste K-Platz ist der NIO
                    ft = Ft.app.wslfa[0].ft

                log.log(4, "* {0:2s} * {1}: Zurück mit Ziel {2}".format(
                    self.name, ueplf.le, ft.name))
                # besser wäre vielleicht, wenn es nach einer
                # erneuten Runde wieder ins Lager geht ? 
                ueplf.le.ziel = ft.name
                                

    def stepKP(self):
        # Ft::stepKP

        for i in reversed(range(0, len(self.lfa))):
            if self.lfa[i].le:
                if self.lfa[i].atKp():
                    continue

                lfNext, ftNext = self.lfa[i].findLf(i)
                if lfNext:
                    self.moveLe(self.lfa[i], lfNext)


    def stepFT(self):
        # Ft::stepFT

        # Lagerfächer der FT durchlaufen
        for i in reversed(range(0, len(self.lfa))):
            lf = self.lfa[i]
            if lf.le:
                lfNext, ftNext = lf.findLf(i)
                if lfNext:
                    log.log(9, "* {0:2s} * {1}: {2} {3} i={4} stepFT".format(
                        self.name, lf.le, lf, lfNext, i))
                    self.moveLe(lf, lfNext)


    def moveLe(self, lfFrom, lfTo):
        # Ft::moveLe
        le = lfFrom.le
        lastmove = None
        res = False
        kp = None

        if le.leid in Le.moved:
            lastmove =  Le.moved[le.leid] 
        if lastmove:
            log.log(4, "* {0:2s} * {1}: WAIT: LE muss warten !".format(
                        lfFrom.ft.name, lfFrom.le, lfTo.lfname))
            return res

        if lfTo.crisec:
            cs = Lf.csdict[lfTo.crisec]
            log.log(12, "* {0:2s} * {1}: {2} {3} cs{4:02d} crisec? ".format(
                lfFrom.ft.name, lfFrom.le, lfFrom, lfTo, cs ))
            dol = True  # doLocking
        else:
            cs = -1
            dol = False

        # Sonderfunktionen für den K-Platz
        if lfTo.lftyp == "KP":
            kp = "TRP"
        elif lfFrom.lftyp == "KP":
            kp = lfFrom.lfname

        if dol:
            dt = datetime.now()
            log.log(4, "* {0:2s} * {1}: {2} -> {3} cs{4:02d} {5:02d}{6:06d} "
                    "Aquired ".format( lfFrom.ft.name, lfFrom.le, lfFrom, lfTo,
                    cs, dt.second,  dt.microsecond))

            # Kritischer Bereich
            Ft.locks[cs].acquire()

        try:
            le = lfFrom.le
            if not dol:
                log.log(4, "* {0:2s} * {1}: {2} -> {3} {4}".format(
                    lfFrom.ft.name, lfFrom.le, lfFrom, lfTo, lfFrom.le.ziel))

            # Nochmal prüfen ob das lfTo wirklich frei ist !
            if lfTo.le is None or lfFrom is lfTo:
                # moveLe() wird auch beim Aufsetzen am K-Platz verwendet
                queue = Ft.guiqueue
                item = (lfFrom.xy, lfTo.xy, le.leid, lfTo, kp)
                Ft.guiqueue.put(item)

                lfFrom.le = None
                lfTo.le = le
                Le.moved[lfTo.le.leid] = lfTo.ft.name
                res = True

                # Jetzt die Gui triggern und dort die Queue auszulesen
                Ft.app.parent.event_generate("<<Tues>>", when="tail")
        except:
            print("!!! Exception in ft::moveLe() !!!")
            exit(0)

        finally:
            if dol:
                Ft.locks[cs].release()
                dt = datetime.now()
                fmt = "* {0:2s} * {1}: {2} -> {3} cs{4:02d} {5:02d}{6:06d}" \
                    + " Released"
                log.log(4,fmt.format(lfFrom.ft.name, lfTo.le, lfFrom, lfTo, cs,
                    dt.second, dt.microsecond))

        return res

class Lf():

    # Enthält alle LF-Namen, entspricht dem prim. key der Tabelle lf
    lfdict = {}
    csdict = {}

    def __init__(self, xy, ft, lfname, altLf = None):

        Lf.lfdict[lfname] = self
        self.xy = xy
        self.ft = ft
        self.lfname = lfname
        self.lftyp  = None
        self.altLf  = None
        self.le     = None
        self.crisec = False
        self.ftZiele = []

    def __str__(self):
        res = "{0:3s}".format(self.lfname)
        return res

    def setLe(self,le):
        # Lf:setLe
        self.le = le

    def setCritcalSection(self, cskey):
        self.crisec = cskey

        if cskey not in Lf.csdict:
            if not Lf.csdict:
                # print("CS1 csdict emtpy {} {}".format(cskey,Lf.csdict))
                Lf.csdict[cskey] = 0
            else:
                # Den höchsten Wert bzw dessen Schlüssel im Dictionary ermitteln
                key = max(Lf.csdict, key=Lf.csdict.get)
                Lf.csdict[cskey] = Lf.csdict[key] + 1
                # print("CS2 csdict       {} {}".format(cskey,Lf.csdict))


    def setAltLf(self, lf):
        self.altLf = lf

    def setLftyp(self, lftyp):
        self.lftyp = lftyp

    def addFtZiel(self, ftname):
        # Lf::addFtZiel()
        log.log(3, "Wegweiser: Über LF <{0}> gehts "
                " zu Fördertechik >{1}>".format(self, ftname))
        self.ftZiele.append(ftname)

    def talk(self):
        # Lf::talk
        if self.lftyp == 'KP':
            log.log(9, "\t {}: at KP ".format(self.le))
            # V39 KP nur starten wenn eine LE auf KP steht
            if self.le:
                #self.ft.app.startkp(self.lfname)
                #self.ft.app.talk(self.lfname)
                Ft.app.startkp(self.lfname)
                Ft.app.talk(self.lfname)

    def atKp(self):
        # Lf::atKp 
        ziel = self.le.ziel

        zielle = self.altLf.le if self.altLf else None
        log.log(9,"* {0:2s} * {3}: KP? LF={1} altLf={2} Ziel={4} LE auf Ziel={5}"
            " LF-Typ={6}".format(self.ft.name, self, self.altLf, self.le, ziel,
            zielle, self.lftyp))
        # K Platz erreicht, LE bleibt dort stehen bis ihr Ziel geändert wurde.
        if self.lftyp == 'KP' and ziel == self.ft.name:
            return True


    def findLf(self,i):
        """ Sucht den nächsten Platz und
            returns LF und FT, wenn es ein ein Fach gibt
        """
        # print("* {4} * Find LF={2} altLf={0} i={1} lfa={3}x".format(
        #    self.altLf,i,self, len(self.ft.lfa), self.ft.name ))

        # 1) Ft ist zu Ende und es gibt ein altLf
        if self.altLf and i == len(self.ft.lfa)-1:
            # print("lf {2}, altLf {0} i={1} le={3}".format(self.altLf,i,
            #           self,self.altLf.le))
            if not self.altLf.le:
                return self.altLf, self.altLf.ft

        # 2) Le hat ein Ziel und das ist auf dem Wegweiser
        ziel = self.le.ziel
        if self.altLf and ziel:
            # log.log(4, "\t {0}: hat das Ziel <{1}>".format(self.le, ziel))
            if ziel in self.altLf.ftZiele and not self.altLf.le:
                return self.altLf, self.altLf.ft

        # 3) Es gibt eine nächste Position
        if i < len(self.ft.lfa)-1:
            lf = self.ft.lfa[i+1]
            if not lf.le:
                return lf, None

        return None, None

class Randomlf():
    """
        Sucht ein zufälliges Lagerfach
        Im ersten Durchlauf (wait=True) merkt es sich das LF
        im 2ten liefert es das LF (idx) zurück
    """
    def __init__(self, ft):
        self.ft = ft
        self.cntlf = len(ft.lfa) - 1
        self.wait = True
        log.log(3, "RANDOM Lagerbereiche: {0} hat !!!!!".format(ft.name))

    def waitandmove(self):
        log.log(3, "Wait {0}".format(self.wait))
        waitwas = self.wait
        if self.wait:
            self.idx = self.findRandom()
            # Wenn nichts gefunden wurde, sequentiel suchen
            if self.idx == 0:
                self.idx = self.findArray()
            if self.idx:
                self.wait = False
        else:
            log.log(3, "And Move to idx = {0}".format(self.idx))
            self.wait = True

        return waitwas, self.idx

    def findArray(self):
        """ ein freies LF finden, wenn es eines gibt """
        # Randomlf::findArray
        lfres = None
        for idx in range(1, self.cntlf+1):
            lf = self.ft.lfa[idx]
            # log.log(3, "ARRAY idx {2} Lf {0} LE {1} ".format(lf,lf.le,idx))
            if lf.le == None:
                lfres = lf
                break

        idx = idx if lfres else 0
        # log.log(3, "FOUND {0} AT {1}".format(lfres,idx))
        return idx

    def findRandom(self):
        """ ein freies LF per Zufall finden """
        # Randomlf::findRandom
        lfres = None
        for _ in range(self.cntlf):
            idx = random.randint(1,self.cntlf)
            lf = self.ft.lfa[idx]
            # log.log(3, "RANDOM idx {2} Lf {0} LE {1} ".format(lf,lf.le,idx))
            if lf.le == None:
                lfres = lf
                break

        idx = idx if lfres else 0
        # log.log(3, "FOUND {0} AT {1}".format(lfres,idx))
        return idx


class Suche():
    """ Lagerbereiche ermitteln """

    def __init__(self):
        self.nLb = 0
        self.lbarray = []
        for name in Ft.fta:
            ft = Ft.fta[name]
            if ft.typ == "LB":
                self.nLb += 1
                self.lbarray.append(ft.name)

        log.log(3, "<{0}> Lagerbereiche: {1} ".format(self.nLb,
                self.lbarray))

    def findLb(self):
        """ zufällige Lagerbereichssuche """
        if self.nLb > 1:
            idx = random.randint(0, self.nLb-1)
            ziel = self.lbarray[idx]
        elif self.nLb == 1:
            ziel = self.lbarray[0]
        else:
            ziel = None

        return ziel


class Log():
    """ Global Logging System
        Verbose wird beim Aufruf der Anwendung festgelegt.
        Level ist im Code, also beim Aufruf der Log-Ausgabe hinterlegt.
    """
    # specific >= 3 :
    #
    # verbose logs
    #         1   2   |   3   4   5  6
    # 1       X   -   |   -   -   -  -
    # 2       X   X   |   -   -   -  -
    # 3       X   X   |   X   -   -  -    DB - Konfiguration
    # 4       X   X   |   -   X   -  -    Routing
    # 5       X   X   |   -   -   X  -    Threads
    # 6       X   X   |   -   -   -  X    DB - Tasks
    # ...
    #
    # verbose 9 = alles 

    def __init__(self):
        self.verbose = 0

    def log(self,level=0, txt=""):
        if not level:
            return

        output = False
        specific = 3   
        # print("LEVEL {0} {1}".format(level, self.verbose))
        if self.verbose == 9:
            output = True
        elif self.verbose < specific:
            if level <= self.verbose:
                output = True
        elif level < specific or level == self.verbose:
                output = True

        if output:
                print("| {0}".format(txt))

    def setVerbose(self,verbose):
        self.verbose = verbose
        # print("Verbose now {0}".format(verbose))


# Initialize Global Logging System
log = Log()
