#!/usr/bin/python

# Standard libraries.
import argparse

# Local modules.
from t_test.t_test import *


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

    parser.add_argument("--verbose", "-v", type=int, default=1,
                        help="Verbosity level of t-test result. " \
                        + "0: No summary displayed. " \
                        + "1: Display simple summary with rejection counts. " \
                        + "2: Display all rejected cases. " \
                        + "Default: {0}".format(DEFAULT_v))

    parser.add_argument("--plot", "-p", type=str, choices=CHOICES_plot,
                        default=DEFAULT_plot,
                        help="Plot style. Choices: {0} ".format(CHOICES_plot) \
                        + "Default: {0}".format(DEFAULT_plot))

    args = parser.parse_args()


    [file_1, file_2] = args.filenames

    data_1 = load_data(file_1)
    sample_1 = process_data(data_1)

    data_2 = load_data(file_2)
    sample_2 = process_data(data_2)

    stat = t_test(sample_1, sample_2, args.alpha, args.discrepancy, args.skip)

    if args.verbose:
        print_rej_summary(stat, args.alpha, args.discrepancy, args.verbose)

    if args.plot == 'histogram':
        plot_p_hist(stat, args.alpha)
    elif args.plot == 'heatmap':
        (x, y, v, tt, xl, yl) = process_2dplot_input(stat)
        plot_p_2d(x, y, v, tt, xl, yl, args.alpha)
