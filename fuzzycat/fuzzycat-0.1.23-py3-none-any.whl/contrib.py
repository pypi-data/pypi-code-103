"""
Contrib related comparisons.

Example: NgramContribMatcher, which compares two normalized raw name tokens
with a jaccard index.

    matcher = ContribMatcher(cmp=JaccardIndexThreshold(0.5),
                             pipeline=Pipeline([
                                 lambda rc: rc.raw_name,
                                 str.strip,
                                 str.lower,
                                 Ngram(n=3),
                                 set,
                             ]))
    result = matcher.compare(a, b)
    ...

Some notes from the dataset.

* 692,893,828 contribs
*  64,680,311 uniq

Top contrib names, many have their name on datasets, which explains the high
number.

3069752 Kessy Abarenkov
2383819 Leho Tedersoo
2383748 Karl-Henrik Larsson
2383745 Urmas Kõljalg
2383699 Mohammad Bahram
2383692 Martin Ryberg
2382832 R. Henrik Nilsson
1702455 Markus Döring
1702427 Tom May
1702415 Dmitry Schigel
1702391 Santiago Sánchez-Ramírez
 841475 GLIS Of The ITPGRFA
 682144 James Scott
 682053 Michael Weiss
 681404 Susumu Takamatsu
 681388 A. Elizabeth Arnold
 681347 Artur Alves
 681341 Ellen Larsson
 681338 Maarja Öpik
 681335 Ursula Eberhardt
 681324 Nhu Nguyen
 681293 Otto Miettinen
 681292 Viacheslav Spirin
 681287 Gareth W. Griffith
 681283 Bálint Dima
 681278 Ursula Peintner
 681276 Tuula Niskanen
 681276 Olinto Liparini Pereira
 681275 Kare Liimatainen
"""

import collections
import functools
import itertools
import logging
import operator
import re
import string
from typing import Any, Callable, List, Optional, Set

import jellyfish
import thefuzz
from fatcat_openapi_client import ReleaseContrib

logger = logging.getLogger("fuzzycat")


class Ngram:
    """
    Turn a string into a list of overlapping tokens.
    """
    def __init__(self, n: int = 3):
        if n < 1:
            raise ValueError("positive n required")
        self.n = n

    def __call__(self, s: str) -> List[str]:
        if 0 < len(s) < self.n:
            return [s]
        return [s[i:i + self.n] for i in range(len(s) - self.n + 1)]


class JaccardIndexThreshold:
    """
    A Jaccard index threshold that can be used to compare two sets. Two empty
    sets are equal.
    """
    def __init__(self, threshold: float = 0.5, verbose=False):
        self.threshold = threshold
        self.verbose = verbose

    def __call__(self, a: Set, b: Set) -> bool:
        if len(a) == 0 and len(b) == 0:
            return True
        index = len(a & b) / len(a | b)
        if self.verbose:
            logger.debug("[jaccard] {}".format(index))
        return index >= self.threshold


class FuzzyStringSimilarity:
    """
    For two sets of strings, run fuzzy matching with "thefuzz" -
    https://github.com/seatgeek/thefuzz, which among other things uses
    Levenshtein distance.

    The min ratio can range from 0 to 100 (with 100 allowing exact matches
    only).
    """
    def __init__(self, min_ratio=75):
        self.min_ratio = min_ratio

    def __call__(self, a: Set, b: Set) -> bool:
        agg = 0
        for v in a:
            match, score = thefuzz.exctractOne(v, b)
            agg += score
        return score > self.min_ratio


class Pipeline:
    """
    A list of functions to execute, f -> g -> h, etc. Note that the output
    type of f needs to match the input type of g, etc.
    """
    def __init__(self, pipeline: Optional[List[Any]] = None, verbose: bool = False):
        self.verbose = verbose
        if pipeline is None:
            self.pipeline = [
                lambda v: v,
            ]
        else:
            self.pipeline = pipeline

    def run(self, value: Any) -> Any:
        v = value
        for i, f in enumerate(self.pipeline, start=1):
            v = f(v)
            if self.verbose:
                logger.debug("[{}/{}] {}".format(i, len(self.pipeline), v))
        return v

    def __call__(self, value: Any, verbose: bool = False) -> Any:
        self.verbose = verbose
        return self.run(value)


# default_release_contrib_pipeline normalizes the raw name.
default_release_contrib_pipeline = Pipeline([
    lambda rc: rc.raw_name,
    str.strip,
    str.lower,
])

