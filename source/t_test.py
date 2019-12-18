#!/usr/bin/python
"""Run t-tests to determine if two sets of data are significantly different.

This script runs t-tests comparing two sets of data in two different files.
t-test is a statistical calculation that can be used to determine if there is a
statistically significant difference between two sample groups.
In this script, unpaired equal variance two-sample t-test will be conducted for
comparison of data that are assumed to be taken from an identical distribution.

Assumptions:
- Population follows normal distribution, or n_1 + n_2 > 40,
  where n_1 and n_2 are sample sizes of two data sets.
- Independent observations. (unpaired)
- Population variance is unknown.

Null hypothesis: (mean_1 - mean_2) = d
Alternate hypothesis: (mean_1 - mean_2) != d
  where mean_1 and mean_2 are sample means of two data sets and d is a set
  discrepancy between the two means.

Note:
- With a sample size approaching to infinity, t-distribution becomes
  z-distribution.

Usage:
- `filenames`: Input data filenames. Must be two strings.
- `--alpha`(`-a`): Target significance level.
- `--discrepancy`(`-d`): Set discrepancy between two data set.
* $ python3 t_test.py file1 file2 -a 0.001 -d 0.04
  -> Calculate t-statistic with significance level of 0.001 (or 0.1 %)
  for each pair of data in `file1` and file2` that are set to have discrepancy
  of 0.04. Count the number of pairs that reject null hypothesis, and plot a
  histogram of p-values.

"""

import argparse
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

DEFAULT_a = 0.05  # Default significance level.
DEFAULT_d = 0  # Default discrepancy between two means.


def load_data(filename):
    """Load data from a file.

    This function loads data from given file as is.

    Arguments:
        filename (str): Input filename.

    Returns:
        data (dict): Dictionary of parsed data.

    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    data = {}
    # Create a dictionary (`key`, `val`) where:
    # - key: Reference keyword for two-sample t-statistic calculation
    # - val: List of parsed data.
    # Example:
    # for line in lines[1:]:
    #     token = line.split()
    #     data[token[0]] = [float(token[1]), float(token[2])]

    return data


def process_data(rdata, default_n=1000):
    """Process data for t-statistic calculation.

    This function performs pre-processing of given raw data
    to calculate mean, standard error and sample size that are required for
    t-statistic calculation.

    Arguments:
        rdata (dict): Dictionary of raw data.
        default_n (int): Default sample size if not specified.

    Returns:
        pdata (dict): Dictionary of processed data in the form of
            [mean, standard error, sample size].

    """
    pdata = {}
    # Note that a t-statistic will be calculated for each pair of dictionary.
    # Example:
    # for key, val in rdata.items():
    #     val.append(default_n)
    #     pdata[key] = val

    return pdata


def check_data_matching(set_1, set_2):
    """Check if two sets of data match each other.

    This function checks if the keyword sets of two input data match each other.
    This is required for two-sample t-test.

    Arguments:
        set_1 (set): Set of keywords from first input data.
        set_2 (set): Set of keywords from second input data.

    Returns:
        None.

    """
    if set_1 != set_2:
        err_str = "Data set mismatching."
        if set_1 - set_2:
            err_str += " sample_1 missing {0}.".format(set_1 - set_2)
        if set_2 - set_1:
            err_str += " sample_2 missing {0}.".format(set_2 - set_1)
        raise KeyError(err_str)


def two_sample_t(m1, se1, m2, se2, d):
    """Calculate two-sample t-statistic.

    This function calculates t-statistic of two-samples comparison.

    Arguments:
        m1 (float): Sample mean of data 1.
        se1 (float): Estimated standard error of the mean of data 1.
        m2 (float): Sample mean of data 2.
        se2 (float): Estimated standard error of the mean of data 2.
        d (float): Set discrepancy between two input data, if any.

    Returns:
        t_stat (float): Calculated t-score.

    """
    t_stat = ((m1-m2)-d) / math.sqrt(se1**2+se2**2)
    return t_stat


def plot_p_hist(p_vals, alpha):
    """Plot histogram of calculated p-values.

    This function generates a historgam of p-values for further analysis.

    Arguments:
        p_vals (list): List of p-values.
        alpha (float): Significance level.

    Returns:
        None.

    """
    fig, ax = plt.subplots()

    nb = int(1.0/alpha)
    plt.hist(p_vals, bins=nb, range=[0.0, 1.0], ec='black')
    ax.axvline(x=alpha, color='red', linestyle="--")

    ax.grid(axis='y', alpha=0.5)
    ax.set_title("p-value Histogram (p <= {0}: Reject null)".format(alpha))
    ax.set_xlabel("p-value [-]")
    ax.set_xticks(np.arange(0.0, 1.0, step=alpha), minor=True)
    ax.set_ylabel("Counts [#]")
    plt.show()


def t_test(sample_1, sample_2, alpha, d):
    """Perform t-test.

    This is the main function to call sub-functions for performing t-test.

    Arguments:
        sample_1 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        sample_2 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        alpha (float): Significance level.
        d (float): Set discrepancy between two input data, if any.

    Returns:
        None.

    """

    check_data_matching(set(sample_1), set(sample_2))

    stat = {}
    for key in data_1:
        [m1, se1, n1] = sample_1[key]
        [m2, se2, n2] = sample_2[key]

        t_val = two_sample_t(m1, se1, m2, se2, d)
        df = n1 + n2 - 2  # Degree of freedom.
        p_val = (1 - stats.t.cdf(abs(t_val), df)) * 2  # Cumulative probability.

        # Critical t-value, two-tailed.
        t_crit = stats.t.ppf(1.0 - alpha/2.0, df)
        if abs(t_val) <= t_crit:
            reject = False
        else:
            reject = True

        stat[key] = (t_val, df, p_val, t_crit, reject)

    # Count rejections of null hypothesis.
    rejected = [key for key, val in stat.items() if val[4]]
    r_str = "t-test: {0} out of {1} cases reject null hypothesis (mean_1 - \
mean_2) = {2} with alpha = {3}\n".format(len(rejected), len(stat), d, alpha)
    r_str += "Rejected cases:"
    for key in rejected:
        r_str += "\n- '{0}' with p-value {1:.5e}".format(key, stat[key][2])
    print(r_str)

    # Plot histogram of p-values.
    p_vals = [val[2] for key, val in stat.items()]
    plot_p_hist(p_vals, alpha)


# Main.
if __name__ == """__main__""":
    parser = argparse.ArgumentParser(description="Run student's t-test.")

    parser.add_argument("filenames", type=str, nargs=2,
                        help="Input data filenames. Must be two strings.")

    parser.add_argument("--alpha", "-a", type=float, default=DEFAULT_a,
                        help="Target significance level. "\
                        + "Default: {0}".format(DEFAULT_a))

    parser.add_argument("--discrepancy", "-d", type=float, default=DEFAULT_d,
                        help="Set discrepancy between two data set. "\
                        + "Default: {0}".format(DEFAULT_d))

    args = parser.parse_args()


    [file_1, file_2] = args.filenames

    data_1 = load_data(file_1)
    sample_1 = process_data(data_1)

    data_2 = load_data(file_2)
    sample_2 = process_data(data_2)


    t_test(sample_1, sample_2, args.alpha, args.discrepancy)
