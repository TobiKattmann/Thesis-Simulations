# ------------------------------------------------------------------------------------- #
# 02.05.2022 T. Kattmann
#
# Plot FFD boxes of initial and optimized geometries together with their respective shape.
# ------------------------------------------------------------------------------------- #

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection, LineCollection

# ------------------------------------------------------------------------------------- #
# Global variables
pin_radius = 0.5

# ------------------------------------------------------------------------------------- #

def read_shape(folder):
    """Read and process (i.e. mirror) all available shapes

    input:
    folder_list: string with folder names.
    -------
    return: list of dataframes, each containing shape of respective design."""
    try:
        shape = pd.read_csv(folder + '/DEFORM/shape0.csv')
        # Rename x and y coord columns appropriately
        shape.rename(columns={'Points:0':'x', 'Points:1':'y'}, inplace=True)
        # Remove first 2 points, that are (-0.5,0.0) and (0.5,0.0), unwanted line through image
        shape.drop([0,1], inplace=True)
        # Add First point to the end of the df to close the shape
        # exract first row as dataframe https://stackoverflow.com/questions/16096627/selecting-a-row-of-pandas-series-dataframe-by-integer-index
        shape = pd.concat([shape, shape[0:1]])
        # Nondimensionalize data with pin radius (0.002[m])
        for field in ['x','y']:
            shape[field] = shape[field] / pin_radius

        return shape
    except:
        print(folder + ' no bueno')

def read_FFD_box(filename):
    """
    Get the FFD box points and return reshaped x,y arrays.

    input:
    filename: string with relative file location of the Design
    -------
    return: np.ndarray with x,y point locations
    """
    filename += '/DEFORM/ffd_boxes_def_0.vtk'
    # Read the ffd-box, get the grid dimensions and store away. Data is read below
    df = pd.read_csv(filename)
    grid_dimension = df.iloc[3].values[0].split()[1:]
    grid_dimension = [int(val) for val in grid_dimension]
    # Read the ffd box Strip unnecessary stuff from beginning of file
    df = pd.read_csv(filename, sep='\t', skiprows=(0,1,2,3,4,5), header=None)
    df.columns = ['x', 'y', 'z']
    # reshape x and y array according to the grid_dimensions (necessary for plotting)
    x = np.reshape(df['x'].values, (grid_dimension[1], grid_dimension[0]))
    y = np.reshape(df['y'].values, (grid_dimension[1], grid_dimension[0]))

    # Nondimensionalize data with pin radius (0.002[m])
    x = x / pin_radius
    y = y / pin_radius

    return x,y

def plot_FFD_box(ax, x, y, col='black', mark='o', ls='-', lw=0.5, ms=10,):
    """
    Plot FFD box on axes object.

    input:
    ax: axes object
    x,y: x,y data of FFD box
    col: color to plot with
    mark: marker of the FFD box points
    -------
    return: nothing
    """
    ax.scatter(x, y, ms, color=col, marker=mark)
    segs1 = np.stack((x,y), axis=2)
    segs2 = segs1.transpose(1,0,2)
    ax.add_collection(LineCollection(segs1, color=col, linestyle=ls, linewidth=lw))
    ax.add_collection(LineCollection(segs2, color=col, linestyle=ls, linewidth=lw))

def add_init_FFD(ax, sym='', ls='--'):
    """
    Add initial FFD box to axes object.
    """
    folder = 'DSN_001'
    x,y = read_FFD_box(folder)
    plot_FFD_box(ax, x, y, 'tab:grey', mark=sym, ls=ls)

if __name__ == '__main__':

    fig = plt.figure()
    gs = fig.add_gridspec(2, 2, hspace=0, wspace=0 )
    #gs = fig.add_gridspec(2, 2)
    ((ax1, ax2), (ax3, ax4)) = gs.subplots(sharex='col', sharey='row')

    # ------------------------------------------------------------------------------------- #
    # Plot up-left side: original
    ax = ax1
    folder = 'DSN_001'

    shape = read_shape(folder)
    ax.plot(shape['x'], shape['y'],
            color='black',
            linestyle=':',
            label='Initial')

    add_init_FFD(ax,sym='o', ls='-')

    # ------------------------------------------------------------------------------------- #
    # Plot up-right side: cte-optimized
    ax = ax2
    folder = 'DSN_031'

    shape = read_shape(folder)
    ax.plot(shape['x'], shape['y'],
            color='black',
            linestyle='-',
            label='cte-Optimized')

    add_init_FFD(ax)
    x,y = read_FFD_box(folder)
    plot_FFD_box(ax, x, y, 'black')
    

    # ------------------------------------------------------------------------------------- #
    # Plot down-left side: avgT-optimized
    ax = ax3
    folder = '../9b__opt-CHT-mdot-avgT/DSN_024'

    shape = read_shape(folder)
    ax.plot(shape['x'], shape['y'],
            color='tab:red',
            linestyle='--',
            label='AvgT-Opt.')

    add_init_FFD(ax)
    x,y = read_FFD_box(folder)
    plot_FFD_box(ax, x, y, 'black')

    # ------------------------------------------------------------------------------------- #
    # Plot down-right side: dp optimized
    ax = ax4
    folder = '../9c__opt-CHT-mdot-dp/DSN_012'

    shape = read_shape(folder)
    ax.plot(shape['x'], shape['y'],
            color='tab:blue',
            linestyle='-.',
            label='Drag-Optimized')

    add_init_FFD(ax)
    x,y = read_FFD_box(folder)
    plot_FFD_box(ax, x, y, 'black')

    #x,y = read_FFD_box('DSN_001')
    #plot_FFD_box(ax2, x, y, 'black', mark='x', ls='--')

    # ------------------------------------------------------------------------------------- #
    ax1.set_ylabel('y/r [-]')
    ax3.set_ylabel('y/r [-]')
    ax3.set_xlabel('x/r [-]')
    ax4.set_xlabel('x/r [-]')
    ax1.set_xlim((-2.715,2.715))
    #ax1.set_ylim((-2.0,2.0))
    ax4.set_xlim((-2.715,2.715))
    #ax4.set_ylim((-2.0,2.0))
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_aspect('equal', adjustable='box')
        ax.label_outer()
        ax.legend(framealpha=0, frameon=False, loc='upper left', borderaxespad=0)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()