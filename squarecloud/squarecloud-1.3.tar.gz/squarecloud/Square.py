# This code was made for SquareCloud (https://squarecloud.app) by Mudinho and NemRela.
# Imports Section
import os
import sys
from warnings import warn


# Bytes converter
def bytes_to(n: int, formatted: bool = False):
    if formatted:
        for i in ['B', 'KB', 'MB', 'GB']:
            if n < 1024.0:
                return f'{n:3.2f}{i}'
            n /= 1024.0
        return n
    return float(f'{n / 1048576:3.2f}')


# Get_bytes from a directory
def get_bytes_from(path: str) -> int:
    try:
        with open(path, 'r') as b:
            return int(b.read())
    except FileNotFoundError:
        return 0


# MB converter (SSD Function)
def megabytes_to(number: int) -> str:
    if number < 999:
        return f'{number}MB'
    else:
        return f'{str(number / 1000)[0:4] if number < 9999 else str(number / 1000)[0:5]}GB'


class Square:
    if os.name != "posix":
        warn('\n\nAtenção: Esta biblioteca pode não funcionar corretamente no seu sistema operacional.\n')

    # Returns your used ram
    @staticmethod
    def used_ram(formatted: bool = False, raw: bool = False):
        bytes: int = get_bytes_from('/sys/fs/cgroup/memory/memory.usage_in_bytes')
        return bytes if raw else bytes_to(bytes, formatted)

    # Returns your total ram
    @staticmethod
    def total_ram(formatted: bool = False, raw: bool = False):
        bytes: int = get_bytes_from('/sys/fs/cgroup/memory/memory.limit_in_bytes')
        return bytes if raw else bytes_to(bytes, formatted)

    # Return your used ram/total ram
    @staticmethod
    def ram(formatted: bool = False) -> str:
        return f'{round(Square.used_ram(raw=True) / 1024 ** 2)}/{Square.total_ram(formatted)}'

    # Returns your used SSD - Just your bot files/folders (Beta)
    @staticmethod
    def ssd():
        folder: str = sys.path[0]
        size: int = 0
        for item in os.listdir(folder):
            if os.path.isdir(f'{os.path.join(folder)}/{item}'):
                for path, dirs, files in os.walk(f'{os.path.join(folder)}/{item}'):
                    for f in files:
                        fp: str = os.path.join(path, f)
                        size += float(bytes_to(n=int(os.path.getsize(fp))))
            else:
                if not str(item) == 'start.sh':
                    size += float(bytes_to(n=int(os.path.getsize(f'{os.path.join(folder)}/{item}'))))
        return megabytes_to(int(size))


print(Square.ssd())
