# ------------------------------------------------------------------------------------- #
# Tobias Kattmann, 09.03.2022
#
# Read data and plot comparisons between streamwise periodic flow and
# downstream repeated geometry
# ------------------------------------------------------------------------------------- #

import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------------- #

def plot_vel(sp_df, dupl_df, show=False):
    """
    Plot (x-)Velocity comparison
    
    input:
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%2==1)): continue
        plt.plot(line["Velocity:0"].values, line["Points:1"].values,
                 label="Segment "+str(i),
                 color=str(1 - i/len(dupl_df)))

    # Plot periodic line 
    plt.plot(sp_df["Velocity:0"].values, sp_df["Points:1"].values,
             label="Periodic",
             color='red',
             linewidth=1)
    
    plt.xlim((0,0.8))
    plt.ylim((0,0.0014))
    plt.xlabel('x-Velocity [m/s]')
    plt.ylabel('y-Coordinate [m]')
    plt.title("x-Velocity Comparison")
    plt.legend()
    plt.grid()
    plt.savefig('xVel.png', bbox_inches='tight')
    if(show): plt.show()
    plt.clf()

def plot_muT(sp_df, dupl_df, show=False):
    """
    Plot Eddy Viscosity comparison
    
    input:
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%2==1)): continue
        plt.plot(line["Eddy_Viscosity"].values, line["Points:1"].values,
                 label="Segment "+str(i),
                 color=str(1 - i/len(dupl_df)))

    # Plot periodic line 
    plt.plot(sp_df["Eddy_Viscosity"].values, sp_df["Points:1"].values,
             label="Periodic",
             color='red',
             linewidth=1)
    
    plt.xlim((0,0.008))
    plt.ylim((0,0.0014))
    plt.xlabel('Eddy Viscosity [Pa*s]')
    plt.ylabel('y-Coordinate [m]')
    plt.title("Eddy Viscosity Comparison")
    plt.legend()
    plt.grid()
    plt.savefig('muT.png', bbox_inches='tight')
    if(show): plt.show()
    plt.clf() # Reset figure, otherwise the previous plots will be drawn as well

def plot_pressure(sp_df, dupl_df, show=False):
    """
    Plot Pressure comparison. Beforehand the pressure values have to be postprocessed.
    In Inc. flow, the absolute value has no meaning anyway,
     we fix the pressure to zero at y=0, i.e. remove p(y=0) for all points
    
    input:
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%2==1)): continue
        plt.plot(line["Pressure"].values - line["Pressure"].values[0], line["Points:1"].values,
                 label="Segment "+str(i),
                 color=str(1 - i/len(dupl_df)))

    # Plot periodic line 
    plt.plot(sp_df["Recovered_Pressure"].values - sp_df["Recovered_Pressure"].values[0], sp_df["Points:1"].values,
             label="Periodic",
             color='red',
             linewidth=1)
    
    #plt.xlim((0,0.008))
    plt.ylim((0,0.0014))
    plt.xlabel('Pressure [Pa]')
    plt.ylabel('y-Coordinate [m]')
    plt.title("Pressure Comparison")
    plt.legend()
    plt.grid()
    plt.savefig('pressure.png', bbox_inches='tight')
    if(show): plt.show()
    plt.clf()

def plot_temperature(sp_df, dupl_df, Tperiodicity=True, show=False):
    """
    Plot Temperature comparison. Beforehand the temperature values have to be postprocessed.
    In Inc. flow, the absolute value has no meaning anyway,
     we fix the pressure to zero at y=0, i.e. remove p(y=0) for all points
    
    input:
    dp_df: dataframe containing sp values
    dupl_df: dataframe containing duplicated domains values
    Tperiodicity: Bool whether Temperature is true periodic or not
    """
    # Plot duplicates first, such that periodic draws over them
    for i,line in enumerate(dupl_df):
        # First one is block profile and would be all white anyway, last one is flawed by pressure outlet
        if((i==len(dupl_df)-1) or (i==0) or (i%2==1)): continue
        plt.plot(line["Temperature"].values - line["Temperature"].values[0], line["Points:1"].values,
                 label="Segment "+str(i),
                 color=str(1 - i/len(dupl_df)))

    # Plot periodic line
    Tperiodicity = False
    if (Tperiodicity):
      fieldName = "Recovered_Temperature"
    else:
      fieldName = "Temperature"
      
    plt.plot(sp_df[fieldName].values - sp_df[fieldName].values[0], sp_df["Points:1"].values,
             label="Periodic",
             color='red',
             linewidth=1)
    
    #plt.xlim((0,0.008))
    plt.ylim((0,0.0014))
    plt.xlabel('Temperature [K]')
    plt.ylabel('y-Coordinate [m]')
    plt.title("Temperature Comparison")
    plt.legend()
    plt.grid()
    plt.savefig('temperature.png', bbox_inches='tight')
    if(show): plt.show()
    plt.clf()


if __name__=='__main__':
    print('Start')
    # Read Streamwise Periodic line
    #sp_df = pd.read_csv("2__periodic_T-per/line_0.csv"); Tperiodicity = True
    sp_df = pd.read_csv("1__periodic/line_0.csv"); Tperiodicity = False

    # Read all the duplicate lines
    dupl_df = []
    for i in range(100): # large value to be safe
        try:
            #dupl_df.append(pd.read_csv("3__repeated-blockprofile_10-dupl/line_" + str(i) + ".csv"))
            #dupl_df.append(pd.read_csv("6__repeated-inletFile_10-dupl/line_" + str(i) + ".csv"))
            #dupl_df.append(pd.read_csv("4__repeated-blockprofile_14-dupl/line_" + str(i) + ".csv"))
            #dupl_df.append(pd.read_csv("5__repeated-blockprofile_18-dupl/line_" + str(i) + ".csv"))
            dupl_df.append(pd.read_csv("6__repeated-blockprofile_22-dupl/line_" + str(i) + ".csv"))
        except:
            break
    #end
    
    show=True
    plot_vel(sp_df, dupl_df, show)
    plot_muT(sp_df, dupl_df, show)
    plot_pressure(sp_df, dupl_df, show)
    plot_temperature(sp_df, dupl_df, Tperiodicity, show)
    print('End')
