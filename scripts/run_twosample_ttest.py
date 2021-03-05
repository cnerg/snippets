#!/usr/bin/python3
"""Run two-sample t-tests on samples from two files.

Author: YoungHui Park

This script serves as a template for running two-sample t-tests by calling
't_test' function from `twosample_ttest` module.
Refer README.md in `t_test` directory for details.

Note:
The following functions are designed as an example for preparing data structured
for the main 't_test' function in `twosample_ttest` module.
One may want to change their implementations according to input data structure
of one's choice.
- load_data
- process_data
- process_2dplot_input

Usage:
- `filenames`: Input data filenames. Must be two strings.
- `--alpha`(`-a`): Target significance level.
- `--discrepancy`(`-d`): Set discrepancy between two data set.
- `--skip`(`-s`): Skip mismatching data points instead of raising errors.
- `--verbose`(`-v`): Verbosity level of t-test result.
- `--plot`(`-p`): Plot type and filename.
- `--entire`(`-e`): Trigger heatmap to show both accepted and rejected cases.
* $ python3 run_twosample_ttest.py file1 file2 -a 0.01 -d 0.04 -s -v 2 \
  -p histogram fig_h.png
  -> Calculate t-statistic with significance level of 0.01 (or 1 %)
  for each pair of data in `file1` and file2` that are set to have discrepancy
  of 0.04. Skip any mismatching data points. Display the number of pairs that
  reject null hypothesis along with details of all rejected cases, and save a
  histogram of p-values in `fig_h.png`.

Reproducing example:
Run the following commands in the root directory of `snippets` repo:
$ python3 scripts/run_twosample_ttest.py \
  t_test/example/flux_full-core.imsht t_test/example/flux_50cm-cut-core.imsht \
  -v 2 -s -p histogram ex-histogram_uwnr-flux-comp.png
$ python3 scripts/run_twosample_ttest.py \
  t_test/example/flux_full-core.imsht t_test/example/flux_50cm-cut-core.imsht \
  -v 2 -s -p heatmap ex-heatmap_uwnr-flux-comp_rej-focused.png
$ python3 scripts/run_twosample_ttest.py \
  t_test/example/flux_full-core.imsht t_test/example/flux_50cm-cut-core.imsht \
  -v 2 -s -p heatmap ex-heatmap_uwnr-flux-comp_acc-focused.png -e

"""

# Standard library imports.
import argparse

# Local module imports.
from t_test import twosample_ttest as tt


DEFAULT_plot_name = "plot_twosample-ttest.png"  # Default plot filename.
CHOICES_plot_type = ('histogram', 'heatmap')  # Plot style choices.


def load_data(filename):
    """Load data from a file.

    This function loads data from given file as is.

    Arguments:
        filename (str): Input filename.

    Returns:
        data (dict): Dictionary of parsed data.

    """
    print("- Loading data from '{0}'.".format(filename))

    with open(filename, 'r') as f:
        lines = f.readlines()

    data = {}
    for line in lines:
        tokens = line.split()
        if len(tokens) == 6:
            try:
                [e, x, y, z, res, rel] = [float(v) for v in line.split()]
            except ValueError:
                e = line.split()[0]
                [x, y, z, res, rel] = [float(v) for v in line.split()[1:]]
            if e == 5.000E-07 and z == 22.5:
                if res != 0.00000E+00 and rel != 0.00000E+00:
                    data[(x,y,z)] = [res, rel*res]
    return data


def process_data(rdata, default_n=1000):
    """Process data for t-value calculation.

    This function performs pre-processing of given raw data
    to calculate mean, standard error and sample size that are required for
    t-value calculation.

    Arguments:
        rdata (dict): Dictionary of raw data.
        default_n (int): Default sample size if not specified.
            Default = 30

    Returns:
        pdata (dict): Dictionary of processed data in the form of
            [mean, standard error, sample size].

    """
    print("- Processing loaded data.")

    pdata = {}
    for key, val in rdata.items():
        val.append(default_n)
        pdata[key] = val

    return pdata


