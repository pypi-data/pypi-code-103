import os
import subprocess
import platform

if platform.system() == 'Windows':
    Directory = __file__.replace("\\exp.py", "")
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
else:
    Directory = __file__.replace('/exp.py', '')


def Shvar_open():
    if platform.system() == 'Windows':
        Directory = __file__.replace("\\exp.py", "")
        path = os.path.normpath(Directory)
        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])
    else:
        Directory = __file__.replace('/exp.py', '')
        print("If OS is not Window, this function is not available")
