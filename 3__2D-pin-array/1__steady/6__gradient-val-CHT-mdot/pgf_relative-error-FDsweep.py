# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 24.04.2022
#
# Plot relative error over FD-stepsize  for 1 DV (or all).
# ------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})

matplotlib.rcParams['axes.unicode_minus'] = False

# ------------------------------------------------------------------------------------- #
# global variables
textwidth = 6.202
fig_width = textwidth  # two images above one another
fig_height = textwidth / 2 * 3/4

# ------------------------------------------------------------------------------------- #

def FD_error_plot(ax, df, chosenDV, FDstep, name):
    """
    Plot bar chart

    inputs
    ax: axes object
    df: pandas dataframe containing all the data.
    chosenDV: List of numbers with the Design variable ID's
    FDstep: List of number with the FD steps
    name: string which determines the linecolor
    """
    # Create list with column names
    FDstep_string= ['relDiff_' + str(step) for step in FDstep]
    x = FDstep

    style=['-','--']
    if(name=='avgT'):
      col = 'tab:red'
    elif(name=='dp'):
      col = 'tab:blue'

    for i,DV in enumerate(chosenDV):
        # Extract data for specific DV (rel. diff. = |gradFD - gradAD| / |gradAD|)_
        y = df.iloc[DV][FDstep_string].values

        # plot data onto axes
        ax.loglog(x, y,
                  label='DV ' + str(DV),
                  marker='o',
                  markersize=4,
                  color=col,
                  linestyle=style[i],
                  clip_on=False)


if __name__=='__main__':

    # Define for which DV's and for which FD-stepsize the plot should be created
    nDV= 7
    chosenDV= range(0, nDV, 1)[3:5]
    FDstep= [1e-4, 1e-05, 1e-06, 1e-07, 1e-08, 1e-09, 1e-10, 1e-11, 1e-12, 1e-13, 1e-14]

    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    # two subplots horizontally
    fig, (ax1, ax2) = plt.subplots(1, 2)

    avgt_df = pd.read_csv('gradient_data_avgt.csv')
    FD_error_plot(ax1, avgt_df, chosenDV, FDstep, 'avgT')

    dp_df = pd.read_csv('gradient_data_dp.csv')
    FD_error_plot(ax2, dp_df, chosenDV, FDstep, 'dp')

    for ax in [ax1, ax2]:
        ax.grid(True, which="both")
        ax.set_xlim((1e-14,1e-4))
        ax.set_ylim((1e-5,1e-0))
        ax.set_xlabel('FD stepsize [m]')
        ax.set_ylabel('|Sens_{FD} - Sens_{AD}| / Sens_{AD}')
        ax.legend(framealpha=1, frameon=True)

    plt.tight_layout()
    fig.set_size_inches(fig_width, fig_height)
    plt.savefig('FD_error_plot.pgf', bbox_inches='tight')
    show = False
    if(show): plt.show()
    plt.clf()
    plt.close()

    print('End')
