#!/usr/bin/python
"""Run two-sample t-tests on samples from two files.

Author: YoungHui Park

This is a wrapper script that runs 't_test' function from `twosample_ttest`
module.

Usage:
- `filenames`: Input data filenames. Must be two strings.
- `--alpha`(`-a`): Target significance level.
- `--discrepancy`(`-d`): Set discrepancy between two data set.
- `--skip`(`-s`): Skip mismatching data points instead of raising errors.
- `--verbose`(`-v`): Verbosity level of t-test result.
- `--plot`(`-p`): Plot style.
* $ python3 t_test.py file1 file2 -a 0.01 -d 0.04 -s -v 2 -p 'histogram'
  -> Calculate t-statistic with significance level of 0.01 (or 1 %)
  for each pair of data in `file1` and file2` that are set to have discrepancy
  of 0.04. Skip any mismatching data points. Display the number of pairs that
  reject null hypothesis along with details of all rejected cases, and plot a
  histogram of p-values.

"""

# Standard libraries.
import argparse

# Local modules.
from t_test.twosample_ttest import *


# Main.
if __name__ == """__main__""":
    parser = argparse.ArgumentParser(description="Run two-sample t-test.")

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

    parser.add_argument("--verbose", "-v", type=int, default=1,
                        help="Verbosity level of t-test result. " \
                        + "0: No summary displayed. " \
                        + "1: Display simple summary with rejection counts. " \
                        + "2: Display all rejected cases. " \
                        + "Default: {0}".format(DEFAULT_v))

    parser.add_argument("--plot", "-p", type=str, nargs=2,
                        metavar=("plot_type", "plot_filename"),
                        help="Plot two-sample t-test results. " \
                        + "Plot type choices: {0}, ".format(CHOICES_plot_type) \
                        + "Default filename: {0}".format(DEFAULT_plot_name))

    args = parser.parse_args()


    [file_1, file_2] = args.filenames

    data_1 = load_data(file_1)
    sample_1 = process_data(data_1)

    data_2 = load_data(file_2)
    sample_2 = process_data(data_2)

    stat = t_test(sample_1, sample_2, args.alpha, args.discrepancy, args.skip)

    if args.verbose:
        print_rej_summary(stat, args.alpha, args.discrepancy, args.verbose)

    if args.plot:
        (plot_type, plot_filename) = args.plot
        if plot_type == 'histogram':
            plot_p_hist(stat, args.alpha, plot_filename)
        elif plot_type == 'heatmap':
            (x, y, v, tt, xl, yl) = process_2dplot_input(stat)
            plot_p_2d(x, y, v, tt, xl, yl, args.alpha, plot_filename)
        print("Two-sample t-test results are plotted as {0} in {1}.".format(
            plot_type, plot_filename))
