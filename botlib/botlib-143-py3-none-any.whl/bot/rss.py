# This file is placed in the Public Domain.

import html.parser
import re
import threading
import urllib

from .dbs import Db, find, last
from .rpt import Repeater
from .tbl import Table
from .thr import launch
from .obj import Object, get, update
from .ofn import edit, save
from .utl import getmain

from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

gotparser = False
try:
    import feedparser

    gotparser = True
except ModuleNotFoundError:
    pass


def __dir__():
    return ("init",
            "Cfg",
            "Feed",
            "Rss",
            "Seen",
            "Fetcher",
            "dpl",
            "ftc",
            "rem",
            "rss")


def init():
    f = Fetcher()
    last(f.cfg)
    launch(f.start)
    return f


class Cfg(Object):

    def __init__(self):
        super().__init__()
        self.dosave = False
        self.display_list = "title,link"
        self.tinyurl = False


class Feed(Object):

    def __getattr__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError:
            self[k] = ""
            return self[k]


class Rss(Object):
    def __init__(self):
        super().__init__()
        self.rss = ""


class Seen(Object):
    def __init__(self):
        super().__init__()
        self.urls = []


class Fetcher(Object):

    cfg = Cfg()
    seen = Seen()

    def __init__(self):
        super().__init__()
        self.connected = threading.Event()

    def display(self, o):
        result = ""
        dl = []
        try:
            dl = o.display_list.split(",")
        except AttributeError:
            pass
        if not dl:
            dl = self.cfg.display_list.split(",")
        if not dl or not dl[0]:
            dl = ["title", "link"]
        for key in dl:
            if not key:
                continue
            data = get(o, key, None)
            if not data:
                continue
            data = data.replace("\n", " ")
            data = striphtml(data.rstrip())
            data = unescape(data)
            result += data.rstrip()
            result += " - "
        return result[:-2].rstrip()

    def fetch(self, feed):
        counter = 0
        objs = []
        for o in reversed(list(getfeed(feed.rss))):
            f = Feed()
            update(f, dict(o))
            update(f, feed)
            if "link" in f:
                u = urllib.parse.urlparse(f.link)
                if u.path and not u.path == "/":
                    url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
                else:
                    url = f.link
                if url in Fetcher.seen.urls:
                    continue
            Fetcher.seen.urls.append(url)
            counter += 1
            objs.append(f)
            if self.cfg.dosave:
                save(f)
        if objs:
            save(Fetcher.seen)
        k = getmain("k")
        for o in objs:
            txt = self.display(o)
            k.announce(txt)
        return counter

    def run(self):
        thrs = []
        for _fn, o in find("rss"):
            thrs.append(launch(self.fetch, o))
        return thrs

    def start(self, repeat=True):
        last(Fetcher.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()


def getfeed(url):
    k = getmain("k")
    if not gotparser or k.cfg.debug:
        return [Object(), Object()]
    try:
        result = geturl(url)
    except (ValueError, HTTPError, URLError):
        return [Object(), Object()]
    if not result:
        return [Object(), Object()]
    result = feedparser.parse(result.data)
    if result and "entries" in result:
        for entry in result["entries"]:
            yield entry


def gettinyurl(url):
    k = getmain("k")
    if k.cfg.debug:
        return []
    postarray = [
        ("submit", "submit"),
        ("url", url),
    ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = Request("http://tinyurl.com/create.php",
                  data=bytes(postdata, "UTF-8"))
    req.add_header("User-agent", useragent(url))
    for txt in urlopen(req).readlines():
        line = txt.decode("UTF-8").strip()
        i = re.search('data-clipboard-text="(.*?)"', line, re.M)
        if i:
            return i.groups()
    return []


def geturl(url):
    k = getmain("k")
    if k.cfg.debug:
        return
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header("User-agent", useragent("BOTLIB"))
    response = urllib.request.urlopen(req)
    response.data = response.read()
    return response


def striphtml(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def unescape(text):
    txt = re.sub(r"\s+", " ", text)
    return html.unescape(txt)


def useragent(txt):
    return "Mozilla/5.0 (X11; Linux x86_64) " + txt


def dpl(event):
    if len(event.prs.args) < 2:
        event.reply("dpl <stringinurl> <item1,item2>")
        return
    db = Db()
    setter = {"display_list": event.prs.args[1]}
    names = get(
        Table.names,
        "rss",
        [
            "rss",
        ],
    )
    _fn, o = db.lastmatch(names[0], {"rss": event.prs.args[0]})
    if o:
        edit(o, setter)
        save(o)
        event.reply("ok")


def ftc(event):
    res = []
    thrs = []
    fetcher = Fetcher()
    fetcher.start(False)
    thrs = fetcher.run()
    for thr in thrs:
        res.append(thr.join() or 0)
    if res:
        event.reply("fetched %s" % ",".join([str(x) for x in res]))
        return


def rem(event):
    if not event.prs.args:
        event.reply("rem <stringinurl>")
        return
    selector = {"rss": event.prs.args[0]}
    nr = 0
    got = []
    for _fn, o in find("rss", selector):
        nr += 1
        o._deleted = True
        got.append(o)
    for o in got:
        save(o)
    event.reply("ok")


def rss(event):
    if not event.prs.args:
        event.reply("rss <url>")
        return
    url = event.prs.args[0]
    if "http" not in url:
        event.reply("%s is not an url" % url)
        return
    res = list(find("rss", {"rss": url}))
    if res:
        return
    o = Rss()
    o.rss = event.prs.args[0]
    save(o)
    event.reply("ok")
