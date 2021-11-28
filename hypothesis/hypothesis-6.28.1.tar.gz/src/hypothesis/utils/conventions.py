# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Most of this work is copyright (C) 2013-2021 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
# END HEADER


class UniqueIdentifier:
    """A factory for sentinel objects with nice reprs."""

    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return self.identifier


class InferType(UniqueIdentifier):
    """We have a subclass for `infer` so we can type-hint public APIs."""


infer = InferType("infer")
not_set = UniqueIdentifier("not_set")
