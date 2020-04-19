"""Test module for t_test.py.

This module contains a number of pytest-based tests for t_test.py script.

The following classes/methods are included in this module:
- TestCheckInputArgs
  * test_input_err
- TestCheckDataMatching
  * test_mismatch_err
  * test_mismatch_skip
- TestCaclTwosampleTvalue
  * test_t_result
- TestTTest
  * test_stat_result

"""

import pytest

from t_test import twosample_ttest as tt

TOL=1e-5  # Tolerance for approximate assertion.


class TestCheckInputArgs(object):
    """Test check_input_args function."""

    @pytest.mark.parametrize("sample_1, sample_2, alpha, d, skip, exp_err", [
        # Check input data for which t-test will be performed.
        ({'a': [1, 2, 3]}, "1, 2, 3", 0.05, 0.0, True, TypeError),
        ([1, 2, 3], {'b': [1, 2, 3]}, 0.05, 0.0, True, TypeError),
        ({'a': [1.0, 2.0, 3]}, {'b': 3}, 0.05, 0.0, True, TypeError),
        ({'a': [1.0, 2.0, 3]}, {'b': [1.0, 2.0]}, 0.05, 0.0, True, TypeError),
        ({'a': [1, 2, 3]}, {'b': [1, "2", 3]}, 0.05, 0.0, True, TypeError),
        # Check significance level.
        ({'a': [1, 2, 3]}, {'b': [1, 2, 3]}, "0.05", 0.0, True, TypeError),
        ({'a': [1, 2, 3]}, {'b': [1, 2, 3]}, 5.0, 0.0, True, ValueError),
        # Check discrepancy set between two input data.
        ({'a': [1, 2, 3]}, {'b': [1, 2, 3]}, 0.05, [0.0], True, TypeError),
        # Check the boolean to skip mismatching keywords.
        ({'a': [1, 2, 3]}, {'b': [1, 2, 3]}, 0.05, 0.0, "True", TypeError)
    ])
    def test_input_err(self, sample_1, sample_2, alpha, d, skip, exp_err):
        """Test if error is properly raised with invalid input arguments."""
        with pytest.raises(exp_err):
            tt.check_input_args(sample_1, sample_2, alpha, d, skip)


class TestCheckDataMatching(object):
    """Test check_data_matching function."""

    @pytest.mark.parametrize("set_1, set_2", [
        ({1, 2, 3}, {1, 2, 3, 4}),
        ({'a', 'b', 'c'}, {'a', 'b'}),
        ({1, 2}, set()),
        ({'a', 'b', 'c'}, {'a', 'b', 'd'})
    ])
    def test_mismatch_err(self, set_1, set_2):
        """Test if error is properly raised with mismatching sets."""
        with pytest.raises(KeyError):
            tt.check_data_matching(set_1, set_2, False)

    @pytest.mark.parametrize("set_1, set_2, exp_set", [
        ({'k1', 'k2', 'k3'}, {'k1', 'k2', 'k3'}, {'k1', 'k2', 'k3'}),
        ({1, 2, 3}, {1, 2, 3, 4}, {1, 2, 3}),
        ({5, 6}, {5}, {5}),
        ({'a', 'b', 'c'}, {'a', 'd', 'e'}, {'a'}),
        ({2, 4, 6, 8}, {1, 3, 5, 7}, set()),
    ])
    def test_mismatch_skip(self, set_1, set_2, exp_set):
        """Test if mismatching sets are properly skipped."""
        obs_set = tt.check_data_matching(set_1, set_2, True)
        assert obs_set == exp_set


class TestCalcTwosampleTvalue(object):
    """Test calc_twosample_tvalue function."""

    @pytest.mark.parametrize("m1, sd1, n1, m2, sd2, n2, d, exp_t", [
        # m1, se1, m2, se2, d, exp_t
        (1.1, 0.05, 3, 1.2, 0.04, 4, 0, -2.95742),
        (305, 1.2, 25, 298, 3.2, 25, 6.5, 0.73151),
        (0.08411, 0.00001, 15, 0.08327, 0.00002, 17, 0.0005, 59.52335),
    ])
    def test_t_result(self, m1, sd1, n1, m2, sd2, n2, d, exp_t):
        """Test if the function properly calculates t-statistic."""
        obs_t = tt.calc_twosample_tvalue(m1, sd1, n1, m2, sd2, n2, d)
        assert obs_t == pytest.approx(exp_t, abs=TOL)


class TestTTest(object):
    """Test t_test function."""

    @pytest.mark.parametrize("sample_1, sample_2, alpha, d, exp_stat", [
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, 0,
         {'a': (-1.56174, 1998, 0.11850761882920313,
                1.96115, False)}),
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, -0.05,
         {'a': (-0.78087, 1998, 0.4349714645987972,
                1.96115, False)}),
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.2, 0,
         {'a': (-1.56174, 1998, 0.11850761882920313,
                1.28198, True)}),
        ({'a': [1.0, 0.04, 25]}, {'a': [1.1, 0.05, 25]}, 0.05, 0,
         {'a': (-1.56174, 48, 0.12491894986321972,
                2.01063, False)}),
        ({'a': [1.0, 0.04, 90]}, {'a': [1.1, 0.05, 120]}, 0.05, 0,
         {'a': (-1.48488, 208, 0.13908953789919698,
                1.97143, False)}),
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.09, 1000]}, 0.05, 0,
         {'a': (-1.01535, 1998, 0.31006195348993537,
                1.96115, False)}),
        ({'a': [1.0, 0.02, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, 0,
         {'a': (-1.85695, 1998, 0.0634653413821944,
                1.96115, False)}),
        ({'a': [0.9, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, 0,
         {'a': (-3.12348, 1998, 0.0018128932050305302,
                1.96115, True)}),
        ({'a': [1.0, 0.04, 1000], 'b': [170, 8, 100]},
         {'a': [1.1, 0.05, 1000], 'b': [189, 7, 100]}, 0.05, 0,
         {'a': (-1.56174, 1998, 0.11850761882920313,
                1.96115, False),
          'b': (-1.78737, 198, 0.07540725606821463,
                1.97202, False)})
    ])
    def test_stat_result(self, sample_1, sample_2, alpha, d, exp_stat):
        """Test if the function properly performs t-tests on given data sets."""
        obs_stat = tt.t_test(sample_1, sample_2, alpha, d, True)
        assert obs_stat == exp_stat
