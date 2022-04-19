# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 19.04.2022
#
# Plot shapes of the optimized geometry and the respective history.
# Additionally plot unconstrained optimas as well.
# ------------------------------------------------------------------------------------- #

import pandas as pd
import matplotlib.pyplot as plt
import os

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
        DSN_folders = ['DSN_001','DSN_010','DSN_019','DSN_030','DSN_060']
    elif(cte_impact):
        DSN_folders = ['DSN_001','DSN_060','../9b__opt-CHT-mdot-avgT', '../9c__opt-CHT-mdot-dp']
    else:
        raise Exception('Specify folders to be read.')

    return DSN_folders

def read_shapes():
    """Read and process (i.e. mirror) all available shapes

    input:
    -------
    return: list of dataframes, each containing shape of respective design."""
    shapes = []
    for i, folder in enumerate(create_folder_list()):
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
            shapes.append(shape)
            print(folder + ' done')
        except:
            #shapes.append(shapes[-1])
            print(folder + ' no bueno')

    return shapes


if __name__=='__main__':
    fig, (ax1, ax2) = plt.subplots(1,2)

    # ------------------------------------------------------------------------------------- #
    # Plot constrained shape with history
    shapes = read_shapes()
    for shape in shapes:
        ax1.plot(shape["Points:0"], shape["Points:1"],
                marker='')
    # Force a square plot https://www.delftstack.com/howto/matplotlib/how-to-make-a-square-plot-with-equal-axes-in-matplotlib/
    ax1.set_aspect('equal', adjustable='box')

    # ------------------------------------------------------------------------------------- #
    # Plot cte opt with uncte opt and initial geo.
    ax2.set_aspect('equal', adjustable='box')
    # ------------------------------------------------------------------------------------- #
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.set_size_inches(w=fig_width, h=fig_height)
    plt.savefig('shapes.png', bbox_inches='tight')#, dpi=100)
    plt.show()
    plt.cla()
    plt.close()
    print('End')