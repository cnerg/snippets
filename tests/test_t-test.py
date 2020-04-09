"""Test module for t_test.py.

This module contains a number of pytest-based tests for t_test.py script.

The following classes/methods are included in this module:
- TestCheckDataMatching
  * test_mismatch_err
- TestTwoSampleT
  * test_t_result
- TestTTest
  * test_stat_result

"""

import pytest

from source import t_test as tt

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
            tt.check_data_matching(set_1, set_2, False)


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


class TestTTest(object):
    """Test t_test function."""

    @pytest.mark.parametrize("sample_1, sample_2, alpha, d, exp_stat", [
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, 0,
         {'a': (-1.561737618886062, 1998, 0.11850818000090202,
                1.9611520148367056, False)}),
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, -0.05,
         {'a': (-0.7808688094430317, 1998, 0.43497216473540523,
                1.9611520148367056, False)}),
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.2, 0,
         {'a': (-1.561737618886062, 1998, 0.11850818000090202,
                1.2819754246852082, True)}),
        ({'a': [1.0, 0.04, 25]}, {'a': [1.1, 0.05, 25]}, 0.05, 0,
         {'a': (-1.561737618886062, 48, 0.12491951102021281,
                2.0106347546964454, False)}),
        ({'a': [1.0, 0.04, 90]}, {'a': [1.1, 0.05, 120]}, 0.05, 0,
         {'a': (-1.561737618886062, 208, 0.11986998647209779,
                1.9714346585183504, False)}),
        ({'a': [1.0, 0.04, 1000]}, {'a': [1.1, 0.09, 1000]}, 0.05, 0,
         {'a': (-1.01534616513362, 1998, 0.31006378040221927,
                1.9611520148367056, False)}),
        ({'a': [1.0, 0.02, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, 0,
         {'a': (-1.85695338177052, 1998, 0.06346485996833384,
                1.9611520148367056, False)}),
        ({'a': [0.9, 0.04, 1000]}, {'a': [1.1, 0.05, 1000]}, 0.05, 0,
         {'a': (-3.1234752377721224, 1998, 0.0018129223981677711,
                1.9611520148367056, True)}),
        ({'a': [1.0, 0.04, 1000], 'b': [170, 8, 100]},
         {'a': [1.1, 0.05, 1000], 'b': [189, 7, 100]}, 0.05, 0,
         {'a': (-1.561737618886062, 1998, 0.11850818000090202,
                1.9611520148367056, False),
          'b': (-1.7873696499288347, 198, 0.07540731280844581,
                1.9720174778338955, False)})
    ])
    def test_stat_result(self, sample_1, sample_2, alpha, d, exp_stat):
        """Test if the function properly performs t-tests on given data sets."""
        obs_stat = tt.t_test(sample_1, sample_2, alpha, d, True)
        assert obs_stat == exp_stat
