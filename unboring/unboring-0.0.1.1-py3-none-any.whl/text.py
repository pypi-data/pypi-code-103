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
