# Heatmaps in matplotlib
Given X, Y, Z experimental data suited to heatmap plotting, one can follow the
steps in this notebook to get a surface plot with a colorbar.  This notebook
shows three varieties of surface plots using toy data.

For all plots, it first uses triangulation on the X, Y data to form a
triangular grid (and normalizes the colors to the z range).  There are three
methods used to plot the surface:
1. tricontourf
2. tripcolor with flat shading
3. tripcolor with Gourard shading
Note that the color bar is only smoothed with tripcolor.
