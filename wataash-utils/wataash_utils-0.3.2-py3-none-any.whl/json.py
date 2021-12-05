# SPDX-License-Identifier: Apache-2.0

import typing as t

# https://github.com/python/typing/issues/182
JSON = t.Union[str, int, float, bool, None, t.Dict[str, 'JSON'], t.List['JSON']]
