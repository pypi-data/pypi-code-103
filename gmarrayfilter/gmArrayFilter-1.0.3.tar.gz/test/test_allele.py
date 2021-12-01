import pytest
from collections import Counter
import arrayFilter._var as VAR
import arrayFilter._allele as AlleleProcessor

from . import TEST_NA_PARAMS
from . import TEST_HYBRID_PARAMS
from . import TEST_LEGAL_ALLELES_PARAMS
from . import TEST_ALLELES_WITH_NA_PARAMS


@pytest.mark.parametrize("allele, result", TEST_NA_PARAMS)
def test_naAlleleTransform(allele, result):
    assert (AlleleProcessor.naAlleleTransform(allele) == VAR.AlleleType.NA) == result


@pytest.mark.parametrize("allele, result", TEST_HYBRID_PARAMS)
def test_isHybrid(allele, result):
    assert AlleleProcessor.isHybrid(allele) == result


@pytest.mark.parametrize("allele, result", TEST_LEGAL_ALLELES_PARAMS)
def test_isATGCorNA(allele, result):
    assert AlleleProcessor.isATGCorNA(allele) == result


@pytest.mark.parametrize("alleles", TEST_ALLELES_WITH_NA_PARAMS)
def test_twiAllele_not_allow_na(alleles):
    allele_grp_count = Counter(alleles)
    assert AlleleProcessor.twiAllele(allele_grp_count, 0) is None


@pytest.mark.parametrize("alleles", TEST_ALLELES_WITH_NA_PARAMS)
def test_twiAllele_allow_na(alleles):
    allele_grp_count = Counter(alleles)
    assert AlleleProcessor.twiAllele(allele_grp_count, 1) == alleles[0]
