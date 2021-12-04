# This file is placed in the Public Domain.


import base64
import os
import queue
import socket
import ssl
import textwrap
import time
import threading
import _thread


from .clt import Client
from .dbs import find, last
from .evt import Event
from .hdl import Handler
from .lop import Stop
from .obj import Object, cdir, update
from .obj import Cfg as ObjCfg
from .ofn import edit, fmt, save
from .opt import Output
from .thr import launch
from .tms import day, elapsed, parse_time
from .utl import getmain, kerror, klog


def __dir__():
    return (
        "init",
        "Cfg",
        "DCC",
        "Event",
        "IRC",
        "User",
        "Users",
        "cfg",
        "dlt",
        "locked",
        "met",
        "mre",
        "nck",
        "ops",
        "pwd",
    )

def cblog(clt, obj):
    txt = "%s %s" % (parse_time(day()), obj.txt)
    logdir = os.path.join(ObjCfg.wd, "logs")
    cdir(logdir)
    fn = os.path.join(logdir, obj.channel)
    f = open(fn, "a")
    f.write(txt)
    f.close()

def init():
    i = IRC()
    i.register("PRIVMSG", cblog)
    last(i.cfg)
    i.start()
    k = getmain("k")
    k.add(i)
    return i


def locked(obj):
    def lockeddec(func, *args, **kwargs):
        def lockedfunc(*args, **kwargs):
            obj.acquire()
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                obj.release()
            return res

        lockedfunc.__wrapped__ = func
        return lockedfunc

    return lockeddec


saylock = _thread.allocate_lock()


class NoUser(Exception):

    pass


class Cfg(Object):

    cc = "!"
    channel = "#botlib"
    nick = "botlib"
    password = ""
    port = 6667
    realname = "24/7 channel daemon"
    server = "localhost"
    servermodes = ""
    sleep = 30
    username = "botlib"
    users = False

    def __init__(self):
        super().__init__()
        for n in dir(Cfg):
            if not n.startswith("_"):
                self[n] = getattr(Cfg, n, None)


class Event(Event):
    def __init__(self):
        super().__init__()
        self.args = []
        self.arguments = []
        self.command = ""
        self.nick = ""
        self.rawstr = ""
        self.sock = None


class TextWrap(textwrap.TextWrapper):
    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = False
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450


