#
#   Project ftsim
#   ftdb2   enthält alle DB-Zugriffe

import  sqlite3
import  threading as thr
try:
    from ftlib4 import *
except ModuleNotFoundError:
    print("Did not find Module ftlib4")
    from ftsim.ftlib4 import *

# Definitionen

# https://effbot.org/zone/python-with-statement.htm
class Db_connect():
    """ Creates a Database Connection
        and either checks the requested Project-Id
        or uses otherwise the highest Project-Id
    """
    app = None

    def __init__(self, dbname, prjid=None, fttyp="DB"):
        self.dbname = dbname
        self.app = None
        self.prjid = prjid
        self.fttyp = fttyp

        if self.fttyp == "DB":
            log.log(2, "DB\tDb_connect-Konstruktor: Controlled Execution")

    def __enter__(self):
        if self.fttyp != "DB":
            return False

        log.log(2, "DB\tSet up things for DB <{0}>".format(self.dbname))
        self.dbcon = sqlite3.connect(self.dbname)

        # Prüfen ob es die Projekt Version gibt
        cursor = self.dbcon.cursor()
        try:
            if self.prjid:
                sql = "select prjid from project where prjid=?"
                para = (self.prjid,)
                cursor.execute(sql, para)
            else:
                sql = "select max(prjid) from project "
                cursor.execute(sql)

        except sqlite3.OperationalError:
            return False

        res = cursor.fetchone()
        self.dbcon.commit()

        if res:
            self.prjid = res[0]
            return (self.dbcon, self.prjid)
        else:
            return False


    def __exit__(self, type, value, traceback):
        """ closes Database and threads """
        if self.fttyp == "DB":
            print("| DB\tTear things down (type <{0}> value <{1}> traceback <{2}>)".format(
                type,value, traceback))
            self.dbcon.close()
            # Closes all threads
            if  Db_connect.app:
                Db_connect.app.ende(destroy=False)


