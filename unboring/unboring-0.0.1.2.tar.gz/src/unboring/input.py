#Gets a string input until correct
def getstring(prompt="String: "):
    while True:
        try:
            string = str(input(prompt))
        except:
            pass
        return string

#Gets an integer input until corect
def getint(prompt="Integer: "):
    while True:
        try:
            integer = int(input(prompt))
        except:
            pass
        return integer
    
#Gets an boolean input until corect
def getbool(prompt="Boolean: "):
    while True:
        boolean = int(input(prompt))
        if boolean.lower() == 'true':
            return True
        elif boolean.lower() == 'false':
            return False
        else:
            pass