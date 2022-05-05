# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 03.05.2022
#
# Plot time history of Obj + Constr for separate Design.
# Additionally add vertical line where OF evaluation starts.
# Also plot FFT Analysis of several Designs
# ------------------------------------------------------------------------------------- #

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fft import plotFFT

import matplotlib
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})

matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['lines.linewidth'] = 1


# ------------------------------------------------------------------------------------- #
# Global vars
t = 'Time_Iter'
avgt = '   "AvgTemp[1]"   '
drag = '      "CD[0]"     '
num_splits = 3 # of the data for FFT analysis

# ------------------------------------------------------------------------------------- #
if __name__=='__main__':
    # Init fig obj
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, gridspec_kw={'width_ratios': [3, 1]})

    # Load and plot Time series Data for multiple Designs
    folders = ['DSN_001','DSN_051']
    name = ['Initial','cte-Optimized']
    ls = ['--', '-']
    offset = [0.0, 0.0]#[-3.65, 0.0]

    for i,folder in enumerate(folders):
        df = pd.read_csv(folder + '/DIRECT/chtMaster.csv')

        col = 'tab:red'
        ln1 = ax1.plot(df[t], df[avgt] + offset[i],
                color=col,
                linestyle=ls[i],
                label=name[i])
        ax1.set_ylim((353.0,358.0))

        plotFFT(ax2, np.split(df[avgt].values, num_splits)[num_splits-1], "AvgT", ls=ls[i], col=col)

        col = 'tab:blue'
        ln2 = ax3.plot(df[t], df[drag],
                color=col,
                linestyle=ls[i],
                label=name[i])
        ax3.set_ylim((1.30,1.38))

        plotFFT(ax4, np.split(df[drag].values, num_splits)[num_splits-1], "Drag", ls=ls[i], col=col)

    # Horizontal Constr Line
    ln3 = ax3.axhline(y=1.332,
            color='black',
            linestyle='-',
            label="init. Constr.")
    # Vertical Opt window start line
    for ax in [ax1, ax3]:
        ax.axvline(x=612,
            color='black',
            linestyle=':')
    # Add text into plot and arrow to indicate opt window
    # https://stackoverflow.com/questions/53740340/how-to-add-text-to-an-image-segment
    # https://stackoverflow.com/questions/25761717/matplotlib-simple-and-two-head-arrows
    if(True):
        height = 355
        ax1.text(670, height+0.3, 'Optimization\nWindow')
        ax1.annotate('', xy=(611, height), xytext=(917, height),
                arrowprops=dict(arrowstyle='<->',
                color='black', linewidth=0.5))
    if(True):
        height = 1.355
        ax3.text(670, height+0.005, 'Optimization\n    Window')
        ax3.annotate('', xy=(611, height), xytext=(917, height),
                arrowprops=dict(arrowstyle='<->',
                color='black', linewidth=0.5))

    # Add legends
    ax1.legend(loc='center left', bbox_to_anchor=(0.2,0.5))
    ax3.legend(loc=0, framealpha=1, frameon=True)

    for ax in [ax2, ax4]:
        ax.set_xlim((0,0.0002))

    ax1.set_ylabel('Avg Temperature [K]')
    ax3.set_ylabel('Drag [-]')
    for ax in [ax1, ax3]:
        ax.set_xlabel('Time Iter')
        ax.set_xlim((0,max(df[t])))

    # ------------------------------------------------------------------------------------- #
    fig.tight_layout()
    plt.savefig('time-hist.pgf', bbox_inches='tight')
    plt.cla()
    plt.close()
