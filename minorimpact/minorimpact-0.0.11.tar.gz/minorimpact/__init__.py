#!/usr/bin/env python3

import hashlib
import os
import os.path
import psutil
import random
import re
import sys

__version__ = "0.0.11"

default_arg_flags = { 'debug':False, 'dryrun':False, 'force':False, 'verbose':False, 'yes':False }

def checkforduplicates(pidfile = None):
    """Checks pidfile to see if an instance of this script is already running.

    Checks the process list for a current process with the id stored in pidfile.  If no such
    process exists, stores the current process id in pidfile and returns False, otherwise returns
    True.

    Parameters
    ----------
    pidfile: string
        The full pathname of the file that contains the process id.

    Returns
    -------
    boolean
        True if another version of this script is already running, False otherwise.
    """
    if (pidfile is None):
        return False

    oldpid = None
    if (os.path.exists(pidfile)):
        with open(pidfile, "r") as p:
            oldpid = p.read().rstrip()

    if (oldpid is not None):
        for proc in psutil.process_iter():
            try:
                if int(oldpid) == proc.pid:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    pid = os.getpid()

    with open(pidfile, "w") as p:
        p.write(str(pid))
    return False

def disksize(*args, **kwargs):
    return filesize(*args, **kwargs)

# Prints to stderr.
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def filesize(size, units="k"):
    """Takes a the size of the file and type of unit, returns a human readable file size string."""
    if (units.lower() == "g"):
        size = size * 1024 * 1024 * 1024
    elif (units.lower() == "m"):
        size = size * 1024 * 1024
    elif (units.lower() == "k"):
        size = size * 1024

    if (size > 1024*1024*1024):
        return f"{size/(1024*1024*1024):.1f}GB"
    if (size > 1024*1024):
        return f"{size/(1024*1024):.1f}MB"
    if (size > 1024):
        return f"{size/(1024):.1f}KB"
    return f"{size}B"

def fprint(*args, **kwargs):
    """Identical to print(), but it flushes the cache everytime.  Useful to capture stdout from a long running cron."""
    print(*args, flush=True, **kwargs)

def getChar(default = None, end = '\n', prompt = None, echo = False):
    """Gets a single character from stdin.

    Parameters
    ----------
    default:string
        Value to return if the user simply presses 'return'.
    echo:boolean
        If True, display the pressed character. Default: False
    end:string 
        What to follow the character with, if echo is True. Default: '\n'
    prompt:string
        A string to print before pausing for input.

    Returns
    ------
    string
        A single character input by the user.
    """

    # figure out which function to use once, and store it in _func
    if "_func" not in getChar.__dict__:
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            getChar._func=msvcrt.getch

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios # raises ImportError if unsupported

            def _ttyRead():
                fd = sys.stdin.fileno()
                oldSettings = termios.tcgetattr(fd)

                try:
                    tty.setcbreak(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

                return answer

            getChar._func=_ttyRead

    if (prompt is not None):
        print(prompt, end = '', flush = True)
    c = getChar._func()
    if (default is not None and c == '\n'): c = default
    if (echo):
        if (c == '\n'): print("", end = end, flush = True)
        else: print(c, end = end, flush = True)
    return c

def killduplicates(pidfile = None):
    """Read a process id from pidfile and kill the matching process if it's currently running."""
    if (pidfile is None):
        return

    if (checkforduplicates(pidfile)):
        with open(pidfile, "r") as p:
            pid = p.read().rstrip()
            psutil.Process(int(pid)).kill()

def md5dir(filename):
    """Given a file or directory path, returns the combined md5sum of it and everything under it, recursively"""
    m = hashlib.md5()
    if (os.path.isdir(filename)):
        for f in sorted(os.listdir(filename)):
            md5 = md5dir(filename + "/" + f)
            m.update(md5.encode('utf-8'))
    else:
        with open(filename, 'rb') as f:
            data = f.read(1048576)
            while(data):
                md5 = hashlib.md5(data).hexdigest()
                m.update(md5.encode('utf-8'))
                data = f.read(1048576)
    return m.hexdigest()

def randintodd(min, max):
    """Returns a random odd value in the range of min to max-1."""
    int = random.randint(min,max)
    if (int % 2) == 0:
        if (int < max): int = int + 1
        else: int = int - 1
    return int

def readdir(dir):
    """Recursively collect all files in the given directory."""
    files = []
    try:
        foo = os.listdir(dir)
    except PermissionError as e:
        print(f"{str(e)}")
        return []

    for f in foo:
        if (re.match("^\.", f)): continue
        file = os.path.join(dir, f)
        if os.path.isfile(file):
            files.append(file)
        elif os.path.isdir(file):
            files = files + readdir(file)
    return files

def splitstringlen(string, maxlength, expandtabs=True):
    """Splits a string into a list of strings no more than maxlength long."""
    newstrings = []
    if (expandtabs):
        string = string.replace("\t", "    ")

    for i in range(0, len(string), maxlength):
        newstrings.append(string[i:i+maxlength])
    return newstrings

# Recursively traverse a directory and collect the total size of every file it contains.  Used to indicate
#   whether the contents of a directory have changed without incurring the high cost of md5dir().
def dirsize(filename):
    """Given a file or directory path, returns the sum if its size and everything under it, recursively."""
    size = 0
    if (os.path.isdir(filename)):
        for f in os.listdir(filename):
            size += dirsize(filename + "/" + f)
    else:
        size = os.path.getsize(filename)
    return size


