""" Simple module with data loading/processing functions for given example.

To reproduce the example output plots,
1. Add the line
  `from t_test.example.ex_data_process import load_data, process_data, process_2dplot_input`
  after the line `from t_test.twosample_ttest import *`
  in `run_twosample_ttest.py` script in `scripts` directory.
2. Run the following commands in the root directory of `snippet` repo:
  - $ python3 scripts/run_twosample_ttest.py t_test/example/flux_full-core.imsht \
      t_test/example/flux_50cm-cut-core.imsht -v 2 -s -p histogram ex-histogram_uwnr-flux-comp.png
  - $ python3 scripts/run_twosample_ttest.py t_test/example/flux_full-core.imsht \
      t_test/example/flux_50cm-cut-core.imsht -v 2 -s -p heatmap ex-heatmap_uwnr-flux-comp.png
  (Manually change 'reject_only' input argument in 'plot_p_2d' function to False
  and run the second command in order to reproduce the equivalent of
  'ex-heatmap_uwnr-flux-comp_reject-only-false.png')

"""


def load_data(filename):
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
    print("- Processing loaded data.")

    pdata = {}
    for key, val in rdata.items():
        val.append(default_n)
        pdata[key] = val

    return pdata


def process_2dplot_input(stat):
    [x, y, v, tt, xl, yl] = [[], [], [], '', '', '']
    x = [key[0] for key in stat]
    y = [key[1] for key in stat]
    v = [val[2] for val in stat.values()]
    tt = "p-value Heatmap"
    xl = "X [cm]"
    yl = "Y [cm]"
    return (x, y, v, tt, xl, yl)