class IRC(Output, Handler):

    def __init__(self):
        Handler.__init__(self)
        Output.__init__(self)
        self.buffer = []
        self.cfg = Cfg()
        self.connected = threading.Event()
        self.channels = []
        self.sock = None
        self.joined = threading.Event()
        self.keeprunning = False
        self.outqueue = queue.Queue()
        self.speed = "slow"
        self.state = Object()
        self.state.needconnect = False
        self.state.error = ""
        self.state.last = 0
        self.state.lastline = ""
        self.state.nrconnect = 0
        self.state.nrerror = 0
        self.state.nrsend = 0
        self.state.pongcheck = False
        self.threaded = False
        self.users = Users()
        self.zelf = ""
        self.register("903", h903)
        self.register("904", h903)
        self.register("AUTHENTICATE", AUTH)
        self.register("CAP", CAP)
        self.register("ERROR", ERROR)
        self.register("LOG", LOG)
        self.register("NOTICE", NOTICE)
        self.register("PRIVMSG", PRIVMSG)
        self.register("QUIT", QUIT)

    def announce(self, txt):
        for channel in self.channels:
            self.say(channel, txt)

    @locked(saylock)
    def command(self, cmd, *args):
        if not args:
            self.raw(cmd)
        elif len(args) == 1:
            self.raw("%s %s" % (cmd.upper(), args[0]))
        elif len(args) == 2:
            self.raw("%s %s :%s" % (cmd.upper(), args[0], " ".join(args[1:])))
        elif len(args) >= 3:
            self.raw(
                "%s %s %s :%s" % (cmd.upper(),
                                  args[0],
                                  args[1],
                                  " ".join(args[2:]))
            )
        if (time.time() - self.state.last) < 4.0:
            time.sleep(4.0)
        self.state.last = time.time()

    def connect(self, server, port=6667):
        if self.cfg.password:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ctx.check_hostname = False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = ctx.wrap_socket(sock)
            self.sock.connect((server, port))
            self.raw("CAP LS 302")
        else:
            addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
            self.sock = socket.create_connection(addr)
        os.set_inheritable(self.fileno(), os.O_RDWR)
        self.sock.setblocking(True)
        self.sock.settimeout(180.0)
        self.connected.set()
        return True

    def doconnect(self, server, nick, port=6667):
        self.state.nrconnect = 0
        while not self.stopped.isSet():
            self.state.nrconnect += 1
            try:
                if self.connect(server, port):
                    self.logon(server, nick)
                    break
            except (OSError, ConnectionResetError):
                klog("reconnect in %s" % elapsed(self.cfg.sleep))
            time.sleep(self.cfg.sleep)

    def dosay(self, channel, txt):
        wrapper = TextWrap()
        txt = str(txt).replace("\n", "")
        for t in wrapper.wrap(txt):
            if not t:
                continue
            self.command("PRIVMSG", channel, t)

    def event(self, txt):
        if not txt:
            return
        e = self.parsing(txt)
        cmd = e.command
        if cmd == "PING":
            self.state.pongcheck = True
            self.command("PONG", e.txt or "")
        elif cmd == "PONG":
            self.state.pongcheck = False
        if cmd == "001":
            self.state.needconnect = False
            if self.cfg.servermodes:
                self.raw("MODE %s %s" % (self.cfg.nick, self.cfg.servermodes))
            self.zelf = e.args[-1]
            self.joinall()
        elif cmd == "002":
            self.state.host = e.args[2][:-1]
        elif cmd == "366":
            self.joined.set()
        elif cmd == "433":
            nick = self.cfg.nick + "_"
            self.raw("NICK %s" % nick)
        return e

    def fileno(self):
        return self.sock.fileno()

    def joinall(self):
        for channel in self.channels:
            self.command("JOIN", channel)

    def handle(self, clt, e):
        self.dispatch(e)

    def keep(self):
        while not self.stopped.isSet():
            self.keeprunning = True
            time.sleep(60)
            self.state.pongcheck = True
            self.command("PING", self.cfg.server)
            time.sleep(10.0)
            if self.state.pongcheck:
                self.keeprunning = False
                try:
                    self.restart()
                except (OSError, ConnectionResetError, BrokenPipeError):
                    klog("reconnect in %s" % elapsed(self.cfg.sleep))
                    time.sleep(self.cfg.sleep)
                break

    def logon(self, server, nick):
        self.raw("NICK %s" % nick)
        self.raw(
            "USER %s %s %s :%s"
            % (self.cfg.username or "botd",
               server,
               server,
               self.cfg.realname or "botd")
        )

    def parsing(self, txt):
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        klog(txt.rstrip())
        o = Event()
        o.rawstr = rawstr
        o.orig = repr(self)
        o.command = ""
        o.arguments = []
        arguments = rawstr.split()
        if arguments:
            o.origin = arguments[0]
        else:
            o.origin = self.cfg.server
        if o.origin.startswith(":"):
            o.origin = o.origin[1:]
            if len(arguments) > 1:
                o.command = arguments[1]
                o.type = o.command
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.count(":") <= 1 and arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        o.arguments.append(arg)
                o.txt = " ".join(txtlist)
        else:
            o.command = o.origin
            o.origin = self.cfg.server
        try:
            o.nick, o.origin = o.origin.split("!")
        except ValueError:
            o.nick = ""
        target = ""
        if o.arguments:
            target = o.arguments[0]
        if target.startswith("#"):
            o.channel = target
        else:
            o.channel = o.nick
        if not o.txt:
            o.txt = rawstr.split(":", 2)[-1]
        if not o.txt and len(arguments) == 1:
            o.txt = arguments[1]
        spl = o.txt.split()
        if len(spl) > 1:
            o.args = spl[1:]
        o.type = o.command
        return o

    def poll(self):
        self.connected.wait()
        if not self.buffer:
            self.some()
        if self.buffer:
            return self.buffer.pop(0)

    def raw(self, txt):
        txt = txt.rstrip()
        if not txt.endswith("\r\n"):
            txt += "\r\n"
        txt = txt[:512]
        klog(txt.rstrip())
        txt += "\n"
        txt = bytes(txt, "utf-8")
        try:
            self.sock.send(txt)
        except BrokenPipeError:
            self.stop()
        self.state.last = time.time()
        self.state.nrsend += 1

    def say(self, channel, txt):
        self.oput(channel, txt)

    def some(self):
        self.connected.wait()
        inbytes = self.sock.recv(512)
        txt = str(inbytes, "utf-8")
        if txt == "":
            raise ConnectionResetError
        self.state.lastline += txt
        splitted = self.state.lastline.split("\r\n")
        for s in splitted[:-1]:
            self.buffer.append(s)
        self.state.lastline = splitted[-1]

    def start(self):
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        assert self.cfg.nick
        assert self.cfg.server
        assert self.cfg.channel
        save(self.cfg)
        self.stopped.clear()
        self.connected.clear()
        self.joined.clear()
        self.sock = None
        self.doconnect(self.cfg.server, self.cfg.nick, int(self.cfg.port))
        self.connected.wait()
        Handler.start(self)
        Output.start(self)
        if not self.keeprunning:
            launch(self.keep)
        self.wait()

    def stop(self):
        self.stopped.set()
        try:
            self.sock.shutdown(2)
        except OSError:
            pass
        Handler.stop(self)
        Output.stop(self)

    def wait(self):
        self.joined.wait()