# default_release_contrib_list_pipeline turns contribs list into a contrib set.
default_release_contrib_list_pipeline = Pipeline([
    lambda seq: set((c.raw_name for c in seq)),
])


class ContribMatcher:
    """
    Compare two contrib entities and determine a match status, based on some
    configuration. The final values of the `pipeline` will be compared with
    `cmp`, which by default is equality.

    Other `cmp` options may generate ngrams and use jaccard index with some
    threshold or decide on a string similarity metric.

    This is essentially just a shell, the various comparison methods live in
    the tuple (pipeline, cmp).
    """
    def __init__(self,
                 pipeline: Optional[List[Any]] = default_release_contrib_list_pipeline,
                 cmp: Callable[[Any, Any], bool] = operator.__eq__):
        self.pipeline = pipeline
        self.cmp = cmp

    def compare(self, a: ReleaseContrib, b: ReleaseContrib) -> bool:
        """
        Compare returns True, if a and b are considered the same, given a
        transformation pipeline and a comparison operation.
        """
        u = self.pipeline(a)
        v = self.pipeline(b)
        return self.cmp(u, v)


class ContribListMatcher:
    """
    Compare two lists of contribs. Each contrib entry is passed through the
    same pipeline.

    Often two issues (separate or combined).

    - contrib missing, e.g.
    - "Gentle Sunder Shrestha", "Gentle S Shrestha", "S. Shrestha", "Gentle Shrestha", ...
    """
    def __init__(self,
                 pipeline: Optional[List[Any]] = default_release_contrib_list_pipeline,
                 cmp: Callable[[Any, Any], bool] = JaccardIndexThreshold(1.0)):
        self.pipeline = pipeline
        self.cmp = cmp

    def compare(self,
                a: List[ReleaseContrib],
                b: List[ReleaseContrib],
                verbose: bool = False) -> bool:
        """
        Compare two lists of contribs, pass each one through the pipeline. The
        result may be a list or any other type. The comparison function needs
        to be compatible.
        """
        u = self.pipeline(a, verbose=verbose)
        v = self.pipeline(b, verbose=verbose)
        return self.cmp(u, v)


def cleanup_single_ws(s: str) -> str:
    return re.sub(r"[ ]{2,}", " ", s)


def cleanup_remove_ws(s: str) -> str:
    return re.sub(r"[\n\r\t\s]*", '', s)


def cleanup_keep_letters_digits_ws(s: str) -> str:
    return ''.join((c for c in s if c in string.ascii_letters + string.digits + " "))


def test_cleanup_single_ws():
    Case = collections.namedtuple("Case", "s result")
    cases = (
        Case("", ""),
        Case("abc", "abc"),
        Case("abc abc", "abc abc"),
        Case("abc  abc", "abc abc"),
        Case("   abc  abc", " abc abc"),
        Case("   abc  abc", " abc abc"),
    )
    for c in cases:
        assert c.result == cleanup_single_ws(c.s)


def test_cleanup_remove_ws():
    Case = collections.namedtuple("Case", "s result")
    cases = (
        Case("", ""),
        Case("abc", "abc"),
        Case("abc abc", "abcabc"),
        Case("abc  abc", "abcabc"),
        Case("   abc  abc", "abcabc"),
    )
    for c in cases:
        assert c.result == cleanup_remove_ws(c.s), c


def test_ngram():
    Case = collections.namedtuple("Case", "s n result")
    cases = (
        Case("", 1, []),
        Case("", 2, []),
        Case("a", 2, ["a"]),
        Case("ab", 2, ["ab"]),
        Case("abcdef", 2, ['ab', 'bc', 'cd', 'de', 'ef']),
        Case("abcdef", 4, ['abcd', 'bcde', 'cdef']),
        Case("Nina Rogo", 3, ["Nin", "ina", "na ", "a R", " Ro", "Rog", "ogo"]),
    )
    for c in cases:
        ngram = Ngram(n=c.n)
        assert ngram(c.s) == c.result


def test_pipeline():
    Case = collections.namedtuple("Case", "pipeline input result")
    cases = (Case(Pipeline([lambda v: v["a"], str.strip, str.lower,
                            Ngram(n=3), set]), {"a": " X123  "}, {'123', 'x12'})),
    for c in cases:
        result = c.pipeline(c.input)
        assert result == c.result


