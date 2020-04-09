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
from matplotlib import colors
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


def process_2dplot_input(stat):
    """Process data for 2D heatmap plot.

    This function processes t-test result data into proper input for
    `plot_p_2d` function that plots p-values in 2D heatmap.

    Arguments:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean]} pair.

    Returns:
        x (list): List of x-coordinates for scatter plot.
        y (list): List of y-coordinates for scatter plot.
        v (list): List of p-values to be displayed in color.
        tt (str): Figure title.
        xl (str): x-axis label.
        yl (str): y-axis label.

    """
    x = [key[0] for key in stat]
    y = [key[1] for key in stat]
    v = [val[2] for val in stat.values()]
    tt = 'F'
    xl = "X"
    yl = "Y"
    return (x, y, v, tt, xl, yl)


def check_data_matching(set_1, set_2, skip):
    """Check if two sets of data match each other.

    This function checks if the keywords set of two input data match each other.
    If 'skip' is True, a set of keywords common to both input data are returned,
    meaning that mismatching keywords will be skipped without raising errors.
    If 'skip' is False, any mismatching keyword on either of two input data will
    raise KeyError with information on which keywords are missing on the data.

    Arguments:
        set_1 (set): Set of keywords from first input data.
        set_2 (set): Set of keywords from second input data.
        skip (bool): Boolean to skip mismatching keywords.

    Returns:
        common_set (set): Set of keywords common to set_1 and set_2.

    """
    common_set = set_1

    if set_1 != set_2:
        err_str = "Data set mismatching."
        if set_1 - set_2:
            err_str += " sample_1 missing {0}.".format(set_1 - set_2)
        if set_2 - set_1:
            err_str += " sample_2 missing {0}.".format(set_2 - set_1)

        common_set = set_1 & set_2

        if skip:
            err_str += "\nMismatching keys will be skipped."
            print(err_str)
        else:
            raise KeyError(err_str)

    return common_set


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


def print_rej_summary(stat, alpha, d):
    """Print summary of null hypothesis rejection results.

    This function counts rejections of null hypothesis and prints the summary.

    Arguments:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean]} pair.
        alpha (float): Significance level.
        d (float): Set discrepancy between two input data, if any.

    Returns:
        None.

    """
    rejected = [key for key, val in stat.items() if val[4]]
    r_str = "t-test: {0} out of {1} cases reject null hypothesis (mean_1 - \
mean_2) = {2} with alpha = {3}\n".format(len(rejected), len(stat), d, alpha)
    r_str += "Rejected cases:"
    for key in rejected:
        r_str += "\n- '{0}' with p-value {1:.5e}".format(key, stat[key][2])
    print(r_str)


def plot_p_hist(stat, alpha):
    """Plot histogram of calculated p-values.

    This function generates a historgam of p-values for further analysis.

    Arguments:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean]} pair.
        alpha (float): Significance level.

    Returns:
        None.

    """
    fig, ax = plt.subplots()

    p_vals = [val[2] for key, val in stat.items()]
    nb = int(1.0/alpha)
    plt.hist(p_vals, bins=nb, range=[0.0, 1.0], ec='black')
    ax.axvline(x=alpha, color='red', linestyle="--")

    ax.grid(axis='y', alpha=0.5)
    ax.set_title("p-value Histogram (p <= {0}: Reject null)".format(alpha))
    ax.set_xlabel("p-value [-]")
    ax.set_xticks(np.arange(0.0, 1.0, step=alpha), minor=True)
    ax.set_ylabel("Counts [#]")
    plt.show()


def plot_p_2d(x, y, v, tt, xl, yl, alpha, reject_only=True):
    """Plot calculated p-values in 2D heatmap.

    This function generates a 2D heatmap of p-values.

    Arguments:
        x (list): List of x-coordinates for scatter plot.
        y (list): List of y-coordinates for scatter plot.
        v (list): List of p-values to be displayed in color.
        tt (str): Figure title.
        xl (str): x-axis label.
        yl (str): y-axis label.
        alpha (float): Significance level.
        reject_only (bool): True if sequential heatmap is generated for rejected
            cases (p <= alpha) and accepted cases (p > alpha) are replaced by
            'pass' marker (tri_down), False if diverging heatmap is generated
            over the entire range with center color set to be the alpha value
            (Note that this can lead to significantly different color scales
            between rejected cases and accepted cases.).

    Returns:
        None.

    """
    fig, ax = plt.subplots()
    x = np.array(x)
    y = np.array(y)
    v = np.array(v)

    if reject_only:
        xp = x[v>alpha]
        yp = y[v>alpha]
        vp = v[v>alpha]
        xr = x[v<=alpha]
        yr = y[v<=alpha]
        vr = v[v<=alpha]
        ax.scatter(xp, yp, c='k', marker='1', label='Pass')
        ax.legend(loc=(1.0, 1.0))
        im = ax.scatter(xr, yr, c=vr, cmap='viridis', marker="s",
                        vmin=0, vmax=alpha)
        cticks = np.linspace(0, alpha, 6)
    else:
        divnorm = colors.TwoSlopeNorm(vcenter=alpha)
        im = ax.scatter(x, y, c=v, cmap='seismic_r', norm=divnorm, marker='s',
                        edgecolors='k', linewidth=0.2)
        cticks = sorted(np.append(np.linspace(0, 1, 11), alpha))

    ax.set_title(tt)
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    fig.colorbar(im, ax=ax, ticks=cticks)

    plt.show()


def t_test(sample_1, sample_2, alpha, d, skip, summary=True):
    """Perform t-test.

    This is the main function to call sub-functions for performing t-test.

    Arguments:
        sample_1 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        sample_2 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        alpha (float): Significance level.
        d (float): Set discrepancy between two input data, if any.
        skip (bool): Boolean to skip mismatching keywords.
        summary (bool): Boolean to print summary of null hypothesis rejections.
            Default = True

    Returns:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean]} pair.

    """
    key_set = check_data_matching(set(sample_1), set(sample_2), skip)

    stat = {}
    for key in key_set:
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

    if summary:
        print_rej_summary(stat, alpha, d)

    return stat


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

    parser.add_argument("--skip", "-s", action='store_true',
                        help="Skip mismatching data points instead of raising" \
                        + " errors.")

    args = parser.parse_args()


    [file_1, file_2] = args.filenames

    data_1 = load_data(file_1)
    sample_1 = process_data(data_1)

    data_2 = load_data(file_2)
    sample_2 = process_data(data_2)

    stat = t_test(sample_1, sample_2, args.alpha, args.discrepancy, args.skip)

    plot_p_hist(stat, args.alpha)