class DCC(Client):

    def __init__(self):
        super().__init__()
        self.connected = threading.Event()
        self.encoding = "utf-8"
        self.origin = ""
        self.sock = None
        self.speed = "fast"

    def raw(self, txt):
        self.sock.send(bytes("%s\n" % txt.rstrip(), self.encoding))

    def announce(self, txt):
        pass

    def connect(self, dccevent):
        self.connected.clear()
        dccevent.parse()
        arguments = dccevent.prs.otxt.split()
        addr = arguments[3]
        port = int(arguments[4])
        if ":" in addr:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((addr, port))
        except ConnectionRefusedError:
            return
        self.sock.setblocking(1)
        os.set_inheritable(self.sock.fileno(), os.O_RDWR)
        k = getmain("k")
        k.add(self)
        self.raw("Welcome %s" % dccevent.origin)
        self.origin = dccevent.origin
        Handler.start(self)
        self.connected.set()

    def dosay(self, channel, txt):
        self.raw(txt)

    def event(self, txt):
        self.connected.wait()
        e = Event()
        e.type = "cmd"
        e.channel = self.origin
        e.origin = self.origin or "root@dcc"
        e.orig = repr(self)
        e.txt = txt.rstrip()
        e.sock = self.sock
        return e

    def handle(self, clt, e):
        self.connected.wait()
        k = getmain("k")
        k.put(e)

    def poll(self):
        txt = str(self.sock.recv(512), "utf8")
        if txt == "":
            raise Stop
        return txt

    def say(self, channel, txt):
        self.raw(txt)


class User(Object):
    def __init__(self, val=None):
        super().__init__()
        self.user = ""
        self.perms = []
        if val:
            update(self, val)