def test_jaccard_index_threshold():
    Case = collections.namedtuple("Case", "a b threshold result")
    cases = (
        Case(set(), set(), 1.0, True),
        Case(set(), set(["a"]), 1.0, False),
        Case(set(["a"]), set(["a"]), 1.0, True),
        Case(set(["a"]), set(["a", "b"]), 1.0, False),
        Case(set(["a"]), set(["a", "b"]), 0.5, True),
        Case(set(["a"]), set(["a", "b", "c"]), 0.5, False),
    )
    for c in cases:
        jit = JaccardIndexThreshold(threshold=c.threshold)
        result = jit(c.a, c.b)
        assert result == c.result


def test_ngram_contrib_matcher(caplog):
    Case = collections.namedtuple("Case", "a b result")
    cases = (
        Case(
            ReleaseContrib(raw_name="Jane Austen"),
            ReleaseContrib(raw_name="J.Austen"),
            True,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor M. Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor Michailowitsch Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
    )
    matcher = ContribMatcher(cmp=JaccardIndexThreshold(0.4, verbose=True),
                             pipeline=Pipeline([
                                 lambda rc: rc.raw_name,
                                 str.strip,
                                 str.lower,
                                 cleanup_remove_ws,
                                 cleanup_keep_letters_digits_ws,
                                 Ngram(n=3),
                                 set,
                             ],
                                               verbose=True))
    for c in cases:
        with caplog.at_level(logging.DEBUG):
            result = matcher.compare(c.a, c.b)
            assert result == c.result


def test_jellyfish_soundex_contrib_matcher(caplog):
    Case = collections.namedtuple("Case", "a b result")
    cases = (
        Case(
            ReleaseContrib(raw_name="Jane Austen"),
            ReleaseContrib(raw_name="J.Austen"),
            True,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor M. Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor Michailowitsch Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
    )
    matcher = ContribMatcher(cmp=JaccardIndexThreshold(0.3, verbose=True),
                             pipeline=Pipeline([
                                 lambda rc: rc.raw_name,
                                 str.strip,
                                 str.lower,
                                 functools.partial(re.sub, r"[.;]", " "),
                                 cleanup_keep_letters_digits_ws,
                                 lambda s: set((jellyfish.soundex(v) for v in s.split())),
                             ],
                                               verbose=True))
    for c in cases:
        with caplog.at_level(logging.DEBUG):
            result = matcher.compare(c.a, c.b)
            assert result == c.result


def test_jellyfish_nysiis_contrib_matcher(caplog):
    Case = collections.namedtuple("Case", "a b result")
    cases = (
        Case(
            ReleaseContrib(raw_name="Jane Austen"),
            ReleaseContrib(raw_name="J.Austen"),
            True,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor M. Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
        Case(
            ReleaseContrib(raw_name="Fjodor Michailowitsch Dostojewski"),
            ReleaseContrib(raw_name="Fyodor Dostoevsky"),
            False,
        ),
    )
    matcher = ContribMatcher(cmp=JaccardIndexThreshold(0.3, verbose=True),
                             pipeline=Pipeline([
                                 lambda rc: rc.raw_name,
                                 str.strip,
                                 str.lower,
                                 functools.partial(re.sub, r"[.;]", " "),
                                 cleanup_keep_letters_digits_ws,
                                 lambda s: set((jellyfish.nysiis(v) for v in s.split())),
                             ],
                                               verbose=True))
    for c in cases:
        with caplog.at_level(logging.DEBUG):
            result = matcher.compare(c.a, c.b)
            assert result == c.result


def test_default_contrib_list_matcher(caplog):
    Case = collections.namedtuple("Case", "a b result")
    cases = (
        Case(
            [],
            [],
            True,
        ),
        Case(
            [ReleaseContrib(raw_name="Michael Jordan")],
            [ReleaseContrib(raw_name="Michael Jordan")],
            True,
        ),
        Case(
            [ReleaseContrib(raw_name="Michael Jordan")],
            [ReleaseContrib(raw_name="michael jordan")],
            False,
        ),
        Case(
            [ReleaseContrib(raw_name="Amadeu Llebaria")],
            [ReleaseContrib(raw_name="A. Llebaria")],
            False,
        ),
    )
    matcher = ContribListMatcher()
    for c in cases:
        with caplog.at_level(logging.DEBUG):
            result = matcher.compare(c.a, c.b, verbose=True)
            assert result == c.result
