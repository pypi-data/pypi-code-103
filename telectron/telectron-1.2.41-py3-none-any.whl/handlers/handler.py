#  telectron - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2021 Dan <https://github.com/delivrance>
#
#  This file is part of telectron.
#
#  telectron is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  telectron is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with telectron.  If not, see <http://www.gnu.org/licenses/>.

import inspect
from typing import Callable

import telectron
from telectron.filters import Filter
from telectron.types import Update


class Handler:
    def __init__(self, callback: Callable, filters: Filter = None):
        self.callback = callback
        self.filters = filters

    async def check(self, client: "telectron.Client", update: Update):
        return await self.execute_filters(self.filters, client, update)

    @staticmethod
    async def execute_filters(filters, client, update):
        if callable(filters):
            if inspect.iscoroutinefunction(filters.__call__):
                return await filters(client, update)
            else:
                return await client.loop.run_in_executor(
                    client.executor,
                    filters,
                    client, update
                )
        return True

    @classmethod
    async def use_result(cls, client, update, result):
        pass
