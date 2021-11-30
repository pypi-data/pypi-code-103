import pyant


def log_dbg(fmt, *args):
    msg = fmt % args
    pyant.DLOG(msg)


def log_inf(fmt, *args):
    msg = fmt % args
    pyant.ILOG(msg)


def log_wrn(fmt, *args):
    msg = fmt % args
    pyant.WLOG(msg)


def log_err(fmt, *args):
    msg = fmt % args
    pyant.ELOG(msg)


def log_fat(fmt, *args):
    msg = fmt % args
    pyant.FLOG(msg)
