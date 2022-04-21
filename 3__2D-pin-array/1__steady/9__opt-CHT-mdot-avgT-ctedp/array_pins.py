# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 19.04.2022
#
# Plot shapes of the optimized geometry and the respective history.
# Additionally plot unconstrained optimas as well.
# ------------------------------------------------------------------------------------- #

from matplotlib import colors
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# ------------------------------------------------------------------------------------- #
# global variables
textwidth = 6.202
fig_width = textwidth # two images next to another
fig_height = textwidth / 2

# ------------------------------------------------------------------------------------- #

def read_shapes(folder):
    """Read and process (i.e. mirror) all available shapes

    input:
    folder: strings with folder where shape is located.
    -------
    return: list of dataframes, each containing shape of respective design."""

    try:
        shape = pd.read_csv(folder + '/DIRECT/shape0.csv')
        # Sort Dataframe according to x-value, necessary for nice plotting
        shape.sort_values("Points:0", inplace=True) # sort by specific column https://stackoverflow.com/questions/37787698/how-to-sort-pandas-dataframe-from-one-column
        # reverse a dataframe https://stackoverflow.com/questions/20444087/right-way-to-reverse-a-pandas-dataframe
        # deep copy a dataframe https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.copy.html
        mirror = shape.iloc[::-1].copy(deep=True)
        # mirror the y-axis coords
        mirror["Points:1"] = -1 * mirror["Points:1"]
        # Concatenate 2 Dataframes https://pandas.pydata.org/docs/reference/api/pandas.concat.html#pandas.concat
        shape = pd.concat([shape, mirror])
        # Adjust center of the x-axis to be in the pin-center (see dimensions.svg)
        shape["Points:0"] = shape["Points:0"] - 0.0055772
        print(folder + ' done')
    except:
        #shapes.append(shapes[-1])
        print(folder + ' no bueno')
        raise Exception('Unable to read shape.')

    return shape

def plot_periodic_domain(ax, shape):
    """Plot the outline of the periodic domain (unit cell)

    input:
    ax: axes object to plot on
    shape: dataframe with shape to plot
    -------
    return: na
    """
    paint = 'tab:red'
    lw = 0.9
    # plot bottom symmetry
    bs1, = ax.plot([0.0, x_dist/2-inner_pin_r],[0,0],color=paint)
    bs2, = ax.plot([x_dist/2+inner_pin_r, x_dist],[0,0],color=paint)
    # plot top symmetry
    ts, = ax.plot([0.0+inner_pin_r, x_dist-inner_pin_r],[y_dist/2,y_dist/2],color=paint)
    # inlet and outlet
    inl, = ax.plot([0.0, 0.0],[0.0, y_dist/2-inner_pin_r],color=paint)
    out, = ax.plot([x_dist, x_dist],[0.0, y_dist/2-inner_pin_r],color=paint)

    # create circle segments
    x,y = create_circle_segment()
    mrc, = ax.plot(x+x_dist/2, y, color=paint) # middle right
    mlc, = ax.plot(-x+x_dist/2, y, color=paint) # middle left
    tlc, = ax.plot(x, -y+y_dist/2, color=paint) # top left
    trc, = ax.plot(-x+x_dist, -y+y_dist/2, color=paint) # top right

    # plot shape parts
    # middle half pin
    mhp, = ax.plot(shape["Points:0"][:len(shape)//2] + 0*x_dist + x_dist/2,
            shape["Points:1"][:len(shape)//2] + 0*y_dist,
            color=paint)

    # upper right pin
    urp, = ax.plot(shape["Points:0"][:len(shape)//4] + 1*x_dist,
            -shape["Points:1"][:len(shape)//4] + 0*y_dist + y_dist/2,
            color=paint)

    # upper left pin
    ulp, = ax.plot(shape["Points:0"][len(shape)//4:len(shape)//2] + 0*x_dist,
            -shape["Points:1"][len(shape)//4:len(shape)//2] + 0*y_dist + y_dist/2,
            color=paint)

    for line in [bs1, bs2, ts, inl, out, mrc, mlc, tlc, trc, mhp, urp, ulp]:
        line.set_color(paint)
        line.set_linewidth(lw)


def create_circle_segment(radius=0.0006):
    """Create quarter circle segment with the circle midpoint being [0,0].
    All 4 orientations should be possible.

    input:
    radius: circle radius
    -------
    return: x,y coordinates
    """
    stepsize = radius/100
    x = np.arange(0, 0+radius+stepsize, stepsize)
    y = np.sqrt(radius**2 - x**2)
    return x, y

if __name__=='__main__':

    # Full pin copies along the axis in negative and positive direction.
    # Intermediate/Staggered pins will be filled up.
    x_copies = range(-2, 3)
    y_copies = range(-2, 3)

    x_dist = 0.0111544 # between two pins in exact downstream direction
    y_dist = 0.00644 # between two pins in exact crossstream direction
    inner_pin_r = 0.0006

    fig, ax = plt.subplots()
    # ax1.set_aspect('equal', adjustable='box')
    # ax2.set_aspect('equal', adjustable='box')
    #fig, (ax1, ax2) = plt.subplots(1,2)

    # ------------------------------------------------------------------------------------- #
    # Plot constrained shape with history
    shape = read_shapes('DSN_060')


    for xi in x_copies:
        for yi in y_copies:
            # copies in exact down-/crossstream direction
            ax.plot(shape["Points:0"] + xi*x_dist + x_dist/2,
                    shape["Points:1"] + yi*y_dist,
                    linewidth=0.75,
                    color = 'black')
            # intermediate pins
            ax.plot(shape["Points:0"] + xi*x_dist,
                    shape["Points:1"] + yi*y_dist + y_dist/2,
                    linewidth=0.75,
                    color = 'black')

    plot_periodic_domain(ax, shape)

    # ------------------------------------------------------------------------------------- #
    #ax.set_xlabel('x [m]')
    #ax.set_ylabel('y [m]')
    # ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    # ax1.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    # Remove ticks and ticklabels https://stackoverflow.com/questions/2176424/hiding-axis-text-in-matplotlib-plots
    ax.axes.get_xaxis().set_ticks([])
    ax.axes.get_yaxis().set_ticks([])
    # Remove figure frame
    ax.axis('off')

    ax.set_xlim((-1*0.0111544, 2*0.0111544))
    ax.set_ylim((-2*0.00322, 3*0.00322))
    ax.set_aspect('equal', adjustable='box')
    ax.label_outer()
    ax.legend(framealpha=1, frameon=False)

    # ------------------------------------------------------------------------------------- #
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #fig.set_size_inches(w=fig_width, h=fig_height)
    plt.savefig('shapes.png', bbox_inches='tight')#, dpi=100)
    plt.show()
    plt.cla()
    plt.close()
    print('End')