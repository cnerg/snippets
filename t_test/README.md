# t-test

This directory contains modules to run the t-test (also called Student's t-test)
on given sample data.

Primary purpose/feature of this work is to run an unpaired equal-variance
two-sample t-test on two sets of data.
This can be useful when one wants to determine whether or not there is a
statistically significant difference between the two sets.
Nuclear engineering relevant examples of such data include *k<sub>eff</sub>* and
tally results calculated by MCNP.


## Table of Contents

- [t-test?](#t-test?)
  - [Procedure](#procedure)
  - [Null hypothesis](#null-hypothesis)
  - [t-value](#t-value)
  - [t-distribution](#t-distribution)
  - [Two-tailed vs. One-tailed test](#two-tailed-vs.-one-tailed-test)
- [Difference with z-test?](#difference-with-z-test?)
- [How to interpret t-test result?](#how-to-interpret-t-test-result?)
- [Related modules, scripts and tests](#related-modules,-scripts-and-tests)
  - [`twosample_ttest.py`](#`twosample_ttest.py`)
  - [`run_twosample_ttest.py`](#`run_twosample_ttest.py`)
  - [`test_twosample_ttest.py`](#`test_twosample_ttest.py`)
- [References](#references)
- [](#)


## t-test?

The t-tests are handy hypothesis tests in statistics when you want to compare
means.
Depending on the t-test that you use, you can compare a sample mean to a
hypothesized value (one-sample t-test), the means of two independent samples
(two-sample t-test), or the difference between paired samples (paired t-test).

The term t-test refers to the fact that these hypothesis tests use
[t-values](###t-value), a type of what are called test statistics,
to evaluate your sample data.
A test statistic is a standardized value that is calculated from sample data
during a hypothesis test.
The procedure that calculates the test statistic compares your data to what is
expected under the [null hypothesis](#null-hypothesis).

t-values are not in the units of the original data, but unitless.
To be able to interpret individual t-values, you need to place them in a larger
context.
[t-distributions](#t-distribution) provide this broader context so you can
determine the unusualness of an individual t-value.
For t-tests, if you take a t-value and place it in the context of the correct
t-distribution, you can calculate a probability associated with the t-value.

The probability, also known as p-value, allows you to determine how common or
rare the t-value is under the assumption that the null hypothesis is true.
If the probability is low enough, it can be concluded that the effect observed
in the sample is inconsistent with the null hypothesis.
The evidence in the sample data is strong enough to reject the null hypothesis
for the entire population.


### Procedure

1. Determine a null and alternate hypothesis.
   For example:
   *H<sub>0</sub>*: μ<sub>1</sub> = μ<sub>2</sub>
   *H<sub>a</sub>*: μ<sub>1</sub> <ne> μ<sub>2</sub>
   where μ<sub>1</sub> is the mean of population 1 and μ<sub>1</sub> is
   the mean of population 2.

2. Determine a significance level.

   The significance level, also denoted as α, is the probability of
   rejecting the null hypothesis when it is true.
   For example, a significance level of 0.05 indicates a 5 % risk of concluding
   that a difference exists when there is no actual difference.

   The choice of significance level is arbitrary.
   Conventionally the 5 %, 1 % and 0.1 % (α = 0.05, 0.01 and 0.001)
   levels have been used.
   Scientists have found that a significance level of 5 % is a good balance
   between Type I error (false rejection of the null hypothesis) and Type II
   error (false acceptance of the null hypothesis).

   Note that significance level refers to a pre-chosen probability, while
   p-value indicates a probability that you calculate after a given study.

3. Calculate the t-value.

   Calculation of t-value requires mean and estimated standard error of the mean
   for each sample.
   (Or alternatively, mean, standard deviation and sample size.)
   Formula for calculating a t-value varies depending on a variety of
   conditions.

   - One-sample vs. Two-sample
   - Unpaired v.s Paired  (Independent vs. Dependent)
   - Equal mean vs. Unequal mean
   - Equal variance vs. Unequal variance  (Pooled vs. Unpooled)
   - Equal sample size vs. Unequal sample size

4. Determine the t-distribution.

   Specific t-distribution for the samples can be determined by degrees of
   freedom calculated from sample data.
   Formula for calculating degrees of freedom also varies by conditions.

5. Determine if the null hypothesis is rejected or accepted.

   There are two criteria that can be used to determine rejection/acceptance of
   null hypothesis.

   * p-value
     p-value is the probability of obtaining an effect at least as extreme as
     the one in your sample data, assuming the truth of the null hypothesis.
     p-value can be obtained using the t-value and cumulative distribution
     function (CDF) of the t-distribution.
     The p-value can then be compared to the chosen significance level
     (α) to determine if the null hypothesis can be rejected.

     - p-value > α: Accept null hypothesis.
     - p-value ≤ α: Reject null hypothesis and accept alternative
       hypothesis.

   * t<sub>crit</sub>
     t<sub>crit</sub>, or critical value for the t-distribution, is used as a
     threshold for interpreting the result of a statistical test.
     The observation values in the population beyond the critical value are
     often called the critical region or the region of rejection.

     - |t-value| ≤ t<sub>crit</sub>: Accept null hypothesis.
     - |t-value| > t<sub>crit</sub>: Reject the null hypothesis and accept
       alternative hypothesis.

     A critical value can be obtained using percent point function (PPF).
     It returns the value for the provided probability that is less than or
     equal to the provided probability from the distribution.

     For most common distributions, the observation values cannot be calculated
     analytically; instead it must be estimated using numerical methods.
     Historically it is common for tables of pre-calculated critical values to
     be provided in the appendices of statistics textbooks for reference
     purposes.


### Null hypothesis

The statement being tested in a test of statistical significance is called the
**null hypothesis** (*H<sub>0</sub>*).
Usually, the null hypothesis is a statement of 'no effect' or 'no difference'.

The statement that is being tested against the null hypothesis is the
**alternative hypothesis** (*H<sub>a</sub>* or *H<sub>1</sub>*).


### t-value

Each type of t-test uses a specific procedure to boil all of your sample data
down to one value, the t-value (also called t-score).
The calculations behind t-values compare your sample mean to the null
hypothesis and incorporates both the sample size and the variability in the
data.
A t-value of 0 indicates that the sample results exactly equal the null
hypothesis.
As the difference between the sample data and the null hypothesis increases,
the absolute value of the t-value increases.


### t-distribution

t-distribution (also called Student's t-distribution) is a type of probability
distributions that arises when estimating the mean of a normally distributed
population in situations where the sample size is small and the population
standard deviation is unknown.

The t-distribution centers on zero because it assumes that the null hypothesis
is true.
It is a symmetric, bell-shaped distribution that is similar to the normal
distribution, but with thicker tails.

A specific t-distribution is defined by its degrees of freedom (df),
a value closely related to sample size.
As the number of degrees of freedom grows, the t-distribution approaches the
normal distribution with mean 0 and variance 1.


### Two-tailed vs. One-tailed test

A two-tailed two-sample t-test can determine whether the difference between two
samples is statistically significant in either the positive or negative
direction.
A one-tailed test can only assess one of those directions.


## Difference with z-test?

z-test is used when comparing sample mean with large sample size to
population mean where population variance is known.

t-test is used to compare sample means with small sample size (< 30)
when population variance is unknown.


## How to interpret t-test result?

The significance level is also referred to as an error rate.
For a significance level of 0.05, expect to obtain sample means in the critical
region 5 % of the time when the null hypothesis is true.
In these cases, you won’t know that the null hypothesis is true but you
reject it because the sample mean falls in the critical region.

If the p-value is less than the chosen significance level, this suggests that
the observed data is sufficiently inconsistent with the null hypothesis and that
the null hypothesis may be rejected.
However, the p-value does not, in itself, support reasoning about the
probabilities of hypotheses.
It is only a tool for deciding whether to reject the null hypothesis.

p-values are calculated based on the assumptions that the null is true
for the population and that the difference in the sample is caused entirely
by random chance.
Consequently, p-values cannot tell you the probability that the null is true
or false because it is 100 % true from the perspective of the calculations.

While a low p-value indicates that your data are unlikely assuming a true
null, it cannot evaluate which of two competing cases is more likely:

- The null is true but your sample was unusual.
- The null is false.

Determining which case is more likely requires subject area knowledge and
replicate studies.


## Related modules, scripts and tests

### `twosample_ttest.py`

This is the main module for unpaired equal variance two-sample t-test,
located in `t_test` directory.
It contains the main function **t_test** that calls sub-functions and runs
t-tests, along with customizable data loading/processing and plotting functions.

Usage:

- Input:
  - `sample_1` & `sample_2`: Dictionary of {key: [Sample mean, Estimated standard
    error of the mean, sample size]} pair.
  - `alpha`: Significance level.
  - `d`: Set discrepancy between two input data, if any.
  - `skip`: Boolean to skip mismatching keywords.
- Output:
  - `stat`: Dictionary of {key, [t-vaue, degree of freedom, p-value,
    critical t-value, rejection boolean]} pair.
- Example:
```python
from t_test import twosample_ttest as tt
stat = tt.t_test(sample_1, sample_2, alpha, d, skip)
```

### `run_twosample_ttest.py`

This is a wrapper script, located in `scripts` directory, that runs
`twosample_ttest.py`.

Usage:
- Command line arguments:
  - `filenames`: Input data filenames. Must be two strings.
  - `--alpha`(`-a`): Target significance level.
  - `--discrepancy`(`-d`): Set discrepancy between two data set.
  - `--skip`(`-s`): Skip mismatching data points instead of raising errors.
  - `--verbose`(`-v`): Verbosity level of t-test result.
  - `--plot`(`-p`): Plot type and filename.
- Example:
```shell
$ python3 t_test.py file1 file2 -a 0.01 -d 0.04 -s -v 2 -p histogram fig_h.png
```
$\rightarrow$ Calculate t-statistic with significance level of 0.01 (or 1 %)
for each pair of data in `file1` and `file2` that are set to have discrepancy
of 0.04. Skip any mismatching data points. Display the number of pairs that
reject null hypothesis along with details of all rejected cases, and save a
histogram of p-values in `fig_h.png`.

### `test_twosample_ttest.py`

This is a unit test file, located in `tests` directory, invoked by *pytest*
that tests main t-test running functions in `twosample_ttest.py`

Usage:
```shell
$ pytest tests/test_twosample_ttest.py -vvv
```

## References

[[1]](https://blog.minitab.com/blog/adventures-in-statistics-2/understanding-t-tests-t-values-and-t-distributions)
[[2]](https://blog.minitab.com/blog/adventures-in-statistics-2/understanding-t-tests-1-sample-2-sample-and-paired-t-tests)
[[3]](https://blog.minitab.com/blog/adventures-in-statistics-2/understanding-hypothesis-tests-significance-levels-alpha-and-p-values-in-statistics)
[[4]](https://statisticsbyjim.com/hypothesis-testing/t-tests-t-values-t-distributions-probabilities/)
[[5]](https://towardsdatascience.com/inferential-statistics-series-t-test-using-numpy-2718f8f9bf2f)
[[6]](https://machinelearningmastery.com/how-to-code-the-students-t-test-from-scratch-in-python/)
[[7]](https://machinelearningmastery.com/critical-values-for-statistical-hypothesis-testing/)
[[8]](https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm)
[[9]](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm)
[[10]](https://www.itl.nist.gov/div898/handbook/prc/section1/prc131.htm)
[[12]](https://www.statisticshowto.com/what-is-an-alpha-level/)
[[13]](https://www.datasciencecentral.com/profiles/blogs/significance-level-vs-confidence-level-vs-confidence-interval)
[[14]](https://www.statsdirect.com/help/basics/p_values.htm)
[[15]](https://study.com/academy/lesson/z-test-t-test-similarities-differences.html)
[[16]](https://en.wikipedia.org/wiki/Student%27s_t-test)
[[17]](https://en.wikipedia.org/wiki/T-statistic)
[[18]](https://en.wikipedia.org/wiki/Test_statistic)
[[19]](https://en.wikipedia.org/wiki/Student%27s_t-distribution)
[[20]](https://en.wikipedia.org/wiki/Null_hypothesis)
[[21]](https://en.wikipedia.org/wiki/P-value)
[[22]](https://en.wikipedia.org/wiki/Standard_error#Standard_error_of_the_mean)