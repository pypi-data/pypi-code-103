from discord.ext import commands


def send_help(self, message, *args, **kwargs):
    ctx = kwargs.get("cls", commands.Context)(prefix=self.user.mention, bot=self, message=message)
    return ctx.send_help(*args)


commands.bot.BotBase.send_help = send_help