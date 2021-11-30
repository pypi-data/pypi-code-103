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

"""
Functions to be used directly within an idict workflow
"""
from io import BytesIO, StringIO

from arff2pandas import a2p


def df2np(input="df", Xout="X", yout="y", **kwargs):
    """
    >>> from idict import let, idict
    >>> d = idict.fromminiarff()
    >>> d >>= df2np
    >>> d.show(colored=False)
    {
        "X": "→(input Xout yout df)",
        "y": "→(input Xout yout df)",
        "_history": {
            "df2np--------pandas-1.3.4--sklearn-1.0.1": {
                "name": "df2np",
                "description": "DataFrame (pandas) to X,y (numpy) converter.",
                "parameters": {
                    "input": "df",
                    "Xout": "X",
                    "yout": "y"
                },
                "code": "def f(input='df', Xout='X', yout='y', **kwargs):\\nfrom sklearn.preprocessing import LabelEncoder\\nle = LabelEncoder()\\ndf = kwargs[input]\\nX_ = df.drop((df.columns[[-1]]), axis=1)\\ny_ = le.fit_transform(df[df.columns[(-1)]])\\nreturn {Xout: X_, yout: y_, '_history': ...}"
            }
        },
        "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
        "_id": "E44sczWfUMWFuItAavOd9v.4Q1.sklearn-1.0.1",
        "_ids": {
            "X": "d4mcz9Xanx8fRsribw-L8-UdKxF9mlearj-1.0.2",
            "y": "fSwn3UKP-APakeSBnJMc6f5n6.6tklearn-1.0.3",
            "_history": "A3RPrmvmGNuH9IfL02DgQY2007VEzNNRA8xZ0.0X",
            "df": "ja_3dbc3e0089a672ae7896199398b692362dc99 (content: 6X_dc8ccea3b2e46f1c78967fae98b692701dc99)"
        }
    }
    >>> d.y
    array([0, 1])
    """
    from sklearn.preprocessing import LabelEncoder

    le = LabelEncoder()
    df = kwargs[input]
    X_ = df.drop(df.columns[[-1]], axis=1)
    y_ = le.fit_transform(df[df.columns[-1]])
    return {Xout: X_, yout: y_, "_history": ...}


df2np.metadata = {
    "id": "df2np--------pandas-1.3.4--sklearn-1.0.1",
    "name": "df2np",
    "description": "DataFrame (pandas) to X,y (numpy) converter.",
    "parameters": ...,
    "code": ...,
}


def df2arff(input="df", output="arff", **kwargs):
    """
    >>> from idict import let, idict
    >>> d = idict.fromminiarff()
    >>> d >>= let(df2arff, output="a")
    >>> d.show(colored=False)
    {
        "a": "→(input output df)",
        "_history": {
            "df2arff----------------arff2pandas-1.0.1": {
                "name": "df2arff",
                "description": "DataFrame (pandas) to ARFF converter.",
                "parameters": {
                    "input": "df",
                    "output": "a"
                },
                "code": "def f(input='df', output='arff', **kwargs):\\nfrom arff2pandas import a2p\\nreturn {output: a2p.dumps(kwargs[input]), '_history': ...}"
            }
        },
        "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
        "_id": "xdyZaF3yh4jf0fQK8IxSo0m5XKfLPerBLwVuTve8",
        "_ids": {
            "a": "ThqwG-KOhpzcRprusvXcZwjDrLgLPerBLwVuTve9",
            "_history": "ofEb.nRSYsUsgAnnyp4KYFovZaUOV6000sv....-",
            "df": "ja_3dbc3e0089a672ae7896199398b692362dc99 (content: 6X_dc8ccea3b2e46f1c78967fae98b692701dc99)"
        }
    }
    >>> d.a
    '@RELATION data\\n\\n@ATTRIBUTE attr1 REAL\\n@ATTRIBUTE attr2 REAL\\n@ATTRIBUTE class {0, 1}\\n\\n@DATA\\n5.1,3.5,0\\n3.1,4.5,1\\n'
    """
    from arff2pandas import a2p

    return {output: a2p.dumps(kwargs[input]), "_history": ...}


df2arff.metadata = {
    "id": "df2arff----------------arff2pandas-1.0.1",
    "name": "df2arff",
    "description": "DataFrame (pandas) to ARFF converter.",
    "parameters": ...,
    "code": ...,
}


