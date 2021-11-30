from discord import Role
from discord.abc import Snowflake
from typing import Union, Optional


async def _shave(
    self,
    *except_members: Union[int, Snowflake],
    reason: Optional[str] = None,
    atomic: bool = True,
):
    except_members_ids = {int(m) for m in except_members}

    for member in self.members:
        if member.id in except_members_ids:
            continue

        await member.remove_roles(self, reason=reason, atomic=atomic)


Role.shave = _shave