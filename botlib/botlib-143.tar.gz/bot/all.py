# This file is placed in the Public Domain.


import bot.bus as bus
import bot.clt as clt
import bot.dbs as dbs
import bot.dpt as dpt
import bot.evt as evt
import bot.fnd as fnd
import bot.irc as irc
import bot.log as log
import bot.lop as lop
import bot.obj as obj
import bot.ofn as ofn
import bot.opt as opt
import bot.prs as prs
import bot.rpt as rpt
import bot.run as run
import bot.rss as rss
import bot.sys as sys
import bot.tbl as tbl
import bot.thr as thr
import bot.tmr as tmr
import bot.tms as tms
import bot.udp as udp
import bot.utl as utl
import bot.ver as ver

from bot.tbl import Table

Table.addmod(bus)
Table.addmod(clt)
Table.addmod(dbs)
Table.addmod(dpt)
Table.addmod(evt)
Table.addmod(fnd)
Table.addmod(irc)
Table.addmod(log)
Table.addmod(lop)
Table.addmod(obj)
Table.addmod(ofn)
Table.addmod(opt)
Table.addmod(prs)
Table.addmod(rpt)
Table.addmod(rss)
Table.addmod(run)
Table.addmod(sys)
Table.addmod(tbl)
Table.addmod(thr)
Table.addmod(tmr)
Table.addmod(tms)
Table.addmod(udp)
Table.addmod(utl)
Table.addmod(ver)
