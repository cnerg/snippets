"""Run t-tests to determine if two sets of data are significantly different.

Author: YoungHui Park

This module runs t-tests comparing two samples.
t-test is a statistical calculation that can be used to determine if there is a
statistically significant difference between two samples.
In this module, unpaired equal variance two-sample t-test will be conducted for
comparison of data that are hypothesized to be taken from an identical
distribution.

Two dictionaries are provided as input of the main 't_test' function with the
form {key: [Sample mean, Estimated standard error of the mean, sample size]}.
The function calculates a t-value along with associated p-value and critical
value for each keyed pair, using the sample data and significance level.
Then it determines whether the null hypothesis is rejected or accepted by
comparing p-value with significance level (or alternatively, t-value with
critical value).
Further, it calculates relative standard error for each sample to provide
information on the reliability of sample data.
Finally, it returns a dictionary with summaries of t-test in the form of
{key: (t-value, degrees of freedom, p-value, critical value, reject/accept,
relative standard errors)}.

Assumptions:
- Population follows normal distribution, or n_1 + n_2 > 40,
  where n_1 and n_2 are sample sizes of two data sets.
- Independent observations. (unpaired)
- Population variance is unknown.

Null hypothesis: (mean_1 - mean_2) = d
Alternate hypothesis: (mean_1 - mean_2) != d
  where mean_1 and mean_2 are sample means of two data sets and d is a set
  discrepancy between the two means.

Usage:
from t_test import twosample_ttest as tt
stat = tt.t_test(sample_1, sample_2, alpha, d, skip)

Following functions are included in this module:
- calc_rse
- print_rej_summary
- plot_p_hist
- plot_p_2d
- check_input_args
- check_data_matching
- calc_twosample_tvalue
- t_test (top-level)

"""

# Third party imports.
from matplotlib import colors
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

DEFAULT_a = 0.05  # Default significance level.
DEFAULT_d = 0  # Default discrepancy between two means.
DEFAULT_n = 30  # Default sample size, if not specified.
DEFAULT_v = 1  # Default verbosity level.
DEFAULT_s = False  # Default boolean to skip mismatching keywords.
DEFAULT_ro = True  # Default boolean for heatmap to plot only rejected cases.

NDIGITS = 5  # Default precision after the decimal point.

DEFAULT_figsize = np.array((6.4, 4.8))
DEFAULT_fontsize_title = 12
DEFAULT_fontsize = 10
DEFAULT_markersize = 36
DEFAULT_cticknum = 6
DEFAULT_figscale = 1.0


def print_rej_summary(stat, alpha, d, verbose=DEFAULT_v):
    """Print summary of null hypothesis rejection results.

    This function counts rejections of null hypothesis and prints the summary.

    Arguments:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean, RSEs]} pair.
        alpha (float): Significance level.
        d (float): Set discrepancy between two input data.
        verbose (int): Integer indicating verbosity level of t-test result.
            0: No summary displayed.
            1: Display simple summary with rejection counts.
            2: Display all rejected cases and relative standard errors.
            * Default: 1

    Returns:
        None.

    """
    rejected = [key for key, val in stat.items() if val[4]]
    r_str = ("- test result: {0} out of {1} cases reject null hypothesis"
             " (mean_1 - mean_2) = {2} with alpha = {3}").format(
                 len(rejected), len(stat), d, alpha)
    if verbose > 1:
        # Rejected cases.
        r_str += "\n  Rejected cases:"
        for key in rejected:
            r_str += "\n  '{0}' with p-value {1:.5e}".format(key, stat[key][2])
        # Relative standard errors.
        r_str += "\n  Relative standard errors:"
        for key, val in stat.items():
            [rse1, rse2] = val[-1]
            r_str += "\n  '{0}' - sample_1: {1:.3f} %, sample_2: {2:.3f} %"\
                .format(key, rse1, rse2)
    print(r_str)


def plot_p_hist(stat, alpha, plot_fname, fig_scale=DEFAULT_figscale):
    """Plot histogram of calculated p-values.

    This function generates a historgam of p-values for further analysis.

    Arguments:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean, RSEs]} pair.
        alpha (float): Significance level.
        plot_fname (str): Filename for the output histogram.
        fig_scale (float): Scale of output figure relative to default setting.
            * Default: 1.0

    Returns:
        None.

    """
    fig, ax = plt.subplots(figsize=DEFAULT_figsize*fig_scale)

    p_vals = [val[2] for key, val in stat.items()]
    # Set the number of bins according to the alpha value,
    # so that all rejecting cases fall into a single bin,
    # giving the total number of rejecting case at once.
    nb = int(1.0/alpha)
    plt.hist(p_vals, bins=nb, range=[0.0, 1.0], ec='black',
             linewidth=1.0*fig_scale)

    # Draw a vertical line at the boundary of rejection/acceptance.
    ax.axvline(x=alpha, color='red', linestyle="--",
               linewidth=1.5*fig_scale)

    # Grid and tick settings.
    ax.grid(axis='y', alpha=0.5, linewidth=0.75*fig_scale)
    ax.set_xticks(np.arange(0.0, 1.0, step=alpha), minor=True)
    ax.tick_params(axis='x', labelsize=DEFAULT_fontsize*fig_scale)
    ax.tick_params(axis='y', labelsize=DEFAULT_fontsize*fig_scale)

    # Label settings.
    ax.set_title("p-value Histogram (p <= {0}: Reject null)".format(alpha),
                 fontsize=DEFAULT_fontsize_title*fig_scale)
    ax.set_xlabel("p-value [-]", fontsize=DEFAULT_fontsize*fig_scale)
    ax.set_ylabel("Counts [#]", fontsize=DEFAULT_fontsize*fig_scale)

    plt.savefig(plot_fname)


