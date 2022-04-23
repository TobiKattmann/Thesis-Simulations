# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 09.03.2022
#
# Read data and plot comparisons between streamwise periodic flow and
# downstream repeated geometry
# ------------------------------------------------------------------------------------- #

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
fig_width = textwidth # two images next to another
#fig_height = textwidth / 2

# ------------------------------------------------------------------------------------- #

def plot_vel(ax, sp_df, dupl_df):
    """
    Plot (x-)Velocity comparison

    input:
    ax: axis object
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%stride!=0)): continue
        ax.plot(line["Velocity:0"].values, line["Points:1"].values*scale,
                 label="Slice "+str(i),
                 color=str(1 - i/len(dupl_df)),
                 linewidth=1,
                 linestyle='--')

    # Plot periodic line
    ax.plot(sp_df["Velocity:0"].values, sp_df["Points:1"].values*scale,
             label="Periodic",
             color='tab:red',
             linewidth=1,
             linestyle='-')

    ax.set_xlim((0,0.8))
    ax.set_ylim((0,1.23))
    ax.set_xlabel('x-Velocity [m/s]')
    ax.set_ylabel('y-Coordinate [mm]')
    #ax.set_title("x-Velocity Comparison")
    #ax.legend(framealpha=1, frameon=True)
    ax.grid()

def plot_pressure(ax, sp_df, dupl_df):
    """
    Plot Pressure comparison. Beforehand the pressure values have to be postprocessed.
    In Inc. flow, the absolute value has no meaning anyway,
     we fix the pressure to zero at y=0, i.e. remove p(y=0) for all points

    input:
    ax: axis object
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%stride!=0)): continue
        ax.plot(line["Pressure"].values - line["Pressure"].values[0], line["Points:1"].values*scale,
                 label="Slice "+str(i),
                 color=str(1 - i/len(dupl_df)),
                 linewidth=1,
                 linestyle='--')

    # Plot periodic line
    ax.plot(sp_df["Recovered_Pressure"].values - sp_df["Recovered_Pressure"].values[0], sp_df["Points:1"].values*scale,
             label="Periodic",
             color='tab:red',
             linewidth=1,
             linestyle='-')

    ax.set_xlim((-100,0.0))
    ax.set_ylim((0,1.23))
    ax.set_xlabel('Pressure [Pa]')
    #ax.set_ylabel('y-Coordinate [m]')
    #ax.set_title("Pressure Comparison")
    #ax.legend(framealpha=1, frameon=True)
    ax.grid()

def plot_temperature(ax, sp_df, dupl_df, Tperiodicity=True):
    """
    Plot Temperature comparison. Beforehand the temperature values have to be postprocessed.
    In Inc. flow, the absolute value has no meaning anyway,
     we fix the pressure to zero at y=0, i.e. remove p(y=0) for all points

    input:
    ax: axis object
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    Tperiodicity: Bool whether Temperature is true periodic or not
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%stride!=0)): continue
        ax.plot(line["Temperature"].values - line["Temperature"].values[0], line["Points:1"].values*scale,
                 label="Slice "+str(i),
                 color=str(1 - i/len(dupl_df)),
                 linewidth=1,
                 linestyle='--')

    # Plot periodic line
    Tperiodicity = False
    if (Tperiodicity):
      fieldName = "Recovered_Temperature"
    else:
      fieldName = "Temperature"

    ax.plot(sp_df[fieldName].values - sp_df[fieldName].values[0], sp_df["Points:1"].values*scale,
             label="Periodic",
             color='tab:red',
             linewidth=1,
             linestyle='-')

    ax.set_xlim((-10,70))
    ax.set_ylim((0,1.23))
    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel('y-Coordinate [mm]')
    #ax.set_title("Temperature Comparison")
    #ax.legend(framealpha=1, frameon=True)
    ax.grid()


def plot_muT(ax, sp_df, dupl_df):
    """
    Plot Eddy Viscosity comparison

    input:
    ax: axis object
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%stride!=0)): continue
        ax.plot(line["Eddy_Viscosity"].values, line["Points:1"].values*scale,
                 label="Slice "+str(i),
                 color=str(1 - i/len(dupl_df)),
                 linewidth=1,
                 linestyle='--')

    # Plot periodic line
    ax.plot(sp_df["Eddy_Viscosity"].values, sp_df["Points:1"].values*scale,
             label="Periodic",
             color='tab:red',
             linewidth=1,
             linestyle='-')

    ax.set_xlim((0,0.008))
    ax.set_ylim((0,1.23))
    ax.set_xlabel('Eddy Viscosity [Pa*s]')
    #ax.set_ylabel('y-Coordinate [m]')
    #ax.set_title("Eddy Viscosity Comparison")
    #ax.legend(framealpha=1, frameon=True)
    ax.grid()

if __name__=='__main__':
    print('Start')
    # Read Streamwise Periodic line
    sp_df = pd.read_csv("2__periodic_T-per/line_0.csv"); Tperiodicity = True
    #sp_df = pd.read_csv("1__periodic/line_0.csv"); Tperiodicity = False

    # Read all the duplicate lines
    dupl_df = []
    for i in range(100): # large value to be safe
        try:
            #dupl_df.append(pd.read_csv("3__repeated-blockprofile_10-dupl/line_" + str(i) + ".csv"))
            #dupl_df.append(pd.read_csv("6__repeated-inletFile_10-dupl/line_" + str(i) + ".csv"))
            #dupl_df.append(pd.read_csv("4__repeated-blockprofile_14-dupl/line_" + str(i) + ".csv"))
            dupl_df.append(pd.read_csv("5__repeated-blockprofile_18-dupl/line_" + str(i) + ".csv"))
            #dupl_df.append(pd.read_csv("6__repeated-blockprofile_22-dupl/line_" + str(i) + ".csv"))
        except:
            break
    #end
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharey=True)

    stride = 4
    scale = 1e3 # conversion to mm
    plot_vel(ax1, sp_df, dupl_df)
    plot_pressure(ax2, sp_df, dupl_df)
    plot_temperature(ax3, sp_df, dupl_df, Tperiodicity)
    plot_muT(ax4, sp_df, dupl_df)
    
    handles, labels = ax4.get_legend_handles_labels()
    lgd = fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5,-0.0), ncol=5, framealpha=1, frameon=True)

    # ------------------------------------------------------------------------------------- #
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    #fig.set_size_inches(w=fig_width, h=fig_height)
    fig.savefig('comp.pgf', bbox_extra_artists=(lgd,), bbox_inches='tight')#, dpi=100)
    #plt.show()
    plt.cla()
    plt.close()
    print('End')
