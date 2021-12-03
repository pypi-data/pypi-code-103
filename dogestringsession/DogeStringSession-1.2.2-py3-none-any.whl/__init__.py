# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from asyncio import get_event_loop
from os import name, system
from sys import exit, version_info

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

__version__ = "1.2.2"

console = Console()

DOGELOGO = f"[bold yellow]░░░░░░░░░█▐▓█░░░░░░░░█▀▄▓▌█░░░░░░\n░░░░░░░░░█▐▓▓████▄▄▄█▀▄▓▓▓▌█░░░░░\n░░░░░░░▄██▐▓▓▓▄▄▄▄▀▀▀▄▓▓▓▓▓▌█░░░░\n░░░░░▄█▀▀▄▓█▓▓▓▓▓▓▓▓▓▓▓▓▀░▓▌█░░░░\n░░░░█▀▄▓▓▓███▓▓▓███▓▓▓▄░░▄▓▐█▌░░░\n░░░█▌▓▓▓▀▀▓▓▓▓███▓▓▓▓▓▓▓▄▀▓▓▐█░░░\n░░▐█▐██▐░▄▓▓▓▓▓▀▄░▀▓▓▓▓▓▓▓▓▓▌█▌░░\n░░█▌███▓▓▓▓▓▓▓▓▐░░▄▓▓███▓▓▓▄▀▐█░░\n░▐█▐█▓▀░░▀▓▓▓▓▓▓▓▓▓██████▓▓▓▓▐█░░\n░▐▌▓▄▌▀░▀░▐▀█▄▓▓██████████▓▓▓▌█▌░\n░▐▌▓▓▓▄▄▀▀▓▓▓▀▓▓▓▓▓▓▓▓█▓█▓█▓▓▌█▌░\n░░█▐▓▓▓▓▓▓▄▄▄▓▓▓▓▓▓█▓█▓█▓█▓▓▓▐█░░\n░░░█▐▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▐█░░░[/]\n\n"


def logo(lng="-"):
    pv = str(version_info[0]) + "." + str(version_info[1])
    console.print(
        Panel(
            f"{DOGELOGO}[bold yellow]🐶 DOGE USERBOT 🐾[/]\n[bold yellow]STRINGSESSION SETUP[/]\n\n[bold white]🧩 PYTHON:[/] [bold yellow]{pv}[/]\n[bold white]🌐 LANGUAGE:[/] [bold yellow]{lng.upper()}[/]",
            border_style="bold yellow",
        ),
        justify="center",
    )


def p_lang(text):
    console.print(Panel(text, style="bold green", border_style="bold white"))


def wowask(wowask):
    return console.input(Panel(wowask, title="🦴", style="bold yellow"))


def p_ask(text):
    console.print(
        Panel(text, title="🐶", style="bold white", border_style="bold yellow")
    )


def p_info(text):
    console.print(Panel(text, style="white"))


def p_success(text):
    console.print(Panel(text, style="green", border_style="green"))


def p_important(text):
    console.print(Panel(text, style="bold cyan"))


def p_error(text):
    console.print(Panel(text, title="🚨", style="bold red", border_style="bold red"))
