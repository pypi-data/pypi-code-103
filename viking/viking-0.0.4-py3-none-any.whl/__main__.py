from viking import *

front()

print("{}(1) Translate   CSV --> Viking Instruction".format("\u001b[34m", "\u001b[0m"), end="\n")

inp = input("{}{}>>> ".format("\u001b[34m", "\u001b[0m"))

if inp.startswith("1"): 
    main()