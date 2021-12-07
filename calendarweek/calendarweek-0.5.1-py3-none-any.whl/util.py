# Copyright 2019, 2020 Dominik George <dominik.george@teckids.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from locale import getpreferredencoding, locale_alias, locale_encoding_alias
from typing import Optional


def normalise_locale(loc: str, enc: Optional[str] = None) -> str:
    loc = locale_alias.get(loc, loc) or ""
    if loc:
        if enc:
            enc = locale_encoding_alias.get(enc.replace("-", ""), enc)
        else:
            enc = getpreferredencoding()
        loc = loc.split(".")[0] + "." + enc
    return loc
