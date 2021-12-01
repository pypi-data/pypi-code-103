from sys import argv
from inspect import cleandoc

code = """
from discord_api import Client, Command

client = Client(log = False)

@client.event
async def on_ready():
    print("ready")
    
client.run("ToKeN")
"""

def main():
    arg = argv[1:]
    cmd = arg[0]
    if cmd == "setup":
        filename = arg[1]
        print("\rNow setup...", end = "")
        with open(filename + ".py", "w") as f:
            f.write(cleandoc(code))
        print("\rSetup is finish", end = "")
    else:
        print("404 Not found error.")
