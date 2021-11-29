import discord


discord.Message.__eq__ = lambda s, o: isinstance(o, discord.Message) and s.id == o.id