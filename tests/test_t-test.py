"""Test module for t_test.py.

This module contains a number of pytest-based tests for t_test.py script.

The following classes/methods are included in this module:
- TestCheckDataMatching
  * test_mismatch_err
- TestTwoSampleT
  * test_t_result

"""

import pytest

import t_test as tt

TOL=1e-5  # Tolerance for approximate assertion.


class TestCheckDataMatching(object):
    """Test check_data_matching function."""

    @pytest.mark.parametrize("set_1, set_2", [
        ({1, 2, 3}, {1, 2, 3, 4}),
        ({'a', 'b', 'c'}, {'a', 'b'}),
        ({1, 2}, set({})),
        ({'a', 'b', 'c'}, {'a', 'b', 'd'})
    ])
    def test_mismatch_err(self, set_1, set_2):
        """Test if error is properly raised with mismatching sets."""
        with pytest.raises(KeyError):
            tt.check_data_matching('file1', set_1, 'file2', set_2)


class TestTwoSampleT(object):
    """Test two_sample_t function"""

    @pytest.mark.parametrize("m1, se1, m2, se2, d, exp_t", [
        (1.1, 0.05, 1.2, 0.04, 0, -1.561738),
        (305, 1.2, 298, 3.2, 6.5, 0.146301),
        (0.08411, 0.00001, 0.08327, 0.00002, 0.0005, 15.20526),
    ])
    def test_t_result(self, m1, se1, m2, se2, d, exp_t):
        """Test if the function properly calculates t-statistic."""
        obs_t = tt.two_sample_t(m1, se1, m2, se2, d)
        assert obs_t == pytest.approx(exp_t, abs=TOL)