def process_2dplot_input(stat):
    """Process data for 2D heatmap plot.

    This function processes t-test result data into proper input for
    `plot_p_2d` function that plots p-values in 2D heatmap.

    Arguments:
        stat (dict): Dictionary of {key, [t-vaue, degree of freedom, p-value,
            critical t-value, rejection boolean, RSEs]} pair.

    Returns:
        x (list): List of x-coordinates for scatter plot.
        y (list): List of y-coordinates for scatter plot.
        v (list): List of p-values to be displayed in color.
        tl (str): Figure title.
        xl (str): x-axis label.
        yl (str): y-axis label.

    """
    [x, y, v, tl, xl, yl] = [[], [], [], '', '', '']
    x = [key[0] for key in stat]
    y = [key[1] for key in stat]
    v = [val[2] for val in stat.values()]
    tl = "p-value Heatmap"
    xl = "X [cm]"
    yl = "Y [cm]"
    return (x, y, v, tl, xl, yl)


def run_ttest(args):
    """Wrapper for running two-sample t-test."""
    [file_1, file_2] = args.filenames

    data_1 = load_data(file_1)
    sample_1 = process_data(data_1)

    data_2 = load_data(file_2)
    sample_2 = process_data(data_2)

    stat = tt.t_test(sample_1, sample_2, args.alpha, args.discrepancy,
                     args.skip)

    if args.verbose:
        tt.print_rej_summary(stat, args.alpha, args.discrepancy, args.verbose)

    if args.plot:
        (plot_type, plot_filename) = args.plot
        if plot_type == 'histogram':
            tt.plot_p_hist(stat, args.alpha, plot_filename)
        elif plot_type == 'heatmap':
            (x, y, v, tl, xl, yl) = process_2dplot_input(stat)
            tt.plot_p_2d(x, y, v, tl, xl, yl, args.alpha, plot_filename,
                         reject_only=(not args.entire))
        print("- Two-sample t-test results are plotted as {0} in {1}.".format(
            plot_type, plot_filename))


def parse_cla():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run two-sample t-test.")

    parser.add_argument("filenames", type=str, nargs=2,
                        help="Input data filenames. Must be two strings.")

    parser.add_argument("--alpha", "-a", type=float, default=tt.DEFAULT_a,
                        help=("Target significance level. "
                              " Default: {0}").format(tt.DEFAULT_a))

    parser.add_argument("--discrepancy", "-d", type=float, default=tt.DEFAULT_d,
                        help=("Set discrepancy between two data set."
                              " Default: {0}").format(tt.DEFAULT_d))

    parser.add_argument("--skip", "-s", action='store_true',
                        help=("Skip mismatching data points instead of raising"
                              " errors."))

    parser.add_argument("--verbose", "-v", type=int, default=tt.DEFAULT_v,
                        help=("Verbosity level of t-test result."
                              " 0: No summary displayed."
                              " 1: Display simple summary with rejection"
                              " counts."
                              " 2: Display all rejected cases and relative"
                              " standard errors."
                              " Default: {0}").format(tt.DEFAULT_v))

    parser.add_argument("--plot", "-p", type=str, nargs=2,
                        metavar=("plot_type", "plot_filename"),
                        help=("Plot two-sample t-test results."
                              " Plot type choices: {0},"
                              " Default filename: {1}").format(
                                  CHOICES_plot_type, DEFAULT_plot_name))

    parser.add_argument("--entire", "-e", action='store_true',
                        help=("Trigger heatmap to show both accepted and"
                              " rejected cases instead of replacing accepted"
                              " cases with 'pass' marker."))

    args = parser.parse_args()
    return args


# Main.
if __name__ == """__main__""":
    args = parse_cla()
    run_ttest(args)
