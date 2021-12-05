import random as rd

def txtcolor(*, text: str, color: str = "", start_index: int = 0,
    stop_index: int = 0, random: bool = False, bold: bool = False) -> str:

    if not stop_index:
        stop_index = len(text)

    if bold == True:
        bold_num = "1"
    else:
        bold_num = "0"

    name_to_number = {
        "grey"  : "30",
        "red"    : "31",
        "green"  : "32",
        "yellow" : "33",
        "blue"   : "34",
        "purple" : "35",
        "cyan"   : "36",
        "white"  : "37",
    }

    def return_colored(color_num: str, text: str) -> str:
        return text[:start_index] + f"\x1b[{bold_num};{color_num};40m{text[start_index:stop_index]}\x1b[0m" + text[stop_index:]

    if random == True:
        randomified = ""
        for i in text:
            randomified += return_colored(str(rd.randint(30, 37)), i)
        return randomified

    try:
        return return_colored(name_to_number[color], text)
    except KeyError:
        raise KeyError(f"You need to either specify a valid color or set random to True.")

def bgcolor(*, text: str, color: str = "", start_index: int = 0, stop_index: int = 0, random: bool = False) -> str:

    if not stop_index:
        stop_index = len(text)

    name_to_number = {
        "grey"  : "30",
        "red"    : "31",
        "green"  : "32",
        "yellow" : "33",
        "blue"   : "34",
        "purple" : "35",
        "cyan"   : "36",
        "white"  : "37",
    }

    def return_colored(color_num: str, text: str) -> str:
        return text[:start_index] + f"\x1b[7;{color_num};40m{text[start_index:stop_index]}\x1b[0m" + text[stop_index:]

    if random == True:
        randomified = ""
        for i in text:
            randomified += return_colored(str(rd.randint(30, 37)), i)
        return randomified

    try:
        return return_colored(name_to_number[color], text)
    except KeyError:
        raise KeyError(f"You need to either specify a valid color or set random to True.")

def complrandom(*, text: str, start_index: int = 0, stop_index: int = 0) -> str:
    if not stop_index:
        stop_index = len(text)

    def return_colored(color_num: str, text: str, type_num: str) -> str:
        return text[:start_index] + f"\x1b[{type_num};{color_num};40m{text[start_index:stop_index]}\x1b[0m" + text[stop_index:]

    try:
        randomified = ""
        for i in text:
            type_num = str(rd.choice((0, 1, 7)))
            color_num = str(rd.randint(30, 37))
            randomified += return_colored(color_num, i, type_num)
        return randomified
    except KeyError:
        raise KeyError(f"You need to either specify a valid color or set random to True.")