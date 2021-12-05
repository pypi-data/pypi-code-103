import time

#Writes to file
def writeFile(path, text):
    file = open(path, "w")
    file.write(text)
    file.close()

#Appends to file
def appendFile(path, text):
    file = open(path, "a")
    file.write(text)
    file.close()

#Prints with no new lines
def printn(text):
    print(text, end="")
    
#Prints letter by letter
def lbl(text, speed=0.1):
    for x in range(0,len(text)):
        print(text[x], end="")
        time.sleep(speed)
    print()