class Users(Object):

    userhosts = Object()

    def allowed(self, origin, perm):
        perm = perm.upper()
        origin = getattr(self.userhosts, origin, origin)
        user = self.get_user(origin)
        if user:
            if perm in user.perms:
                return True
        klog("denied %s" % origin)
        return False

    def delete(self, origin, perm):
        for user in self.get_users(origin):
            try:
                user.perms.remove(perm)
                user.save()
                return True
            except ValueError:
                pass

    def get_users(self, origin=""):
        s = {"user": origin}
        return find("user", s)

    def get_user(self, origin):
        u = list(self.get_users(origin))
        if u:
            return u[-1][-1]

    def perm(self, origin, permission):
        user = self.get_user(origin)
        if not user:
            raise NoUser(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            user.save()
        return user


def AUTH(clt, obj):
    clt.raw("AUTHENTICATE %s" % clt.cfg.password)


def CAP(clt, obj):
    if clt.cfg.password and "ACK" in obj.arguments:
        clt.raw("AUTHENTICATE PLAIN")
    else:
        clt.raw("CAP REQ :sasl")


def h903(clt, obj):
    clt.raw("CAP END")


def h904(clt, obj):
    clt.raw("CAP END")


def ERROR(clt, obj):
    clt.state.nrerror += 1
    clt.state.error = obj.txt
    kerror(obj.txt)


def KILL(clt, obj):
    pass


def LOG(clt, obj):
    pass


def NOTICE(clt, obj):
    if obj.txt.startswith("VERSION"):
        txt = "\001VERSION %s %s - %s\001" % (
            clt.cfg.name.upper(),
            clt.cfg.version or 1,
            clt.cfg.username or "bot",
        )
        clt.command("NOTICE", obj.channel, txt)


def PRIVMSG(clt, obj):
    if obj.txt.startswith("DCC CHAT"):
        if clt.cfg.users and not clt.users.allowed(obj.origin, "USER"):
            return
        try:
            dcc = DCC()
            dcc.connect(obj)
            return
        except ConnectionError:
            return
    if obj.txt:
        if obj.txt[0] in [clt.cfg.cc, "!"]:
            obj.txt = obj.txt[1:]
        elif obj.txt.startswith("%s:" % clt.cfg.nick):
            obj.txt = obj.txt[len(clt.cfg.nick)+1:]
        else:
            return
        splitted = obj.txt.split()
        splitted[0] = splitted[0].lower()
        obj.txt = " ".join(splitted)
        if clt.cfg.users and not clt.users.allowed(obj.origin, "USER"):
            return
        obj.type = "cmd"
        k = getmain("k")
        k.dispatch(obj)


def QUIT(clt, obj):
    if obj.orig and obj.orig in clt.zelf:
        clt.reconnect()



def cfg(event):
    c = Cfg()
    last(c)
    delkeys(event.prs.sets, ["mod"])
    if not event.prs.sets:
        event.reply(fmt(c, skip=["password", "stamp", "username", "realname"]))
        return
    edit(c, event.prs.sets)
    save(c)
    event.reply("ok")


def delkeys(self, keyz=None):
    if keyz is None:
        keyz = []
    for key in keyz:
        del self[key]


def dlt(event):
    if not event.prs.args:
        event.reply("dlt <username>")
        return
    selector = {"user": event.prs.args[0]}
    for _fn, o in find("user", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break


def met(event):
    if not event.prs.args:
        event.reply("met <userhost>")
        return
    user = User()
    user.user = event.prs.rest
    user.perms = ["USER"]
    save(user)
    event.reply("ok")


def mre(event):
    if event.channel is None:
        event.reply("channel is not set.")
        return
    if event.channel not in Output.cache:
        event.reply("no output in %s cache." % event.channel)
        return
    for txt in range(3):
        txt = Output.cache[event.channel].pop(0)
        if txt:
            event.say(txt)
    event.reply("(+%s more)" % Output.size(event.channel))


def nck(event):
    bot = event.bot()
    if isinstance(bot, IRC):
        bot.command("NICK", event.prs.rest)
        bot.cfg.nick = event.prs.rest
        save(bot.cfg)


def ops(event):
    bot = event.bot()
    if isinstance(bot, IRC):
        if bot.users.allowed(event.origin, "USER"):
            return
        bot.command("MODE", event.channel, "+o", event.nick)


def pwd(event):
    if len(event.prs.args) != 2:
        event.reply("pwd <nick> <password>")
        return
    m = "\x00%s\x00%s" % (event.prs.args[0], event.prs.args[1])
    mb = m.encode("ascii")
    bb = base64.b64encode(mb)
    bm = bb.decode("ascii")
    event.reply(bm)
