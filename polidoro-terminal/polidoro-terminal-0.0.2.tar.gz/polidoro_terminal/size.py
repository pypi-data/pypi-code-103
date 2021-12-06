import os


def size():
    env = os.environ

    cr = None
    try:
        cr = env['LINES'], env['COLUMNS']
    except Exception:
        pass

    # noinspection PyShadowingNames,PyBroadException,SpellCheckingInspection
    def ioctl_gwinsz(fd):
        try:
            import fcntl
            import termios
            import struct

            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except Exception:
            return
        return cr

    if not cr:
        cr = ioctl_gwinsz(0) or ioctl_gwinsz(1) or ioctl_gwinsz(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_gwinsz(fd)
            os.close(fd)
        except Exception:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])


columns = size()[0]


rows = size()[1]
