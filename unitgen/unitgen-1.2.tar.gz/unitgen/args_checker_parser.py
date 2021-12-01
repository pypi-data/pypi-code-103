from sys import argv
import os

class ArgsCheckerAndParser:
    def get_files_list(self):
        if len(argv) > 1:
            if os.path.isdir(argv[1]):
                files = [os.path.join(argv[1],i) for i in  os.listdir(argv[1])]
            else:
                files =  argv[1:]

            return [file for file in files if file.lower().endswith(".py")]

    def inital_checker(self):
        self.__usage()
        self.__exists_checker()
        self.__files_checker()
    
    def __usage(self):
        if len(argv) == 1:
            print("Generate unit tests boilerplate code")
            print("Usage: ")
            print("\tunitgen <relative path to directory>")
            print("\tunitgen <file1.py> <file2.py> <file3.py> ...")
            exit(1)

    def __exists_checker(self):
        for i in range(1, len(argv)):
            if not os.path.exists(argv[i]):
                print("Error: " + argv[i] + " does not exist")
                exit(1)
        if len(argv) == 2:

            path = argv[1]
            if not os.path.exists(path):
                print("Error: " + path + " directory does not exist")
                exit(1)

            if "." not in os.path.basename(path) and not os.path.isdir(path):
                print("Error: " + path + " is not a directory")

            

    def __files_checker(self):
        if len(argv) == 2:
            path = argv[1]
            if "." not in os.path.basename(path) and not os.path.isdir(path):
                print("Error: " + path + " is not a directory")
                exit(1)

        if len(argv) > 2:
            for i in range(1, len(argv)):
                if not os.path.isfile(argv[i]):
                    print("Error: " + argv[i] + " is not a file")
                    print("You cannot combine files and directories")
                    exit(1)