class Ftdb():
    """ Die Konfiguration der GesamtAnlage aus DB-Tabellen erstellen """

    def __init__(self, dbinfo):
        log.log(3, "Konstruktor Ftdb - Projekt")
        self.dbcon, self.prjid = dbinfo

        # Liste der Workstations
        self.wslfa = []

    def spconfig(self):
        para = (self.prjid,)
        sql = "select fieldx, fieldy, fieldpx from project where prjid = ?"
        cursor = self.dbcon.cursor()
        cursor.execute(sql, para)
        res= cursor.fetchone()
        self.dbcon.commit()
        return res

    def prjconfig(self):
        self.initLes()
        self.initFts()
        self.updLf()
        return self.wslfa

    def initLes(self):
        """ Ladeeinheiten erstellen """
        para = (self.prjid,)
        sql = "select leid, ftziel from le where prjid = ?"
        cursor = self.dbcon.cursor()
        cursor.execute(sql, para)
        row = cursor.fetchall()
        for leid, ftziel in row:
            log.log(3, "LE <{0:3s}> mit Ziel {1} erstellen.".format(leid, ftziel))
            cur = Le(leid, ftziel)

    def initFts(self):
        """ Fördertechnikbereiche mit zugehörigen Lagerfächern erstellen. """
        # Ftdb::initFts

        para = (self.prjid,)
        sql = "select ftname, fttyp, xbez, ybez from ft where prjid = ?"
        cursor = self.dbcon.cursor()
        cursor.execute(sql, para)
        fts = cursor.fetchall()
        for flds in fts:
            Ft(flds)

        for ftname in Ft.fta:
            self.initLfs(ftname)
        

    def initLfs(self, ftname):
        """ Lagerfächer initialisieren """
        ft = Ft.fta[ftname]
        para = (self.prjid, ftname)
        sql = """
            select lfname, xkor, ykor, leid, lftyp
            from lf
            where lf.prjid = ? and lf.ftname = ?
            order by 1
            """
        cursor = self.dbcon.cursor()
        cursor.execute(sql, para)
        lfs = cursor.fetchall()
        lfa = []
        for lfname, x, y, leid, lftyp in lfs:
            log.log(3, "LF <{0}> ".format(lfname))
            lf = Lf((x,y), ft, lfname)

            # Lagerfachtyp setzen
            if lftyp:
                if lftyp in ['KP']:
                    lf.setLftyp(lftyp)
                    self.wslfa.append(lf)
                else:
                    raise KeyError("Unbekannter LF Typ <" + lftyp + "> !")

            # Wo sich die LE befindet steht nur im LF
            if leid in Le.lea:
                log.log(3, "LE <{0}> auf LF <{1}>".format(leid, lfname))
                le = Le.lea[leid]
                lf.setLe(le)
                le.setStatus(lf)  # lestat = 20, wenn LE unterwegs

            lfa.append(lf)

        for lf in self.wslfa:
            log.log(3, "WS <{0}> auf Fördertechnik <{1}>".format(lf.lfname,lf.ft.name))

        # Die Lagerfächer in die FT einhängen
        ft.setLfa(lfa)

        # Die Lagerfachsuche initialisieren
        ft.initrandomLf()

    def updLf(self):
        # lf:  primary key    prjiid, lfname

        # die Lagerfächer kennen ihre Reihenfolge nicht, d.h.
        # sie brauchen innerhalb der Fördertechnik eine Liste 

        # Hier mussen wir die Lf Objekt suchen und dem Objekt zufuegen.
        # das geht also erst nachdem alle LFer angelegt wurden.

        #print("UPD", Lf.lfdict)
        para = (self.prjid, )
        sql = "select lfname, altlf from lfalt where prjid = ?"
        cursor = self.dbcon.cursor()
        cursor.execute(sql, para)
        res = cursor.fetchall()
        for lf1, lf2 in res:
            log.log(3, "LF={0}, Alternatives LF={1}".format(lf1,lf2))
            von = Lf.lfdict[lf1]
            nach = Lf.lfdict[lf2]
            von.setAltLf(nach)

        # Die Fördertechnikziele ermitteln
        sql = "select lfname, ftname from lfziel where prjid = ?"
        cursor.execute(sql, para)
        res = cursor.fetchall()
        for lfname, ftname in res:
            lf = Lf.lfdict[lfname]
            lf.addFtZiel(ftname) 

        sql = """
            select a.altlf, l1.ftname, l2.ftname from lfalt a
                join lf l1 on a.altlf = l1.lfname and a.prjid=l1.prjid
                join lf l2 on a.lfname=l2.lfname  and a.prjid=l2.prjid
                where l1.ftname != l2.ftname and a.prjid = ?
            """
        cursor.execute(sql, para)
        res = cursor.fetchall()
        for lfname, ftn1, ftn2 in res:
            cslis = [ftn1,ftn2]
            cslis.sort()
            log.log(3, "Critcal Section LF <{0}> {1} {2} {3}".format(
                lfname, ftn1, ftn2, cslis))
            lf = Lf.lfdict[lfname]
            # V48
            lf.setCritcalSection(tuple(cslis))

        self.dbcon.commit()

        # Soviele Locks erstellen, wie Lf.csdict Sätze hat.
        ftlocks = len(Lf.csdict)
        for i in range(ftlocks):
            Ft.locks.append(thr.Lock())
        log.log(5, "{0} FT-Lock(s) erstellt.".format(ftlocks))


