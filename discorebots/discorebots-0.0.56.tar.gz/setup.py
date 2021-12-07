import setuptools
long_description = """# About

Module to create discord bots its easy!

#Example

```py
from discorebots import setupBot

bot = setupBot(
prefix=".", #provide your bot prefix
intents=True, #discord intents (if True pls enable intents in discordapp.com/developers/applications in your application bot)
sharding=True, #if you want sharding guilds
shardsAmount=2 #shards count
)

bot.onWebsocketResponse("Bot is ready to use!") #log ready
bot.onClientMessage() #acess bot messages

bot.addCommand(
name = "ping",
code = "Pong! $pingms"
)

bot.addCommand(
name = "uptime",
code = "Uptime: $uptime"
)

bot.start("token")
```
"""


setuptools.setup(
    name="discorebots", # Put your username here!
    version=f"0.0.56", # The version of your package!
    author="SScefaLI", # Your name here!
    author_email="birka11@list.ru", # Your e-mail here!
    description="Package to create discord bots its easy!", # A short description here!
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="", # Link your package website here! (most commonly a GitHub repo)
    packages=setuptools.find_packages(), # A list of all packages for Python to distribute!
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'discord', 'requests'
    ], # Enter meta data into the classifiers list!
    python_requires='>=3.8', # The version requirement for Python to run your package!
)