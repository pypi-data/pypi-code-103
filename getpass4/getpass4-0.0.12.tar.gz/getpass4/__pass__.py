import caugetch as getch
def __getpass__(prompt: str, char=('*'), mnbe: bool = False, __r_qwaf4__: bool = False):
    #mnbe = may not be empty
    mod_ = []
    from getpass4.__output__ import coded, decoded
    if not isinstance(char,tuple) and isinstance(char,str):
        char = (char)
    for an_ch in char:
        if len(str(an_ch)) > 1:
            raise(Exception('"chars in char must be strings with 1 character of length"!'))
    from random import randint
    one_char = ''
    print(prompt, end='', flush=True)
    buf = ''
    do = 1
    written = 0
    muk2 = ''
    muk = 0
    control1 = ('\\x18', '\\x03', '\\x16')
    control2 = ('X', 'C', 'V')
    char_group = []
    nexts_chs = []
    amb = ''
    __qwaf4__ = False
    while True:
        meem = False
        oof = True
        del_ = False
        dame = 0
        from random import randint; one_char = char[randint(0,len(char)-1)]; del randint;
        if len(nexts_chs) == 0:
            ch = getch.getch()
        elif len(nexts_chs) > -1:
            ch = nexts_chs[0]
            nexts_chs.pop(0)
        ch_backup = mega = str([ch])
        
        # printa
        
        #print(f'{ch_backup}', end='', flush=True)
        
        if 'xe0' in mega or 'x00' in mega:
            mega = True
        else:
            mega = False
        #print(muk)
        
        def __delete__(buf):
            """This function requires the variable "buf" and returns buf, written, and char_group!"""
            print('\r', end='', flush=True)
            print(prompt, end='', flush=True)
            print(' ' * (len(buf)), end='', flush=True)
            print('\b' * (len(buf)), end='', flush=True)
            buf = ''; written = 0;
            return buf, written, []


        if '\\x' in ch_backup:
            if mega:
                muk = 1
                if 'x00' in ch_backup:
                    muk2 = 'x00'
                elif 'xe0' in ch_backup:
                    muk2 = 'xe0' 
            else:
                for i, ctrl_coded in enumerate(control1):
                    if ctrl_coded in ch_backup:
                        from clipboard import copy as clpbCopy; from clipboard import paste as clpbPaste;
                        if control2[i] == 'X' and len(buf) >= 1: #if Ctrl + X was pressed
                            clpbCopy(str(buf))
                            buf, written, char_group = __delete__(buf)
                        elif control2[i] == 'C' and len(buf) >= 1: #if Ctrl + C was pressed
                            clpbCopy(str(buf))
                        elif control2[i] == 'V': #if Ctrl + V was pressed
                            nexts_chs = list(str(clpbPaste()))
                        
                            


        #print([ch], end='',flush=True)
        if do > 0:
            do -= 1
        if True: #print(str(ch).replace("b'","'"),end='',flush=True)
            for i, char_ in enumerate(coded):
                if mega:
                    decoded.append('')
                    i = -1
                if char_ in str(ch).replace("b'","'") or mega:
                    buf += f'{decoded[i]}'
                    print(f'{decoded[i]}', end='', flush=True)
                    written += 1
                    dame = 1
                    ch = ''
                    break
                elif '\\x' in str(ch).replace("b'","'"):
                    #buf += f'{decoded[i]}'
                    #print(f'{decoded[i]}', end='', flush=True)
                    #written += 1
                    dame = 1
                    ch = ''
        if dame == 0:
            try:
                if oof:
                    ch = ch.decode('utf-8')
            except UnicodeDecodeError:
                ch = ''
                do = 2
            except AttributeError as __error___:
                if isinstance(ch, str):
                    pass
                else:
                    raise(__error___)
            if "\\x" in str([ch]) and str([ch]) != "['\\x08']":
                ch = ''
                do = 2
                dame = 2
        
        if ch == '\r' and do == 0: #if Enter was pressed
            __delete__(buf)
            print(''.join(char_group),end='', flush=True)
            #print('')
            if len(buf) == 0:
                print('\r' + prompt, end='', flush=True)
                print('@empty_password', end='', flush=True)
                from colorama import init, Fore, Back, Style;init(convert=True)
                print('\r' + prompt + Fore.LIGHTYELLOW_EX + '@empty_password' + Fore.RESET, flush=True)
                if mnbe:
                    passk = prompt[::-1]; passk = passk[passk.find(':'):]; passk = passk[::-1];
                    if passk.endswith(':'): passk = passk[:-1];
                    if passk.strip() == '': passk = 'password';
                    from colorama import init, Fore, Back, Style;init(convert=True)
                    print('\n' + Fore.RED + f'ERROR: "The {passk} may not be empty"!\n' + Fore.RESET + Back.RESET + Style.RESET_ALL, flush=True)
                    #print(prompt, end='', flush=True)
                    bub = __getpass__(prompt, char, True, __r_qwaf4__=True)
                    #print(bub,flush=True)
                    if len(bub) == 2 and bub[1]:
                        if not __r_qwaf4__:
                            __delete__(buf)
                            print('@quitted_with_alt+f4', end='', flush=True)
                            print('\r' + prompt, end='', flush=True)
                            from colorama import init, Fore, Back, Style;init(convert=True)
                            print(Fore.LIGHTYELLOW_EX + '@quitted_with_alt+f4' + Fore.RESET, flush=True)
                        muk2 = ''
                        __qwaf4__ = True
                        break
                    #print('AEWQ', flush=True)
                    amb = bub[0]
                    break

                else:
                    print('\n', flush=True)
                    break
            else:
                print('\n', flush=True)
                break
        else:
            if ch_backup == "[b'\\x08']": # if ch is backspace
                if written > 0:
                    print('\b', end=' ', flush=True)
                    print('\b', end='', flush=True)
                    buf = buf[:-1]
                    written -= 1
                    char_group.pop()
            elif do == 0:
                #print(mega)
                if dame == 0:
                    meem = True
            else:
                pass
                #print('\b', end='', flush=True)
                #buf = f'{buf}\b'
            if mega:
                if written == 0:
                    print('\b ', end='\b', flush=True)
                    mod_.append(len(buf))
            
            if dame == 0:
                #print(muk)
                if muk == 0:
                    buf += ch
                    print(f'{one_char}', end='', flush=True)
                    written += 1
                    char_group.append(one_char)
                else:
                    if written == 0:
                        print(' ', end='', flush=True)
                    elif str(ch_backup) == "[b'S']" and muk2 == 'xe0':
                        buf, written, char_group = __delete__(buf)
                        muk2 = ''
                    elif str(ch_backup) == "[b'k']" and muk2 == 'x00':
                        if not __r_qwaf4__:
                            buf, written, char_group = __delete__(buf)
                            print('@quitted_with_alt+f4', end='', flush=True)
                            print('\r' + prompt, end='', flush=True)
                            from colorama import init, Fore, Back, Style;init(convert=True)
                            print(Fore.LIGHTYELLOW_EX + '@quitted_with_alt+f4' + Fore.RESET, flush=True)
                        muk2 = ''
                        __qwaf4__ = True
                        break
                    muk -= 1
                    

    mod_ = [x for x in mod_ if x != 0]
    if isinstance(amb, str):
        for i, chm in enumerate(buf):
            if not i in mod_ and isinstance(chm, str):
                amb += chm
    if __r_qwaf4__:
        amb = (amb, __qwaf4__)
    return amb
"""
password = __getpass__('password: ',  mnbe=True)

print('\n"', end='')
print(password, end='')
print('"')
input() # Esse input é para a o arquivo py não fechar sozinho antes de apertar ENTER
"""
