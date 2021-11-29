from discord.ext import commands


async def dispatch_error(self, ctx, error):
    ctx.command_failed = True
    cog = self.cog

    try:
        coro = self.on_error
    except AttributeError:
        pass
    else:
        injected = commands.core.wrap_callback(coro)

        if cog is not None:
            await injected(cog, ctx, error)
        else:
            await injected(ctx, error)

    try:
        coro = self.root_parent.on_error
    except AttributeError:
        pass
    else:
        injected = commands.core.wrap_callback(coro)

        if cog is not None:
            await injected(cog, ctx, error)
        else:
            await injected(ctx, error)

    try:
        if cog is not None:
            local = commands.Cog._get_overridden_method(cog.cog_command_error)
            if local is not None:
                wrapped = commands.core.wrap_callback(local)
                await wrapped(ctx, error)
    finally:
        ctx.bot.dispatch("command_error", ctx, error)


commands.Command.dispatch_error = dispatch_error