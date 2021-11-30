"""
pycord.features.shell
~~~~~~~~~~~~~~~~~~~~~~~~

The pycord shell commands.

:copyright: (c) 2021 Devon (Gorialis) R
:license: MIT, see LICENSE for more details.

"""

from discord.ext import commands

from pycord.codeblocks import Codeblock, codeblock_converter
from pycord.exception_handling import ReplResponseReactor
from pycord.features.baseclass import Feature
from pycord.paginators import PaginatorInterface, WrappedPaginator
from pycord.shell import ShellReader


class ShellFeature(Feature):
    """
    Feature containing the shell-related commands
    """

    @Feature.Command(
        parent="pyc",
        name="shell",
        aliases=["bash", "sh", "powershell", "ps1", "ps", "cmd"],
    )
    async def pyc_shell(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Executes statements in the system shell.

        This uses the system shell as defined in $SHELL, or `/bin/bash` otherwise.
        Execution can be cancelled by closing the paginator.
        """

        async with ReplResponseReactor(ctx.message):
            with self.submit(ctx):
                with ShellReader(argument.content) as reader:
                    prefix = "```" + reader.highlight

                    paginator = WrappedPaginator(prefix=prefix, max_size=1975)
                    paginator.add_line(f"{reader.ps1} {argument.content}\n")

                    interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
                    self.bot.loop.create_task(interface.send_to(ctx))

                    async for line in reader:
                        if interface.closed:
                            return
                        await interface.add_line(line)

                await interface.add_line(f"\n[status] Return code {reader.close_code}")

    @Feature.Command(parent="pyc", name="git")
    async def pyc_git(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Shortcut for 'pyc sh git'. Invokes the system shell.
        """

        return await ctx.invoke(
            self.pyc_shell,
            argument=Codeblock(argument.language, "git " + argument.content),
        )

    @Feature.Command(parent="pyc", name="pip")
    async def pyc_pip(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Shortcut for 'pyc sh pip'. Invokes the system shell.
        """

        return await ctx.invoke(
            self.pyc_shell,
            argument=Codeblock(argument.language, "pip " + argument.content),
        )
