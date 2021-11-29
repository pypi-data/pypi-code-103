from discord_api import Client, Command

client = Client(log = False)

@client.event
async def on_ready():
    print("ready")
    
client.run("ToKeN")