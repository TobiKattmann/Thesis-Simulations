# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 24.04.2022
#
# Plot relative error over FD-stepsize  for 1 DV (or all).
# ------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
        ax.loglog(x, y,
                  label='DV ' + str(DV),
                  marker='x',
                  clip_on=False)


if __name__=='__main__':

    # Define for which DV's and for which FD-stepsize the plot should be created
    chosenDV= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    chosenDV= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    FDstep= [1e-01, 1e-02, 1e-03, 1e-04, 1e-05, 1e-06, 1e-07, 1e-08, 1e-09, 1e-10]

    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    # two subplots horizontally
    fig, (ax1, ax2) = plt.subplots(1, 2)

    avgt_df = pd.read_csv('gradient_data_avgt.csv')
    FD_error_plot(ax1, avgt_df, chosenDV, FDstep)

    dp_df = pd.read_csv('gradient_data_drag.csv')
    FD_error_plot(ax2, dp_df, chosenDV, FDstep)

    for ax in [ax1, ax2]:
        ax.grid(True, which="both")
        ax.set_xlim((1e-10,1e-1))
        ax.set_ylim((1e-9,1e-0))
        ax.set_xlabel('FD stepsize [m]')
        ax.set_ylabel('|Sens_{FD} - Sens_{AD}| / Sens_{AD}')
        ax.legend(framealpha=1, frameon=True)

    plt.tight_layout()
    fig.set_size_inches(fig_width, fig_height)
    plt.savefig('FD_error_plot.png', bbox_inches='tight')
    show = True
    if(show): plt.show()
    plt.clf()
    plt.close()

    print('End')
