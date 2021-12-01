import arrayFilter._var as VAR

TEST_NA_PARAMS = [
    ("---", True),
    ("-/-", True),
    ("./.", True),
    ("NA", True),
    ("AA", False),
    ("A/A", False),
    ("1/1", False),
]


TEST_HYBRID_PARAMS = [
    ("AT", True),
    ("1/0", True),
    ("A/T", True),
    ("AA", False),
    ("A/A", False),
    ("1/1", False),
]


TEST_LEGAL_ALLELES_PARAMS = [
    ("-/-", True),
    ("---", True),
    ("./.", True),
    ("AA", True),
    ("A/A", True),
    ("1/1", True),
    ("ATTTTTGG", True),
    ("ATTTTTGG/ATTTTTGG", True),
    ("A", False),
    ("chr1A", False),
    ("PolyHighResolution", False),
    (1160480, False),
]

TEST_ALLELES_WITH_NA_PARAMS = [
    ["AA", VAR.AlleleType.NA],
    ["A/A", VAR.AlleleType.NA],
    ["1/1", VAR.AlleleType.NA],
]
