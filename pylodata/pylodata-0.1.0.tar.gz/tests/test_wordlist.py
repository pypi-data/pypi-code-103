from pylodata import data_path
from pylodata.wordlist import *
from pylodata.patterns import *
from lingpy import Wordlist

def test_get_binary_patterns():
    wl = Wordlist(data_path("wichmannmixezoquean.tsv"))
    pats, characters = get_binary_patterns(wl, "cogid")
    etd = wl.get_etymdict(ref="cogid")
    assert len(etd) == len(pats)


def test_get_multistate_patterns():
    wl = Wordlist(data_path("wichmannmixezoquean.tsv"))
    pats, characers = get_multistate_patterns(wl, "cogid")
    assert len(pats) == wl.height

def test_get_correspondence_patterns():
    pats, characters = get_correspondence_patterns(
            data_path("wichmannmixezoquean-correspondences.tsv"),
            positions=["c", "v"], threshold=1)
    assert len(pats) == 176
    assert len(get_correspondence_patterns(
            data_path("wichmannmixezoquean-correspondences.tsv"),
            positions=["c"])[0]) < len(pats)
    assert len(get_binary_correspondence_patterns(
            data_path("wichmannmixezoquean-correspondences.tsv"),
            positions=["c"], threshold=1)[0]) > len(pats)


