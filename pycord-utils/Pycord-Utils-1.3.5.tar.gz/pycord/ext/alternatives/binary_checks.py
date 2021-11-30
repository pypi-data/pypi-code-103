import inspect

from discord.ext import commands
from ._common import py_allow


py_allow(3, 9, 0)


class CheckDecorator:
    def __init__(self, predicate):
        self.predicate = predicate
        self.check = Only(Check(predicate))

    def __call__(self, func):
        if isinstance(func, commands.Command):
            func.checks.append(self.check)
        else:
            if not hasattr(func, "__commands_checks__"):
                func.__commands_checks__ = []

            func.__commands_checks__.append(self.check)

        return func

    def __repr__(self):
        return f"CheckDecorator<check={self.check!r}>"

    def __invert__(self):
        ~self.check.first
        return self.check

    def __or__(self, other):
        self.check.first = Either(
            self.check.first, other.check.first if isinstance(other, CheckDecorator) else other
        )
        return self.check

    def __and__(self, other):
        self.check.first = Both(
            self.check.first, other.check.first if isinstance(other, CheckDecorator) else other
        )
        return self.check


class Check:
    def __init__(self, predicate):
        self.predicate = predicate
        self.inverted = False

    def __repr__(self):
        return f"Check(predicate={self.predicate!r}, inverted={self.inverted})"

    async def __call__(self, *args, **kwargs):
        r = self.predicate(*args, **kwargs)
        if isinstance(r, bool):
            r = r
        else:
            r = await r

        if self.inverted:
            r = not r

        return r

    def __invert__(self):
        self.inverted = not self.inverted
        return self

    def __or__(self, other):
        return Either(self.predicate, other if isinstance(other, CheckOp) else other.predicate)

    def __and__(self, other):
        return Both(self.predicate, other if isinstance(other, CheckOp) else other.predicate)


commands.core.check = CheckDecorator
commands.check = CheckDecorator


class Only:
    def __init__(self, first: Check):
        self.first = first
        self.inverted = False

    def _call(self, *args, **kwargs):
        return self.first(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if isinstance(args[0], commands.Command):
            args[0].checks.append(self)
            return args[0]
        else:
            return self._call(*args, **kwargs)

    def __repr__(self):
        return f"Only(first={self.first!r})"

    def __invert__(self):
        self.inverted = not self.inverted
        return self

    def __or__(self, other):
        return Either(self, other)

    def __and__(self, other):
        return Both(self, other)


class CheckOp:
    def __init__(self, first: Check, second: Check):
        self.first = first
        self.second = second
        self.inverted = False
        self.check = self

    def __repr__(self):
        return f"{self.__class__.__name__}(first={self.first!r}, second={self.second!r}, inverted={self.inverted})"

    async def _try_single(self, callback, *args, **kwargs):
        r = await callback(*args, **kwargs)

        return not r if self.inverted else r

    async def _try_call(self, *args, **kwargs):
        return await self._try_single(self.first, *args, **kwargs), await self._try_single(
            self.second, *args, **kwargs
        )

    def __invert__(self):
        self.inverted = not self.inverted
        return self

    def __or__(self, other):
        return Either(self, other)

    def __and__(self, other):
        return Both(self, other)

    async def _call(self, *args, **kwargs):
        ...

    def __call__(self, *args, **kwargs):
        if isinstance(args[0], commands.Command):
            args[0].checks.append(self)
            return args[0]
        else:
            return self._call(*args, **kwargs)


class Both(CheckOp):
    async def _call(self, *args, **kwargs):
        fs, ss = await self._try_call(*args, **kwargs)
        return fs and ss


class Either(CheckOp):
    async def _call(self, *args, **kwargs):
        try:
            if await self._try_single(self.first, *args, **kwargs):
                return True
        except:
            pass

        try:
            if await self._try_single(self.second, *args, **kwargs):
                return True
        except:
            pass

        return False