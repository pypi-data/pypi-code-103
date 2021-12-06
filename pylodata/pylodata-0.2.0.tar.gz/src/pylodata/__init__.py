from pathlib import Path

__version__ = "0.2.0"


def data_path(*combs):
    return Path(__file__).parent.joinpath("data").joinpath(*combs).as_posix()


SAMPLES = {
    "ex1": {
        "tree": "(((A,B)NodeA1,(C,D)NodeA2)NodeA,((E,F)NodeB1,(G,H)NodeB2)NodeB)Root;",
        "patterns": {
            "1": {
                "A": "a",
                "B": "b",
                "C": "b",
                "D": "c",
                "E": "c",
                "F": "a",
                "G": "a",
                "H": "a",
            }
        },
        "characters": ["a", "b", "c"],
        "taxa": ["A", "B", "C", "D", "E", "F", "G", "H"],
    },
    "ex2": {
        "tree": "(((A,B)NodeA1,(C,D)NodeA2)NodeA,((E,F)NodeB1,(G,H)NodeB2)NodeB)Root;",
        "patterns": {
            "2": {
                "A": "a",
                "B": ["a", "c"],
                "C": "b",
                "D": "c",
                "E": "c",
                "F": "a",
                "G": ["a", "b"],
                "H": ["a", "c"],
            }
        },
        "characters": ["a", "b", "c"],
        "taxa": ["A", "B", "C", "D", "E", "F", "G", "H"],
    },
    "wichmannmixezoquean.tree": "(((ChiapasZoque,(SanMiguelChimalapaZoque,SantaMariaChimalapaZoque)),(SoteapanZoque,TexistepecZoque)),(OlutaPopoluca,(SayulaPopoluca,(NorthHighlandMixe,(LowlandMixe,SouthHighlandMixe)))));",
    "wichmannmixezoquean-nj.tree": "(((((LowlandMixe:0.22,SouthHighlandMixe:0.21):0.050,NorthHighlandMixe:0.23):0.050,SayulaPopoluca:0.27):0.030,OlutaPopoluca:0.30):0.052,((ChiapasZoque:0.24,(SanMiguelChimalapaZoque:0.23,SantaMariaChimalapaZoque:0.20):0.050):0.020,(SoteapanZoque:0.22,TexistepecZoque:0.32):0.060):0.078);",
    "ex3": {
        "matrix": [[-2, 1, 1], [1, -2, 1], [1, 1, -2]],
        "pattern": {
            "A": ["a"],
            "B": ["b"],
            "C": ["a"],
            "D": ["c"],
            "E": ["c"],
            "F": ["b"],
        },
        "characters": ["a", "b", "c"],
        "tree": "((((A:1,B:1):0.5,C:1.5):1.0,(D:0.5,E:0.5):2),F:2.5);",
        "taxa": ["A", "B", "C", "D", "E", "F"],
    },
    "ex4": {
        "matrix": [[-2, 1, 1], [1, -2, 1], [1, 1, -2]],
        "pattern": {"A": ["a"], "B": ["b"], "C": ["c"], "D": ["d"]},
        "characters": ["a", "b", "c", "d"],
        "tree": "(((A:1,B:1):1,C:1):1,D:1);",
        "taxa": ["A", "B", "C", "D"],
        "pi": [0.25, 0.25, 0.25, 0.25],
    },
}
