# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from json import loads
from os.path import dirname, join, realpath

from . import Panel, Prompt, logo, name, p_ask, p_lang, system

languages_folder = join(dirname(realpath(__file__)), "languages")


def importlanguages():
    if name == "nt":
        system("cls")
    else:
        system("clear")
    logo()

    p_lang(f"[1] [bold red]TÜRK[/][bold white]ÇE")
    p_lang(f"[2] [bold blue]ENG[/][bold white]LI[/][bold red]SH")

    p_ask(
        Panel(
            f"\n[bold yellow]🦴 Please write a language number:\n\n[bold yellow]🦴 Lütfen bir dil numarası yazın:\n"
        )
    )

    lng = Prompt.ask(f"🌍", choices=["1", "2"], default="1")

    if lng == "1":
        DOGELANG = "tr"

    elif lng == "2":
        DOGELANG = "en"

    return DOGELANG


DOGELANG = importlanguages()

LAN = loads(open(f"{languages_folder}/{DOGELANG}.json.py", "r").read())["STRINGS"]
