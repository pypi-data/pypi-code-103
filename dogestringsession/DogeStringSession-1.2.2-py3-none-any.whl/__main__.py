# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from . import *
from .language import DOGELANG, LAN
from .session import sessiongenerator

LAN = LAN["SESSION"]

logo(DOGELANG)
if name == "nt":
    system("cls")
else:
    system("clear")
logo(DOGELANG)

SS, C = sessiongenerator()

if name == "nt":
    system("cls")
else:
    system("clear")
logo(DOGELANG)

p_success(
    f"[bold cyan]🚧 {LAN['BECAREFUL']}![/]\n\n[bold green]🧡 {LAN['STRINGSESSION_BELOW']}:[/]"
)
print("\n\n")
print(SS)


async def sendmsg():
    await C.send_message(
        "me",
        f"**🐶 {LAN['DOGE_ME_MSG']}**\n\n⏩ `STRING_SESSION`: `{SS}`\n\n\n**🚧 {LAN['BECAREFUL']}!**",
    )


(get_event_loop()).run_until_complete(sendmsg())