def openml(Xout="X", yout="y", name="iris", version=1):
    """
    >>> from idict import Ø
    >>> (Ø >> openml).show(colored=False)
    {
        "X": "→(Xout yout name version)",
        "y": "→(Xout yout name version)",
        "_history": {
            "openml---------------------sklearn-1.0.1": {
                "name": "openml",
                "description": "Fetch DataFrame+Series (pandas) from OpenML.",
                "parameters": {
                    "Xout": "X",
                    "yout": "y",
                    "name": "iris",
                    "version": 1
                },
                "code": "def f(Xout='X', yout='y', name='iris', version=1):\\nfrom sklearn.datasets import fetch_openml\\nX, y = fetch_openml(name=name, version=version, as_frame=True, return_X_y=True)\\nreturn {Xout: X, yout: y, '_history': ...}"
            }
        },
        "_id": "openml---------------------sklearn-1.0.1",
        "_ids": {
            "X": "ze11cyj1Gi2mcWmsh1rrjkjdzgI9mlearj-1.0.2",
            "y": "nw5qXzxIkHrUajn6VTL7M7KIWLZsklearn-1.0.3",
            "_history": "W46Q.9OBxnS9oeFTzDYkRbWSoDQEzNNRA8xZ0.0X"
        }
    }
    >>> (Ø >> openml).X.head()
       sepallength  sepalwidth  petallength  petalwidth
    0          5.1         3.5          1.4         0.2
    1          4.9         3.0          1.4         0.2
    2          4.7         3.2          1.3         0.2
    3          4.6         3.1          1.5         0.2
    4          5.0         3.6          1.4         0.2
    >>> (Ø >> openml).y.head()
    0    Iris-setosa
    1    Iris-setosa
    2    Iris-setosa
    3    Iris-setosa
    4    Iris-setosa
    Name: class, dtype: category
    Categories (3, object): ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
    """
    from sklearn.datasets import fetch_openml

    X, y = fetch_openml(name=name, version=version, as_frame=True, return_X_y=True)
    return {Xout: X, yout: y, "_history": ...}


openml.metadata = {
    "id": "openml---------------------sklearn-1.0.1",
    "name": "openml",
    "description": "Fetch DataFrame+Series (pandas) from OpenML.",
    "parameters": ...,
    "code": ...,
}


# todo-tentar criar xy de DF usando x=DF e y=series, em vez de numpy. testar com RF      df[df.columns[-1]]


def arff2df(input="arff", output="df", **kwargs):
    r"""
    >>> from idict import let, idict
    >>> d = idict.fromminiarff(output=["arff"], output_format="arff")
    >>> d.arff
    '@RELATION mini\n@ATTRIBUTE attr1\tREAL\n@ATTRIBUTE attr2 \tREAL\n@ATTRIBUTE class \t{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1'
    >>> d >>= arff2df
    >>> d.show(colored=False)
    {
        "df": "→(input output arff)",
        "_history": {
            "arff2df----------------arff2pandas-1.0.1": {
                "name": "arff2df",
                "description": "ARFF to DataFrame (pandas) converter.",
                "parameters": {
                    "input": "arff",
                    "output": "df"
                },
                "code": "def f(input='arff', output='df', **kwargs):\nwith StringIO() as (f):\n    f.write(kwargs[input])\n    df = a2p.loads(f.getvalue())\nreturn {output: df, '_history': ...}"
            }
        },
        "arff": "@RELATION mini\n@ATTRIBUTE attr1\tREAL\n@ATTRIBUTE attr2 \tREAL\n@ATTRIBUTE class \t{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1",
        "_id": "n4EMpHwlrvpM-fFo4LC5914xb892pandas-1.0.1",
        "_ids": {
            "df": "ro3YIlxbNkgwanHshPzTghlh3T.Kqandao-1.0.2",
            "_history": "ofEb.nRSYsUsgAnnyp4KYFovZaUOV6000sv....-",
            "arff": "OW_29bd5266cf0a6400c5747b4c332b4a54d1955 (content: Ev_8bb973161e5ae900c5743b3c332b4a64d1955)"
        }
    }
    >>> d.df
       attr1@REAL  attr2@REAL class@{0,1}
    0         5.1         3.5           0
    1         3.1         4.5           1
    """
    with StringIO() as f:
        f.write(kwargs[input])
        df = a2p.loads(f.getvalue())

    return {output: df, "_history": ...}


arff2df.metadata = {
    "id": "arff2df----------------arff2pandas-1.0.1",
    "name": "arff2df",
    "description": "ARFF to DataFrame (pandas) converter.",
    "parameters": ...,
    "code": ...,
}