def plot_p_2d(x, y, v, tl, xl, yl, alpha, plot_fname,
              reject_only=DEFAULT_ro, fig_scale=DEFAULT_figscale):
    """Plot calculated p-values in 2D heatmap.

    This function generates a 2D heatmap of p-values.

    Arguments:
        x (list): List of x-coordinates for scatter plot.
        y (list): List of y-coordinates for scatter plot.
        v (list): List of p-values to be displayed in color.
        tl (str): Figure title.
        xl (str): x-axis label.
        yl (str): y-axis label.
        alpha (float): Significance level.
        plot_fname (str): Filename for the output histogram.
        reject_only (bool): True if sequential heatmap is generated for rejected
            cases (p <= alpha) and accepted cases (p > alpha) are replaced by
            'pass' marker (tri_down), False if diverging heatmap is generated
            over the entire range with center color set to be the alpha value
            (Note that this can lead to significantly different color scales
            between rejected cases and accepted cases.).
            * Default: True
        fig_scale (float): Scale of output figure relative to default setting.
            * Default: 1.0

    Returns:
        None.

    """
    fig, ax = plt.subplots(figsize=DEFAULT_figsize*fig_scale)
    x = np.array(x)
    y = np.array(y)
    v = np.array(v)

    if reject_only:
        # Rejection-focused mode.
        # Simply mark as 'Pass' for accepting cases,
        # but detail the range of p-values for rejecting cases.

        # Separate rejecting cases from accepting cases.
        xp = x[v>alpha]
        yp = y[v>alpha]
        vp = v[v>alpha]
        xr = x[v<=alpha]
        yr = y[v<=alpha]
        vr = v[v<=alpha]

        # Use a single 'Y' marker for all accepting cases.
        ax.scatter(xp, yp, marker='1', label='Pass',
                   c='k', linewidth=1.5*fig_scale,
                   s=DEFAULT_markersize*fig_scale**2)
        ax.legend(loc=(1.0, 1.02), fontsize=DEFAULT_fontsize*fig_scale)

        # Give colors according to their p-values for all rejecting case.
        im = ax.scatter(xr, yr, c=vr, cmap='viridis', marker="s",
                        vmin=0, vmax=alpha, s=DEFAULT_markersize*fig_scale**2)
        cticks = np.linspace(0, alpha, DEFAULT_cticknum)
    else:
        # Acceptance-focused mode.
        # Detail the full range of p-values for both rejecting and accepting
        # cases, possibly losing much information on rejecting cases.

        # Use the alpha value as a diverging point.
        divnorm = colors.TwoSlopeNorm(vcenter=alpha)
        im = ax.scatter(x, y, c=v, cmap='seismic_r', norm=divnorm, marker='s',
                        edgecolors='k', linewidth=0.4,
                        s=DEFAULT_markersize*fig_scale**2)
        cticks = sorted(np.append(np.linspace(0, 1, 11), alpha))

    # Color bar settings.
    cb = fig.colorbar(im, ax=ax, ticks=cticks)
    cb.set_label(label='p-value [-]', fontsize=DEFAULT_fontsize*fig_scale)
    cb.ax.tick_params(labelsize=DEFAULT_fontsize*fig_scale)

    # Tick settings.
    ax.tick_params(axis='x', labelsize=DEFAULT_fontsize*fig_scale)
    ax.tick_params(axis='y', labelsize=DEFAULT_fontsize*fig_scale)

    # Label settings.
    ax.set_title(tl, fontsize=DEFAULT_fontsize_title*fig_scale)
    ax.set_xlabel(xl, fontsize=DEFAULT_fontsize*fig_scale)
    ax.set_ylabel(yl, fontsize=DEFAULT_fontsize*fig_scale)

    plt.savefig(plot_fname)


