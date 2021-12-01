def search(thing) -> 'If thing is a string type, return the unicode number of it     If thing is a int type, return the corresponding character of it':
    if type(thing) == type(''):
        return ord(thing)
    elif type(thing) == type(1):
        return chr(thing)

def table(items, cols, add_numbers=False):
    rows = items // cols
    table = list('' for x in range(rows+1))
    char = 1
    for col in range(1, cols + 1):
        for row in range(1, rows+1):
            if add_numbers == True:
                table[row] += '{:3.0f}'.format(char) + ' '
            if add_numbers == False:
                table[row] += chr(char)
            else:
                table[row] += ' ' + chr(char)
            char += 1
    return table

def listcode(items, add_numbers=False):
    table = []
    char = 1
    for x in range(1, items + 1):
        if add_numbers == True:
            table.append('{:3.0f}'.format(char) + ' ')
        if add_numbers != True:
            table.append(chr(char))
        else:
            table[-1] += chr(char)
        char += 1
    return table