class Orders():
    """ DB Operationen für Bewegungdaten """

    def __init__(self):
        log.log(6, "Konstruktor Orders ")

    def writeZeiten(self, taskoid):
        log.log(6, "WRITE ZEITEN")
        cursor = Step.dbcon.cursor()
        para = ( Ft.app.prjid, taskoid)
        sql = """
            insert into zeiten (prjid, taskoid, startt, endt, seq)
            select prjid, taskoid, startt, endt, seq
            from tasko where prjid=? and taskoid=?
            """
        cursor.execute(sql, para)

        # count open taskos
        sql = """
            select count(*) from tasko
            where prjid = ? and taskostat != 95
            """
        para = ( Ft.app.prjid, )
        cursor.execute(sql, para)
        res= cursor.fetchone()
        fertig = True if res[0]==0 else False

        sql = """
            insert into summen (prjid, startt, endt)
              select min(a.prjid), min(a.startt), max(a.endt) from tasko a
            where a.prjid = ? and exists (
              select 1 from tasko b where b.prjid=a.prjid)
            """
        if fertig:
            cursor.execute(sql, para)
            log.log(2, "DB\tZeiten in Tabelle 'summen' übertragen.")

        Step.dbcon.commit()

        log.log(6, "TASKO's left {0} fertig {1}".format(res[0],fertig))
        return fertig

    def shuffleTaskos(self):
        """ Zufällige Reihenfolge für Taskos erstellen """
        cursor = Step.dbcon.cursor()
        para = ( Ft.app.prjid,)
        sql = """
            select taskoid, rowid from tasko
            where prjid = ? order by 1
            """
        cursor.execute(sql, para)
        taskos = []
        rowids = []
        orders = cursor.fetchall()
        for taskoid, rowid in orders:
            taskos.append(taskoid)
            rowids.append(rowid)

        random.shuffle(rowids)
        for r,t in enumerate(taskos):
            log.log(6, "SHUFFLE ::: {0} {1} {2}".format(r, t, rowids[r]))
            para = (rowids[r], Ft.app.prjid, t)
            sql = """
                update tasko set seq = ?
                where prjid = ? and taskoid = ? """
            cursor.execute(sql, para)

        Step.dbcon.commit()


    def resetTasks(self):
        """ Tasko's und Task's zurücksetzten """

        cursor = Step.dbcon.cursor()
        para = ( Ft.app.prjid,)
        sql = """
            update task set taskstat = 0
            where prjid = ?
            """
        cursor.execute(sql, para)
        log.log(2, "DB\t<{0}> Tasks zurückgesetzt.".format(cursor.rowcount))
        sql = """
            update tasko set taskostat = 0, wsid=NULL, startt=NULL, endt=NULL
            where prjid = ?
            """
        cursor.execute(sql, para)
        log.log(2, "DB\t<{0}> Taskos zurückgesetzt.".format(cursor.rowcount))
        Step.dbcon.commit()

        # zufällige Reihenfolge bedeutet order by tasko.seq
        self.shuffleTaskos()

    def findtasko(self, ftname):
        """ Eine neue Tasko und einen freien K-Platz suchen und starten """

        para = (Ft.app.prjid,)
        sql = """
            select lf.ftname, a.taskoid
            from tasko a join lf on lf.prjid=a.prjid
            where lf.lftyp = 'KP' and a.taskostat = 0 and a.prjid = ?
            and not exists ( select 1 from tasko b
                where b.prjid=a.prjid and a.taskoid != b.taskoid
                    and b.wsid = lf.ftname and b.wsid not null
                    and b.taskostat < 95)
            order by a.seq
            """
        cursor = Step.dbcon.cursor()
        cursor.execute(sql, para)
        taskos = cursor.fetchall()
        for tasko in taskos:
            res, les = self.checktasks(tasko, ftname)
            if res:
                self.starttasko(*tasko, les)
                break

        Step.dbcon.commit()

    def checktasks(self, tasko, ftname):
        """ prüft ob alle LEs zur Tasko verfügbar sind """
        dummy, taskoid = tasko
        para = (Ft.app.prjid, taskoid)
        sql = """
            select t.leid from tasko o
                join task t on o.taskoid=t.taskoid and o.prjid=t.prjid
            where taskstat = 0 and t.prjid = ? and o.taskoid = ?
            order by 1 """

        cursor = Step.dbcon.cursor()
        cursor.execute(sql, para)
        tasks = cursor.fetchall()
        leids = []
        for task in tasks:
            leid = task[0]
            res = False
            if leid in Le.lea:
                le = Le.lea[leid]
                if le.lestat == 0:
                    res = True
                    leids.append(le)

            log.log(9, "* {0:2s} * {1}: Check Task -> {2}".format(
                ftname, leid, res))
            if res == False:
                break

        return res, leids


    def starttasko(self, ftziel, taskoid, les):
        """ Tasko und Tasks starten """
        dtnow = datetime.now()
        dts = dtnow.isoformat(sep=' ',timespec='milliseconds')
        para = (ftziel, dts, Ft.app.prjid, taskoid)
        sql = """
            update tasko set taskostat = 20, wsid = ?, startt = ?
            where prjid = ? and taskoid = ?
            """
        cursor = Step.dbcon.cursor()
        cursor.execute(sql, para)
        log.log(6, "* {0:2s} * DB : Starte TASKO {2} für KP-Platz {1} ".format(
            "x", ftziel, taskoid ))

        for le in les:
            para = (Ft.app.prjid, le.leid, taskoid)
            sql = """
                update task set taskstat =  20
                where prjid = ? and leid = ? and taskoid = ?
                """
            cursor.execute(sql, para)
            le.ziel = ftziel
            le.lestat = 20

        para = (ftziel, dts, Ft.app.prjid, taskoid)

    def taskAtKp(self, le, ftname):
        para = (Ft.app.prjid, le.leid)
        sql = """
            update task set taskstat =  60
            where prjid = ? and leid = ? and taskstat = 20
            """
        cursor = Step.dbcon.cursor()
        res = cursor.execute(sql, para)
        le.lestat = 60
        Step.dbcon.commit()
        log.log(6, "* {0:2s} * {1}: LE at KP (status {2})".format(
                    ftname, le.leid, le.lestat))


    def closeTask(self, le, ftname):
        para = (Ft.app.prjid, le.leid)
        cursor = Step.dbcon.cursor()

        # Alle offenen Tasks/LEs zur jeweiligen Tasko
        sql = """
            select a.rowid, a.leid, a.taskstat, a.taskoid
            from task a
            where a.prjid = ? and a.taskstat < 95 and exists
                (select 1 from task b
                    where b.leid = ?  and b.taskstat = 60 and
                    b.taskoid = a.taskoid and b.prjid = a.prjid)
            order by a.taskstat desc
            """
        cursor.execute(sql, para)
        tasks = cursor.fetchall()
        closetasko = None
        clt = True
        for rowid, leid, taskstat, taskoid in tasks:
            if  leid == le.leid:
                para = (rowid,)
                sql = "update task set taskstat=95 where rowid = ?"
                cursor.execute(sql, para)
                log.log(6, "* {0:2s} * {1}: CLOSE TASK to status 95 ".format(
                    ftname, le.leid))
                closetasko = taskoid
            else:
                clt = False

            log.log(9, "* {0:2s} * {1}: {2} {3} ??? {4}".format(
                    ftname, taskoid, leid, taskstat, clt))

        if clt and closetasko:
            dtnow = datetime.now()
            dts = dtnow.isoformat(sep=' ',timespec='milliseconds')
            para = (dts, Ft.app.prjid, closetasko)
            sql = """
                update tasko set taskostat=95, endt = ?
                where prjid = ? and taskoid = ?
                """
            log.log(6, "* {0:2s} * DB : CLOSE TASKO {1} ".format(
                    ftname, closetasko))
            cursor.execute(sql, para)

        Step.dbcon.commit()

        if clt and closetasko:
            fertig = self.writeZeiten(closetasko)
            if fertig and Ft.app.autorun:
                Ft.app.ende()


