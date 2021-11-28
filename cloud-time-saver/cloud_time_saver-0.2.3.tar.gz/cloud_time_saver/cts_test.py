#!/usr/bin/env python3
from subprocess import call
import os
import logging
import subprocess
import sys

def main():
    pick = input('To run the program type RUN,If you want to see list of all commands you can run enter help, and if you want to exit \n enter exit: ')
    
    
    cwd1 = (os.path.dirname(os.path.realpath(__file__)))
    os.system('cd ..')
    cwd2 = os.getcwd()
    os.chdir(cwd2 + '/cloud_time_saver/app')
    if pick == 'run':
        command = input(" Please enter full, and correct name of command you want to run : ")
        call(["python3" , "main.py" , "find_and_run_plugins" , command])

    elif pick == 'help':
        call(["python3" , "main.py" , "cheat_sheat"])
    elif pick == 'exit':
        sys.exit()
    else:
        raise(TypeError)
        
if __name__=='__main__':
    main()