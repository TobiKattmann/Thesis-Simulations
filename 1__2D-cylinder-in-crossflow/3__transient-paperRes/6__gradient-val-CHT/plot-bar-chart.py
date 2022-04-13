# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 10.03.2022
#
# Plot Bar chart with DA vs FD gradient comparison
# ------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------------- #

def barchart(df, ylabel, imageName, x='DV', y=['DAgrad'], show='False'):
    """
    Plot bar chart
    
    inputs
    df: pandas dataframe containing all the data.
    ylabel: string for the plots ylabel
    imageName: name of the image written to disk
    x: single string for the x-axis keys (most likely 'DV')
    y: list of strings with the bars to be plotted (will most likely contain 'DAgrad')
    show: whether to show a plot or not
    """
    # create plot
    fig, ax = plt.subplots()
    index = np.arange(len(df[x].values)) # Here I could prob use df[x].values directly, makes a diff if DV does not start at 0
    bar_block_width = 0.7 
    bar_width = bar_block_width/len(y) # i.e. one bar-block has the total-width of 0.7
    true_bar_width = bar_width*0.9 # one might want to have space between the bars of one block itself as well (1.0=no space)

    for i,columnName in enumerate(y):
        # create x-array, values are middle points of the bars
        # "index - bar_block_width/2" is the left bar block border, but the first bar middle point ...
        # ... is of course half a bar_width to the right again
        # The i*bar_width then gives the offset for each individual bar (zero for the first)
        x_vals = (index - bar_block_width/2 + bar_width/2) + (i * bar_width)
        plt.bar(x_vals, df[columnName].values, true_bar_width,
                label=columnName)

    plt.xlabel(x)
    plt.ylabel(ylabel)
    plt.title('Gradient validation')
    plt.legend()
    ax.set_axisbelow(True) # otherwise grid is written above the the bars https://stackoverflow.com/questions/1726391/matplotlib-draw-grid-lines-behind-other-graph-elements
    plt.grid()

    plt.tight_layout()
    fig.set_size_inches(10, 3)
    plt.savefig(imageName+'.png', bbox_inches='tight', dpi=100)
    if(show): plt.show()
    plt.clf()
    plt.close()

if __name__=='__main__':
    avgt_df = pd.read_csv('gradient_data_avgt.csv')
    barchart(avgt_df, "Avg. Temp. Gradient [K/m]", "avgt", y=['DAgrad','FDgrad_0.1','FDgrad_0.01','FDgrad_0.001','FDgrad_0.0001','FDgrad_1e-05','FDgrad_1e-06','FDgrad_1e-07','FDgrad_1e-08'])

    drag_df = pd.read_csv('gradient_data_drag.csv')
    barchart(drag_df, "Drag Gradient [-/m]", "drag", y=['DAgrad','FDgrad_0.1','FDgrad_0.01','FDgrad_0.001','FDgrad_0.0001','FDgrad_1e-05','FDgrad_1e-06','FDgrad_1e-07','FDgrad_1e-08'])
