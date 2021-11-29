from discord.ext import commands



async def invoke(self, ctx):
    await self.prepare(ctx)

    ctx.invoked_subcommand = None
    injected = commands.core.hooked_wrapped_callback(self, ctx, self.callback)

    ret = await injected(*ctx.args, **ctx.kwargs)
    if ret is not None:
        await ctx.send(ret)


commands.Command.invoke = invoke