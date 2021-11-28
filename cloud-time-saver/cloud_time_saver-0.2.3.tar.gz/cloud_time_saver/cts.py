#!/usr/bin/env python3
from subprocess import call
import os
import logging
import subprocess
from colorama import Fore
import sys

def main():
    try:
        print('Welcome user.')
        print(Fore.BLUE , 'THIS SOFTWARE WILL ENABLE YOU TO CONTROL YOUR AWS SERVICES WHILE NOT LEAVING YOUR TERMINAL.\n\n')
        print(Fore.RED , '------------------------------------------------------ATTENTION!------------------------------------------------------')
        print(' PLEASE MAKE YOU CONFIGURED YOUR AWS ACCOUNT ON YOUR SYSTEM, AND BE SURE TO FOLLOW INSTRUCTIONS FROM SOFTWARE STICTLY')
        print(Fore.MAGENTA,'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        pick = input('To run the program type RUN,If you want to see list of all commands you can run enter help, and if you want to exit \n enter exit: ')
    
    
        cwd = (os.path.dirname(os.path.realpath(__file__)))
        os.chdir(cwd + '/app')
        if pick == 'run':
            print(Fore.RED,'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print(' IF YOU ENTER COMMAND THAT DOES NOT EXISTS PROGRAM WILL AUTOMATICLY EXIT !!!')
            command = input(" Please enter full, and correct name of command you want to run : ")
            print(Fore.WHITE ,'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            call(["python3" , "main.py" , "find_and_run_plugins" , command])

        elif pick == 'help':
            call(["python3" , "main.py" , "cheat_sheat"])
        elif pick == 'exit':
            sys.exit()
        else:
            print('YOU ENTERED THE UNEXPECTED VALUE!')
            raise(TypeError)
        
    except subprocess.SubprocessError as e:
        logging.exception(e)

main()

