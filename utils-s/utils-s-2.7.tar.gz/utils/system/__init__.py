import signal
import subprocess
import os
from . import paths

def HomeDirectory():
    return os.path.expanduser('~')

def command(args: list, quite=False, read=False):
    if quite:
        sub = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    elif read:
        sub = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

        response = sub.communicate()[0].decode('utf8')
        sub.wait()
        sub.poll()
        returnCode = int(sub.returncode)

        return response, returnCode, sub
    else:
        sub = subprocess.Popen(args)

    sub.wait()
    sub.kill()
    sub.terminate()

def ip_address(interface='en0'):
    ip = command(['ipconfig', 'getifaddr', interface], read=True)
    try:
        ip = ip[0].removesuffix('\n')
    except AttributeError or Exception:
        if ip[0].endswith('\n'):
            ip = ip[0][:-1]

    return ip

def hostname():
    import socket
    return socket.gethostname()

def remove(file):
    command(['rm', '-rf', file])

def kill_process(pid):
    if not isinstance(pid, int):
        pid = int(pid)
    os.kill(pid, signal.SIGTERM)



if __name__ == '__main__':
    pass
