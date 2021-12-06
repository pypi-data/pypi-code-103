"""This module contains test for `continuous` package."""

import pytest
import scipy.stats as st

from method_of_moments.continuous.beta import Beta


UNIT_INTERVAL = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
POSITIVE_FLOAT_NUMBERS = [10 ** i for i in range(-2, 4)]


class TestBeta:
    """Tests for Beta distribution"""

    @pytest.mark.parametrize("a_parameter", POSITIVE_FLOAT_NUMBERS)
    @pytest.mark.parametrize("b_parameter", POSITIVE_FLOAT_NUMBERS)
    @pytest.mark.parametrize("arg", UNIT_INTERVAL)
    def test_beta(self, a_parameter, b_parameter, arg):
        """Test for Beta distribution."""
        _scipy = st.beta
        _mom = Beta(
            mean=_scipy.mean(a_parameter, b_parameter),
            variance=_scipy.var(a_parameter, b_parameter),
        )
        assert pytest.approx(
            _scipy.pdf(arg, a_parameter, b_parameter) == _mom.pdf(arg=arg)
        )
