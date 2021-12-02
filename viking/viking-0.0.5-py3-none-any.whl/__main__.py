from simulate import main as simulate
from translate import main as translate

# CLI for Viking
# Basicly Imports __init__ and controls it all
# Made by Owen Shaule

def front():
    front = """
    {}██╗░░░██╗{}██╗██╗░░██╗██╗███╗░░██╗░██████╗░
    {}██║░░░██║{}██║██║░██╔╝██║████╗░██║██╔════╝░
    {}╚██╗░██╔╝{}██║█████═╝░██║██╔██╗██║██║░░██╗░
    {}░╚████╔╝{}░██║██╔═██╗░██║██║╚████║██║░░╚██╗
    {}░░╚██╔╝{}░░██║██║░╚██╗██║██║░╚███║╚██████╔╝
    {}░░░╚═╝{}░░░╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝░╚═════╝░
    {}{}Instruction System translator for 2D CSV
    {}{}{}Experimental | Do not currently use with decimals 

    """
    for i in front.splitlines():
        print(i.format("\u001b[36m", "\u001b[34m", "\u001b[1m\u001b[31m"))

print("{}(1) Translate   CSV --> Viking Instruction".format("\u001b[34m", "\u001b[0m"), end="\n")
print("{}(2) Simulate Viking Instruction".format("\u001b[34m", "\u001b[0m"), end="\n")


inp = input("{}{}>>> ".format("\u001b[34m", "\u001b[0m"))

if inp.startswith("1"): 
    translate()
elif inp.startswith("2"): 
    simulate()