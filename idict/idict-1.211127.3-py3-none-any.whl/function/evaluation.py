#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#


def split(input=["X", "y"], seed=0, test_pct=33, **kwargs):
    """
    >>> from idict import idict, let
    >>> d = idict.fromtoy() >> split
    >>> d.show(colored=False)
    {
        "Xtr": "→(input seed test_pct X y)",
        "ytr": "→(input seed test_pct X y)",
        "Xts": "→(input seed test_pct X y)",
        "yts": "→(input seed test_pct X y)",
        "_history": {
            "split------------------------------idict": {
                "name": "split",
                "description": "Split data in two sets.",
                "parameters": {
                    "input": [
                        "X",
                        "y"
                    ],
                    "seed": 0,
                    "test_pct": 33
                },
                "code": "def f(input=['X', 'y'], seed=0, test_pct=33, **kwargs):\\nif input != ['X', 'y']:\\n    raise Exception(f\\"Not implemented for input different than ['X', 'y']: {input}\\")\\nfrom sklearn.model_selection import train_test_split\\nargs = [kwargs[input[i]] for i in range(len(input))]\\nXtr, Xts, ytr, yts = train_test_split(*args, test_size=test_pct / 100, shuffle=True, stratify=args[1], random_state=seed)\\nreturn {'Xtr':Xtr, \\n 'ytr':ytr,  'Xts':Xts,  'yts':yts,  '_history':...}"
            }
        },
        "X": "«{'attr1': {0: 5.1, 1: 1.1, 2: 6.1, 3: 1.1, 4: 3.1, 5: 4.7, 6: 9.1, 7: 8.3, 8: 9.1, 9: 2.5, 10: 7.1, 11: 0.1, 12: 2.1, 13: 0.1, 14: 5.1, 15: 31.1, 16: 1.1, 17: 2.2, 18: 3.1, 19: 1.1}, 'attr2': {0: 6.4, 1: 2.5, 2: 3.6, 3: 3.5, 4: 2.5, 5: 4.9, 6: 3.5, 7: 2.9, 8: 7.2, 9: 4.5, 10: 6.6, 11: 4.3, 12: 0.1, 13: 4.0, 14: 4.5, 15: 4.7, 16: 3.2, 17: 8.5, 18: 2.5, 19: 8.5}}»",
        "y": "«[0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1]»",
        "_id": "p.x69T.cSjiQ54bFGF7ZgltTkc.--------idict",
        "_ids": {
            "Xtr": "ilZI7tLD4Nd4-rBhm1VwwhL0Dl---------idicu",
            "ytr": "jCa.izCg7Htl4knG3X7xq0tzr4c.-------idicv",
            "Xts": "Vq7kyqYYP5OEx3cGLQmxdWa6gPV--------idicw",
            "yts": "PWPzJwzif12WDDJ2tKBx8FUE4y7.-------idicx",
            "_history": "8wu1HRHVwRK1TSAb43PgOraAUhwXQg333.16o9ru",
            "X": "-2_3606060c77dc8f0807deec66fac5120578d0e (content: 34_1738c83af436029507def2710bc5125f58d0e)",
            "y": "o._080bf2a35d8ab275d4050dfd02b939104feac (content: S0_b6360d62ccafa275d4051dfd02b939104feac)"
        }
    }
    >>> d.yts
    array([1, 0, 1, 0, 0, 0, 1])
    """
    if input != ["X", "y"]:
        # TODO create a way in ldict to accept a dynamic dict as return value
        raise Exception(f"Not implemented for input different than ['X', 'y']: {input}")
    from sklearn.model_selection import train_test_split

    # Multidynamic input is only detected when the kwargs index is also indexed by something.
    args = [kwargs[input[i]] for i in range(len(input))]
    Xtr, Xts, ytr, yts = train_test_split(
        *args, test_size=test_pct / 100, shuffle=True, stratify=args[1], random_state=seed
    )
    return {"Xtr": Xtr, "ytr": ytr, "Xts": Xts, "yts": yts, "_history": ...}


split.metadata = {
    "id": "split------------------------------idict",
    "name": "split",
    "description": "Split data in two sets.",
    "parameters": ...,
    "code": ...,
}
