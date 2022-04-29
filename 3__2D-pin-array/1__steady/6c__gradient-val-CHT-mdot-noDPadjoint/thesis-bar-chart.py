# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 10.03.2022
#
# Plot Bar chart with DA vs FD gradient comparison
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

def barchart(ax, df, ylabel, imageName, x='DV', y=['DAgrad']):
    """
    Plot bar chart
    
    inputs
    ax: axes object
    df: pandas dataframe containing all the data.
    ylabel: string for the plots ylabel
    imageName: name of the image written to disk
    x: single string for the x-axis keys (most likely 'DV')
    y: list of strings with the bars to be plotted (will most likely contain 'DAgrad')
    """
    # create plot
    index = np.arange(len(df[x].values)) # Here I could prob use df[x].values directly, makes a diff if DV does not start at 0
    bar_block_width = 0.8
    bar_width = bar_block_width/len(y) # i.e. one bar-block has the total-width of 0.7
    true_bar_width = bar_width*0.9 # one might want to have space between the bars of one block itself as well (1.0=no space)

    if(imageName=="avgt"):
        maincol = 'tab:red'
    elif(imageName=='dp'):
        maincol = 'tab:blue'
    colors = [maincol, 'white']
    labels = ['DA', 'FD (1e-12)']
    hatching = ['', '//']
    ecol = maincol

    for i,columnName in enumerate(y):
        # create x-array, values are middle points of the bars
        # "index - bar_block_width/2" is the left bar block border, but the first bar middle point ...
        # ... is of course half a bar_width to the right again
        # The i*bar_width then gives the offset for each individual bar (zero for the first)
        x_vals = (index - bar_block_width/2 + bar_width/2) + (i * bar_width)
        ax.bar(x_vals, df[columnName].values, true_bar_width,
                label=labels[i],
                color = colors[i], 
                hatch=hatching[i],
                edgecolor=ecol)

    if(imageName=="avgt"):
        ax.set_ylim((-6e3, 4e3))
    elif(imageName=="dp"):
        ax.set_ylim((-0.25e5, 1.75e5))

    ax.axhline(y=0.0, color='black', linestyle='-', linewidth=1)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.set_xticks(np.arange(min(df[x].values), max(df[x].values)+1, 1.0))
    ax.set_xlabel(x)
    ax.set_ylabel(ylabel)
    ax.legend(framealpha=1, frameon=True)
    ax.set_axisbelow(True) # otherwise grid is written above the the bars https://stackoverflow.com/questions/1726391/matplotlib-draw-grid-lines-behind-other-graph-elements
    ax.grid()


if __name__=='__main__':

    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    # two subplots horizontally
    fig, (ax1, ax2) = plt.subplots(1, 2)

    avgt_df = pd.read_csv('gradient_data_avgt.csv')
    barchart(ax1, avgt_df, "Avg. Temp. Gradient [K/m]", "avgt", y=['DAgrad','FDgrad_1e-12'])

    dp_df = pd.read_csv('gradient_data_dp.csv')
    barchart(ax2, dp_df, "Pressure Drop Gradient [Pa/m]", "dp", y=['DAgrad','FDgrad_1e-12'])

    plt.tight_layout()
    fig.set_size_inches(fig_width, fig_height)
    plt.savefig('GV.png', bbox_inches='tight', dpi=100)
    show = True
    if(show): plt.show()
    plt.clf()
    plt.close()

    print('End')
