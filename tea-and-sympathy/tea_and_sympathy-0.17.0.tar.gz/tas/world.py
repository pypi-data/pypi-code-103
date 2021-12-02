#!/usr/bin/env python3
# encoding: utf-8

# This is a technical demo and teaching example for the turberfield-catchphrase library.
# Copyright (C) 2021 D E Haynes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import bisect
from collections import Counter
from collections import defaultdict
from collections import namedtuple
import functools
import itertools
import random
import re
import textwrap

from balladeer import Article
from balladeer import Fruition
from balladeer import Gesture
from balladeer import Grouping
from balladeer import Head
from balladeer import Name
from balladeer import Phrase
from balladeer import Pronoun
from balladeer import Verb
from balladeer import World

from tas.types import Availability
from tas.types import Character
from tas.types import Container
from tas.types import Location
from tas.types import Motivation


class Tea(World):

    @functools.cached_property
    def player(self):
        return next(
            i for s in self.lookup.values() for i in s
            if i.get_state(Motivation) == Motivation.player
        )

    @property
    def local(self):
        reach = (self.player.location, Location.inventory)
        grouped = self.arrange(i for i in self.lookup.each if i.get_state(Location) in reach)
        return Grouping(list, {k.__name__: v for k, v in grouped.items()})

    @property
    def fruition(self):
        rv = Grouping(list)
        for g in self.visible["Gesture"]:
            rv[g.get_state(Fruition).name].append(g)
        return rv

    @property
    def visible(self):
        return Grouping(
            list,
            {k: [i for i in v if i.get_state(Availability) != Availability.removed]
             for k, v in self.local.items()
        })

    def build(self):
        return [
            Container(
                names=[Name("Mug")],
                description=textwrap.dedent(
                    """
                    A pale blue mug. It has on it a cartoon Teddy Bear
                    and the slogan 'I Fly Luton'.

                    It is dusted with ash. Inside are several cigarette butts.
                    They are crushed and soggy.

                    One however is almost pristine.
                    Only slightly charred and no trace of any lipstick.
                    
                    """,
                ),
            ).set_state(Location.bedroom, Availability.allowed),
            Container(
                names=[Name("Kettle")],
                description=textwrap.dedent(
                    """
                    A battered old kettle.

                    """,
                ),
            ).set_state(20, Location.kitchen, Availability.fixture),
            Character(
                names=[Name("Sophie", Article("", ""), Pronoun("she", "her", "herself", "hers"))],
                description="{0.name} came here from Berkshire. She goes to Art College."
            ).set_state(Motivation.acting, Location.kitchen),
            Character(
                names=[Name("Louise", Article("", ""), Pronoun("she", "her", "herself", "hers"))],
                description="{0.name} is a young woman from Manchester. She works as a nurse."
            ).set_state(Motivation.player, Location.bedroom),
            Gesture(
                "make tea",
                head=Head(
                    propose=[
                        Phrase(
                            Verb("make"),
                            Name("tea", Article("the", ""))
                        )
                    ]
                )
            ).set_state(
                Location.kitchen,
                Availability.removed,
                Fruition.inception
            ),
            Gesture(
                "smoke cigarette",
                head=Head(
                    propose=[
                        Phrase(
                            Verb("smoke", progressive="is smoking", perfect="smoked"),
                            Name("cigarette")
                        )
                    ]
                )
            ).set_state(
                Location.kitchen,
                Availability.removed,
                Fruition.inception
            ),
        ]
