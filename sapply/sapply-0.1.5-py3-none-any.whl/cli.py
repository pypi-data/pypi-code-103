from sapply.cmapdefs import cmapdefs
from sapply.charmap import read_charmap
from sapply.flip import flip
from sapply.zalgo import zalgo
from sapply.morse import to_morse
import pathlib
from signal import signal, SIGPIPE, SIG_DFL
import sys
import site

signal(SIGPIPE, SIG_DFL)

MAJOR, MINOR, PATCH = '0', '1', '0'

def convert(char_map, text):
    out = ""
    for char in text:
        if char in char_map:
            out += char_map[char]
        elif char.lower() in char_map:
            out += char_map[char.lower()]
        else:
            out += char
    return out

def strikethrough(text, strikeover):
    return ''.join([char + strikeover for char in text])

def optmatch(cmd, short, long=''):
    if (long == ''):
        return (cmd == short)
    else:
        return (cmd == short or cmd == long)

def mapto(cmap: str):
    file = cmapdefs[cmap]
    root    = pathlib.Path(f'{site.getsitepackages()}/sapply')
    local   = pathlib.Path(f'{site.getusersitepackages()}/sapply')
    path = ''
    if (root.is_dir()):
        path = pathlib.Path(f'{root}/resources/{file}').expanduser()
    else:
        path = pathlib.Path(f'{local}/resources/{file}').expanduser()
    return (read_charmap(path))

def main():
    cmds = ['flip', 'zalgo', 'morse']

    subcmd = None
    text = None
    effects = None

    for cmd in cmds:
        if cmd in sys.argv:
            subcmd = cmd

    if subcmd is None:
        text = sys.argv[1]
        effects = sys.argv[2:]
    else:
        text    = sys.argv[2]
        effects = sys.argv[3:]

    if not text:
        sys.exit()

    # Subcommands
    # Add subargs for each of these commands
    # Pass args parameter and parse commands in each function
    if (subcmd == 'flip'):
        flip(text)
    if (subcmd == 'zalgo'):
        zalgo(text)
    if (subcmd == 'morse'):
        print(to_morse(text.upper()))
    if (subcmd is not None):
        return

    # Main
    out = ""
    if(len(effects) < 2):
        cmd = effects[0]
        if (optmatch(cmd, '--sub')):
            out = convert(mapto('subscript'), text)
        if (optmatch(cmd, '--super')):
            out = convert(mapto('superscript'), text)
        if (optmatch(cmd, '-ds', '--doublestruck')):
            out = convert(mapto('doubleStruck'), text)
        if (optmatch(cmd, '-oe', '--oldeng')):
            out = convert(mapto('oldEnglish'), text)
        if (optmatch(cmd, '-med', '--medieval')):
            out = convert(mapto('medieval'), text)
        if (optmatch(cmd, '-mono', '--monospace')):
            out = convert(mapto('monospace'), text)
        if (optmatch(cmd, '-b', '--bold')):
            out = convert(mapto('bold'), text)
        if (optmatch(cmd, '-i', '--italics')):
            out = convert(mapto('italic'), text)
    elif(len(effects) < 3):
        cmd = effects[0]
        opt = effects[1]
        # Handle combinable effects
        if (optmatch(cmd, '--cmap')):
            opt = effects[1]
            cmap = read_charmap(opt)
            out = convert(cmap, text)
        if (optmatch(cmd, '-b', '--bold') and optmatch(opt, '-s', '--sans')):
            out = convert(mapto('boldSans'), text)
        if (optmatch(cmd, '-i', '--italics') and optmatch(opt, '-b', '--bold')):
            out = convert(mapto('boldItalic'), text)
        if (optmatch(cmd, '-i', '--italics') and optmatch(opt, '-s', '--sans')):
            out = convert(mapto('italicSans'), text)
        if (optmatch(cmd, '-st', '--strike') and optmatch(opt, '-')):
            out = strikethrough(text, u'\u0336')
        if (optmatch(cmd, '-st', '--strike') and optmatch(opt, '~')):
            out = strikethrough(text, u'\u0334')
    print(out)
