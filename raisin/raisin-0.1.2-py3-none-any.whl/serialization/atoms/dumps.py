#!/usr/bin/env python3

"""
** Conversion from ascii to object. **
--------------------------------------
"""


def deserialize_dumps(pack, gen, psw, paralleling_rate, **_):
    """
    ** Deserialize the objects returned by the function ``raisin.serialization.dumps``. **

    Examples
    --------
    >>> from raisin.serialization.atoms.dumps import deserialize_dumps
    >>> deserialize_dumps(pack=b'0aWDBam0vc', gen=[], psw=None, paralleling_rate=0)
    123456789
    >>>
    """
    from raisin.serialization.core import deserialize, str2bytes

    return deserialize(
        pack=str2bytes((pack + b''.join(gen)).decode(encoding='ascii')),
        gen=[],
        psw=psw,
        paralleling_rate=paralleling_rate,
    )
