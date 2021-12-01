# This file is placed in the Public Domain.


import os
import pwd
import sys
import time


from .bus import Bus
from .dpt import Dispatcher
from .lop import Loop
from .obj import Object, cdir, get, update
from .obj import Cfg as ObjCfg
from .prs import parse
from .tbl import Table
from .thr import launch
from .utl import spl


starttime = time.time()


class Cfg(Object):

    console = False
    daemon = False
    debug = False
    index = None
    mod = ""
    mask = 0o22
    name = ""
    systemd = False
    uuids = []
    verbose = False
    version = None


class Runtime(Bus, Dispatcher, Loop):

    def __init__(self):
        Bus.__init__(self)
        Dispatcher.__init__(self)
        Loop.__init__(self)
        self.cfg = Cfg()
        self.classes = Object()
        self.cmds = Object()
        self.opts = Object()
        self.prs = Object()
        self.register("cmd", self.handle)

    def addcmd(self, cmd):
        Table.add(cmd)

    def cmd(self, clt, txt):
        if not txt:
            return None
        e = clt.event(txt)
        e.origin = "root@shell"
        e.parse()
        self.do(e)
        e.wait()
        return None

    def do(self, e):
        self.dispatch(e)

    def error(self, txt):
        pass

    def handle(self, clt, obj):
        obj.parse()
        f = None
        mn = get(Table.modnames, obj.prs.cmd, None)
        if mn:
            mod = Table.get(mn)
            if mod:
                f = getattr(mod, obj.prs.cmd, None)
        if not f:
            f = get(self.cmds, obj.prs.cmd, None)
        if f:
            f(obj)
            obj.show()
        obj.ready()

    def init(self, mns, threaded=False):
        for mn in spl(mns):
            mod = Table.get(mn)
            i = getattr(mod, "init", None)
            if i:
                self.log("init %s" % mn)
                if threaded:
                    launch(i)
                else:
                    i()

    def log(self, txt):
        pass

    def opt(self, ops):
        if not self.opts:
            return False
        for opt in ops:
            if opt in self.opts:
                return True
        return False

    def parse_cli(self):
        parse(self.prs, " ".join(sys.argv[1:]))
        update(self.opts, self.prs.opts)
        update(self.cfg, self.prs.sets)
        self.cfg.index = self.prs.index
        self.cfg.console = self.opt("c")
        self.cfg.daemon = self.opt("d")
        self.cfg.debug = self.opt("z")
        self.cfg.mask = 0o22
        self.cfg.systemd = self.opt("s")
        self.cfg.verbose = self.opt("v")

    def privileges(self, name, group):
        if not self.root():
            self.log("you need root privileges to run botc")
            return False
        try:
            pwn = pwd.getpwnam(name)
        except (TypeError, KeyError):
            self.log('add group/user with 1) groupadd botd 2) useradd -b /var/lib -d /var/lib/botd -m -g botd botd')
            return False
        try:
            pwn = pwd.getpwnam(name)
        except (TypeError, KeyError):
            return False
        if not os.path.exists(ObjCfg.wd):
            os.mkdir(ObjCfg.wd)
        cdir(ObjCfg.wd + os.sep)
        os.chown(ObjCfg.wd, pwn.pw_uid, pwn.pw_gid)
        cdir(os.path.join(ObjCfg.wd, "store", ""))
        os.chown(os.path.join(ObjCfg.wd, "store", ""), pwn.pw_uid, pwn.pw_gid)
        os.setgroups([])
        os.setgid(pwn.pw_gid)
        os.setuid(pwn.pw_uid)
        os.umask(Cfg.mask)
        self.cfg.uuids = os.getresuid()
        return True

    @staticmethod
    def root():
        if os.geteuid() != 0:
            return False
        return True

    @staticmethod
    def wait():
        while 1:
            time.sleep(5.0)
