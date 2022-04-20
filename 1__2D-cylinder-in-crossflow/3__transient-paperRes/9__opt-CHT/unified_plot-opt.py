# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 10.03.2022
#
# Plot optimization OF and constraint as well as (left + right axis)
# as well as gradient norm over the design iterations.
# ------------------------------------------------------------------------------------- #

from cmath import nan
from numpy import NaN
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------------- #
# global variables
textwidth = 6.202
fig_width = textwidth # two images above one another
fig_height = textwidth
xmax = 14

# ------------------------------------------------------------------------------------- #

def postprocessData(df, dfkey, infeasibleValue):
    """
    Set row x-key ('ITER') to nan whenever an invalid desing is present
    Like so, the respective datapoint will be dropped in the plots and no line segment
    will be drawn.

    input
    df: dataframe containing the data
    dfkey: string containing the column in which the infeasible value should be searched
    infeasibleValue: value at which the ('ITER')-column entry is changed to nan
    -------
    return:
    altered dataframe
    """
    # Preprocess values: Drop infeasible designs from Dataframe
    # by setting the x-value of the plot to nan, the respective datapoint is dropeed from the plot
    df = df.reset_index()  # make sure indexes pair with number of rows
    df['ITER'] = df['ITER'].astype(float) # convert to float such that a nan can be specified -> not possible with int

    for index, row in df.iterrows():
       if(row[dfkey] == infeasibleValue):
           df.at[index, 'ITER'] = nan

    return df

if __name__=='__main__':
    hist_df = pd.read_csv('optim.csv')
    hist_df = postprocessData(hist_df, '  tavgT', 1000)
    df = hist_df[:xmax]
    # ------------------------------------------------------------------------------------- #
    # Plot 2 plots into same figure
    # https://matplotlib.org/stable/gallery/subplots_axes_and_figures/subplots_demo.html
    fig, axs = plt.subplots(2)
    #fig.suptitle('Optimization History')

    ax1 = axs[0]
    color = 'tab:red'
    #ax1.set_xlabel('Design Iteration')
    ax1.set_ylabel('OF value: Avg. Temp. [K]', color=color)
    ln1 = ax1.plot(df['ITER'].values-1, df['  tavgT'].values, # -1 to start at zero
             color=color,
             linestyle='-',
             linewidth=1,
             marker='o',
             markersize=4,
             clip_on=False,
             label="Obj. Func.")
    ax1.set_xlim((0,xmax-1))
    ax1.set_ylim((354.0,358.0))
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid()

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Constraint: Drag [-]', color=color)  # we already handled the x-label with ax1
    ln3 = ax2.axhline(y=1.332, color='black', linestyle='-', label="init. Constr.") # https://stackoverflow.com/questions/33382619/plot-a-horizontal-line-using-matplotlib
    ln2 = ax2.plot(df['ITER'].values-1, df['  drag'].values,
             color=color,
             linestyle='-',
             linewidth=1,
             marker='x',
             markersize=4,
             clip_on=False,
             label="Constraint")
    ax2.set_ylim((1.29,1.37))
    ax2.tick_params(axis='y', labelcolor=color)

    # See https://stackoverflow.com/questions/5484922/secondary-axis-with-twinx-how-to-add-to-legend
    # how to put legend of multiple axes intp one legend
    # added these three lines
    lns = ln1+ln2+[ln3] # ln3 is not a list by default but the others are
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0, framealpha=1, frameon=True)

    # ------------------------------------------------------------------------------------- #

    gradnorm_df = pd.read_csv('gradient_norm.csv')
    gradnorm_df = postprocessData(gradnorm_df, 'avgT-gradNorm', nan)
    df = gradnorm_df[:xmax]
    # ------------------------------------------------------------------------------------- #

    ax1 = axs[1]
    color = 'tab:red'
    ax1.set_xlabel('Design Iteration')
    #ax1.set_ylabel('OF gradient [K/m]', color=color)
    ax1.set_ylabel('||G||/||G_0||')
    ax1.plot(df['ITER'].values, df['avgT-gradNorm'].values / df['avgT-gradNorm'].values[0],
             color=color,
             linestyle='-',
             linewidth=1,
             marker='o',
             markersize=4,
             clip_on=False,
             label="normalized OF gradient")
    ax1.set_xlim((0,xmax-1))
    ax1.set_ylim((0.8, 1.1))
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax1.tick_params(axis='y')#, labelcolor=color)
    ax1.grid()
    color = 'tab:blue'
    ax1.plot(df['ITER'].values, df['drag-gradNorm'].values / df['drag-gradNorm'].values[0],
            color=color,
            linestyle='-',
            linewidth=1,
            marker='x',
            markersize=4,
            clip_on=False,
            label="normalized Constr. gradient")
    ax1.legend(framealpha=1, frameon=True)

    # ------------------------------------------------------------------------------------- #    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.set_size_inches(w=fig_width, h=fig_height)
    plt.savefig('OF-and-Grad.png', bbox_inches='tight')#, dpi=100)
    plt.show()
    plt.cla()
    plt.close()
