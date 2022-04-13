# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 10.03.2022
#
# Plot optimization OF and constraint as well as (left + right axis)# as well as gradient norm over the design iterations.
# as well as gradient norm over the design iterations.
# ------------------------------------------------------------------------------------- #

from cmath import nan
from numpy import NaN
import pandas as pd
import matplotlib.pyplot as plt

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
       if(row[dfkey] >= infeasibleValue):
           df.at[index, 'ITER'] = nan

    return df

def plotOF(df):
    """
    Plot the OF and constraint value, use left and right axis for that

    input
    df: dataframe containing the data
    """
    # Plot https://matplotlib.org/stable/gallery/subplots_axes_and_figures/two_scales.html
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Design Iteration')
    ax1.set_ylabel('OF value: Avg. Temp. [K]', color=color)
    ax1.plot(df['ITER'].values, df['  tavgT'].values,
             color=color,
             linestyle='-',
             marker='o')
    #ax1.set_ylim((359.0,360.2))
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid()

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Constraint: Pressure Drop [Pa]', color=color)  # we already handled the x-label with ax1
    ax2.plot(df['ITER'].values, df['  drag'].values,
             color=color,
             linestyle='-',
             marker='x')
    #ax2.set_ylim((100.0,300.0))
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.axhline(y=1.3, color='black', linestyle='-') # https://stackoverflow.com/questions/33382619/plot-a-horizontal-line-using-matplotlib

    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #fig.set_size_inches(10, 3)
    plt.savefig('OF_constr.png', bbox_inches='tight')#, dpi=100)
    plt.show()
    plt.cla()
    plt.close()

def plotGradNorm(df):
    """
    Plot the gradient norm of OF and constraint value, use left and right axis for that

    input
    df: dataframe containing the data
    """
    # Plot https://matplotlib.org/stable/gallery/subplots_axes_and_figures/two_scales.html
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Design Iteration')
    ax1.set_ylabel('OF gradient [K/m]', color=color)
    ax1.plot(df['ITER'].values, df['avgT-gradNorm'].values,
             color=color,
             linestyle='-',
             marker='o')
    #ax1.set_ylim((359.0,360.2))
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid()

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('Constraint gradient [-/m]', color=color)  # we already handled the x-label with ax1
    ax2.plot(df['ITER'].values, df['drag-gradNorm'].values,
             color=color,
             linestyle='-',
             marker='x')
    #ax2.set_ylim((100.0,300.0))
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #fig.set_size_inches(10, 3)
    plt.savefig('gradNorm_OF_constr.png', bbox_inches='tight')#, dpi=100)
    plt.show()
    plt.cla()
    plt.close()
    

if __name__=='__main__':
    hist_df = pd.read_csv('optim.csv')
    hist_df = postprocessData(hist_df, '  tavgT', 1000.0)
    plotOF(hist_df)

    gradnorm_df = pd.read_csv('gradient_norm.csv')
    gradnorm_df = postprocessData(gradnorm_df, 'avgT-gradNorm', nan)
    plotGradNorm(gradnorm_df)