class Step(thr.Thread):
    """
        Jeder Fördertechnikbereich, die GUI und die DB
        laufen jeweils in einem eigenen Thread
    """
    dbcon = None

    def __init__(self, app, ftname, orders):
        thr.Thread.__init__(self)
        self.ftname = ftname
        self.app = app

        self.prjid = self.app.prjid
        self.dbname = self.app.dbname
        Ft.orders = orders


    def run(self):
        ft = Ft.fta[self.ftname]

        with Db_connect(self.dbname, self.prjid, ft.typ) as dbinfo:
            # Ein DB-Connect gibts nur für den DB-Thread
            if dbinfo:
                Step.dbcon = dbinfo[0]
                if ft.typ == "DB":
                    Ft.orders.resetTasks()

            self.loop(ft)


    def loop(self, ft):
        itest = 0

        # z.Z. sind alle Wartezeiten in den Treads gleich
        speed = ft.app.speed
        if ft.typ == "DB":
            log.log(1,"Wartezeit im Zyklus {0} Sekunden.".format(speed))

        while  self.app.auto and not self.app.exitFlg:
            itest += 1
            # log.log(1,"DB LOOP {0} Speed = {1}".format(itest, speed))
            ft.step(speed)

            # XXXX Durchlauf begrenzen !
            if itest > 3:
                pass
                # break
