import os


def hide():
    os.system('setterm -cursor off')


def show():
    os.system('setterm -cursor on')
