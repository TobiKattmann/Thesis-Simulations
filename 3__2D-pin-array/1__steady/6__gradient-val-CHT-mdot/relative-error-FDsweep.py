# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 24.04.2022
#
# Plot relative error over FD-stepsize  for 1 DV (or all).
# ------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/30201310/use-of-hyphen-or-minus-sign-in-matplotlib-versus-compatibility-with-latex
# Ensures correct rendering of minus sign '-' in the Latex document
from matplotlib.ticker import FuncFormatter
def math_formatter(x, pos):
    return "%i" %x

# ------------------------------------------------------------------------------------- #
# global variables
textwidth = 6.202
fig_width = textwidth  # two images above one another
fig_height = textwidth / 2 * 3/4

# ------------------------------------------------------------------------------------- #

def FD_error_plot(ax, df, chosenDV, FDstep):
    """
    Plot bar chart

    inputs
    ax: axes object
    df: pandas dataframe containing all the data.
    chosenDV: List of numbers with the Design variable ID's
    FDstep: List of number with the FD steps
    """
    # Create list with column names
    FDstep_string= ['relDiff_' + str(step) for step in FDstep]
    x = FDstep

    for DV in chosenDV:
        # Extract data for specific DV (rel. diff. = |gradFD - gradAD| / |gradAD|)_
        y = df.iloc[DV][FDstep_string].values

        # plot data onto axes
        ax.loglog(x, y, label='DV' + str(DV))


if __name__=='__main__':

    # Define for which DV's and for which FD-stepsize the plot should be created
    nDV= 7
    chosenDV= range(0, nDV, 1)
    FDstep= [1e-05, 1e-06, 1e-07, 1e-08, 1e-09, 1e-10, 1e-11, 1e-12, 1e-13]

    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    # two subplots horizontally
    fig, (ax1, ax2) = plt.subplots(1, 2)

    avgt_df = pd.read_csv('gradient_data_avgt.csv')
    FD_error_plot(ax1, avgt_df, chosenDV, FDstep)

    dp_df = pd.read_csv('gradient_data_dp.csv')
    FD_error_plot(ax2, dp_df, chosenDV, FDstep)

    for ax in [ax1, ax2]:
        ax.grid(True, which="both")
        ax.set_xlim((1e-13,1e-5))
        ax.set_ylim((1e-5,1e-0))
        ax.legend()

    plt.tight_layout()
    fig.set_size_inches(fig_width, fig_height)
    plt.savefig('FD_error_plot.png', bbox_inches='tight', dpi=100)
    show = True
    if(show): plt.show()
    plt.clf()
    plt.close()

    print('End')