def check_input_args(sample_1, sample_2, alpha, d, skip):
    """Check if valid input arguments are provided.

    This function checks if valid input arguments are provided.

    Arguments:
        sample_1 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        sample_2 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        alpha (float): Significance level.
        d (float): Set discrepancy between two input data.
        skip (bool): Boolean to skip mismatching keywords.

    Returns:
        None.

    """
    # Check input data for which t-test will be performed.
    for i, sample in enumerate([sample_1, sample_2]):
        sn = "sample_{0}".format(i+1)
        if not isinstance(sample, dict):
            raise TypeError("{0} must be a dictionary.".format(sn))
        for key, val in sample.items():
            if not isinstance(val, list) or len(val) != 3:
                raise TypeError(("{0}: Value of key '{1}' must be a list"
                                 " with 3 elements. Check t_test docstring"
                                 " for valid input.").format(sn, key))
            if not all(isinstance(v, (float, int)) for v in val):
                raise TypeError(("{0}: Value of key '{1}' must be a list"
                                 " of floats or ints.").format(sn, key))

    # Check significance level.
    if not isinstance(alpha, (float)):
        raise TypeError("alpha must be a float.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1) range.")

    # Check discrepancy set between two input data.
    if not isinstance(d, (float, int)):
        raise TypeError("d must be a float or an int.")

    # Check the boolean to skip mismatching keywords.
    if not isinstance(skip, bool):
        raise TypeError("skip must be a boolean.")


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
        err_str = "  Data set mismatching."
        if set_1 - set_2:
            err_str += " sample_1 missing {0}.".format(set_1 - set_2)
        if set_2 - set_1:
            err_str += " sample_2 missing {0}.".format(set_2 - set_1)

        common_set = set_1 & set_2

        if skip:
            err_str += "\n  Mismatching keys will be skipped."
            print(err_str)
        else:
            raise KeyError(err_str)

    return common_set


def calc_rse(m, sem):
    """Calculate relative standard error (RSE).

    This function calculates relative standard error using
    given mean and standard error of the mean.

    Arguments:
        m (float): Mean of a sample.
        sem (float): Standard error of the mean.

    Returns:
        rse (float): Relative standard error of the mean.

    """
    rse = round(sem / m * 100, NDIGITS - 2)  # Unit: %
    return rse


def calc_twosample_tvalue(m1, sd1, n1, m2, sd2, n2, d):
    """Calculate two-sample t-value.

    This function calculates t-value for two-sample pooled t-test
    (equal variance).

    Arguments:
        m1 (float): Mean of sample 1.
        sd1 (float): Standard deviation of sample 1.
        n1 (float): Size of sample 1.
        m2 (float): Mean of sample 2.
        sd2 (float): Standard deviation of sample 2.
        n2 (float): Size of sample 2.
        d (float): Set discrepancy between two input data.

    Returns:
        t_val (float): Calculated t-value.

    """
    sp = np.sqrt(((n1-1)*sd1**2+(n2-1)*sd2**2) / (n1+n2-2))
    t_val = ((m1-m2)-d) / (sp*np.sqrt(1/n1+1/n2))
    return round(t_val, NDIGITS)


def t_test(sample_1, sample_2, alpha=DEFAULT_a, d=DEFAULT_d, skip=DEFAULT_s):
    """Perform t-test.

    This is the main function to call sub-functions for performing t-test.

    Arguments:
        sample_1 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        sample_2 (dict): Dictionary of {key: [Sample mean, Estimated standard
            error of the mean, sample size]} pair.
        alpha (float): Significance level.
            * Default: 0.05
        d (float): Set discrepancy between two input data, if any.
            * Default: 0
        skip (bool): Boolean to skip mismatching keywords.
            * Default: False

    Returns:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean, RSEs]} pair.

    """
    print("- Running two-sample t-test.")

    check_input_args(sample_1, sample_2, alpha, d, skip)
    key_set = check_data_matching(set(sample_1), set(sample_2), skip)

    stat = {}
    for key in key_set:
        [m1, sem1, n1] = sample_1[key]
        [m2, sem2, n2] = sample_2[key]
        rse1 = calc_rse(m1, sem1)
        rse2 = calc_rse(m2, sem2)

        # Convert estimated standard error of the mean (type of data typically
        # provided by Monte Carlo codes such as MCNP as uncertainty of
        # calculations) to sample standard deviation (type of data required by
        # t-value calculation).
        sd1 = sem1 * np.sqrt(n1)
        sd2 = sem2 * np.sqrt(n2)

        t_val = calc_twosample_tvalue(m1, sd1, n1, m2, sd2, n2, d)
        df = n1 + n2 - 2  # Degree of freedom.
        p_val = (1 - stats.t.cdf(abs(t_val), df)) * 2  # Cumulative probability.

        # Critical t-value, two-tailed.
        t_crit = round(stats.t.ppf(1.0 - alpha/2.0, df), NDIGITS)
        reject = abs(t_val) > t_crit

        stat[key] = (t_val, df, p_val, t_crit, reject, [rse1, rse2])

    return stat
