# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 19.04.2022
#
# Plot shapes of the optimized geometry and the respective history.
# Additionally plot unconstrained optimas as well.
# ------------------------------------------------------------------------------------- #

import numpy as np
from matplotlib import colors
import pandas as pd
import matplotlib.pyplot as plt
import os
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
fig_width = textwidth # two images next to another
fig_height = textwidth / 2

# ------------------------------------------------------------------------------------- #

def create_folder_list(all=False, opt_history=False, cte_impact=False):
    """Return ordered list of strings with all folder names."""
    if(all):
        # create list with folder names
        baseFolder = "./"
        sub_folders = [name for name in os.listdir(baseFolder) if os.path.isdir(os.path.join(baseFolder, name))]
        DSN_folders = [folder for folder in sub_folders if 'DSN' in folder]
        # sort alphabetically as there were minor problems
        DSN_folders = sorted(DSN_folders)
    elif(opt_history):
        DSN_folders = ['DSN_004','DSN_005','DSN_001','DSN_006']
    elif(cte_impact):
        DSN_folders = ['DSN_004', 'DSN_005','DSN_001','DSN_006']
    else:
        raise Exception('Specify folders to be read.')

    return DSN_folders

def read_shapes(folder_list):
    """Read and process (i.e. mirror) all available shapes

    input:
    folder_list: list of strings with folder names.
    -------
    return: list of dataframes, each containing shape of respective design."""
    shapes = []
    for i, folder in enumerate(folder_list):
        try:
            shape = pd.read_csv(folder + '/DEFORM/shape0.csv')
            # Remove first 2 points, that are (-0.5,0.0) and (0.5,0.0), unwanted line through image
            shape.drop([0,1], inplace=True)
            # Add First point to the end of the df to close the shape
            # exract first row as dataframe https://stackoverflow.com/questions/16096627/selecting-a-row-of-pandas-series-dataframe-by-integer-index
            shape = pd.concat([shape, shape[0:1]])
            # Nondimensionalize data with pin radius (0.5[m])
            for field in ["Points:0","Points:1"]:
                shape[field] = shape[field] / 0.5
            shapes.append(shape)
            print(folder + ' done')
        except:
            #shapes.append(shapes[-1])
            print(folder + ' no bueno')

    return shapes


if __name__=='__main__':

    fig = plt.figure()
    gs = fig.add_gridspec(1, 2, wspace=0)
    (ax1, ax2) = gs.subplots(sharex=True, sharey=True)

    # ------------------------------------------------------------------------------------- #
    # Plot constrained shape with history
    shapes = read_shapes(create_folder_list(opt_history=True))

    labels = ['10-th Design','30-th Design','Initial','Optimized']
    farben = [str(0.6),str(0.3),'black','black'] 
    styles = ['-.','--',':','-']

    for i,shape in enumerate(shapes):
        ax1.plot(shape["Points:0"], shape["Points:1"],
                 label=labels[i],
                 color=farben[i],
                 linestyle=styles[i],
                 linewidth=1)

    # ------------------------------------------------------------------------------------- #
    # Plot cte opt with uncte opt and initial geo.
    shapes = read_shapes(create_folder_list(cte_impact=True))

    labels = ['avgT-optimized','dp-optimized','Initial','cte-optimized']
    farben = ['tab:red','tab:blue','black','black'] 
    styles = ['--','-.',':','-']

    for i,shape in enumerate(shapes):
        ax2.plot(shape["Points:0"], shape["Points:1"],
                 label=labels[i],
                 color=farben[i],
                 linestyle=styles[i],
                 linewidth=1)

    # ------------------------------------------------------------------------------------- #
    ax1.set_ylabel('y/r [-]')
    ax1.set_xlim((-1.5,1.5))
    # specify xticks to prevent overlap https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.pyplot.xticks.html
    ax1.set_xticks(np.arange(-1, 1+1e-12, step=0.5))
    ax1.set_ylim((-1.5,1.5))
    for ax in [ax1, ax2]:
        ax.set_aspect('equal', adjustable='box')
        ax.label_outer()
        ax.legend(framealpha=1, frameon=False)
        
        ax.set_xlabel('x/r [-]')  
        # Force a square plot https://www.delftstack.com/howto/matplotlib/how-to-make-a-square-plot-with-equal-axes-in-matplotlib/
        

    # ------------------------------------------------------------------------------------- #
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #fig.set_size_inches(w=fig_width, h=fig_height)
    plt.savefig('shapes.pgf', bbox_inches='tight')#, dpi=100)
    #plt.show()
    plt.cla()
    plt.close()
    print('End')
    