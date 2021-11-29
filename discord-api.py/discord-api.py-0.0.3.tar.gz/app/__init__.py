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
    filename = arg[0]
    a = print("Now setup...")
    with open(filename + ".py", "w") as f:
        f.write(cleandoc(code))
    print("Setup is finish.")