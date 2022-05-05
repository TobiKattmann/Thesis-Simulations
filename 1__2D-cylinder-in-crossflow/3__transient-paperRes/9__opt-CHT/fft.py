# ------------------------------------------------------------------------------------- #

# 06.04.2022 T. Kattmann
#
# Create an FFT of the unsteady quantities like avgT, CD, etc
# ------------------------------------------------------------------------------------- #

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------------- #
# Global vars
timestep = 500

# ------------------------------------------------------------------------------------- #

def plotValue(ax, vals, name):
    """Plot function value on axes object"""
    sr = len(vals)
    t = np.arange(0, sr*timestep, timestep)
    ax.plot(t, vals)
    ax.set_ylabel(name)
    ax.set_xlabel("Time [s]")

def plotFFT(ax, vals, name, ls='-', col='b'):
    """Compute and plot FFT of one scalar time-series

    vals: numpy.ndarray that contains the data
    name: string with the fieldname
    -------
    return: nothing
    """
    sr = len(vals)

    # Following https://pythonnumericalmethods.berkeley.edu/notebooks/chapter24.04-FFT-in-Python.html
    # there are 54 ts in a period with dt=500s => T = 54*500 = 27000s => f = 1/T = 1/27000 = 0.00003704
    # Note that the above is true for the full shedding cycle, but Temperature and Drag exhibit double the frequency i.e. 7.407e-5 [Hz]
    # sampling rate
    from scipy.fftpack import fft, ifft

    X = fft(vals)
    N = len(X)
    n = np.arange(N)
    # get the sampling rate
    sr = 1 / (timestep)
    T = N/sr
    freq = n/T

    # Get the one-sided specturm
    n_oneside = N//2
    # get the one side frequency
    f_oneside = freq[:n_oneside]

    # Why do I have to exclude the first entry (which would be the largest freq)?
    index_of_largest_freq= np.argmax(np.abs(X[:n_oneside])[1:])
    print(name, " Dominant Frequency: ", f_oneside[1:][index_of_largest_freq])

    ax.plot(f_oneside[1:], np.abs(X[:n_oneside])[1:] / max(np.abs(X[:n_oneside])[1:]),
            color=col,
            linestyle=ls)
    ax.set_xlabel('Freq (Hz)')
    #ax.set_ylabel('FFT Amplitude |X(freq)|')
    ax.set_ylabel('normalized Magnitude')
    ax.grid()
#end

# ------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    df = pd.read_csv("DSN_040/DIRECT/chtMaster.csv")
    # 1. Remove heading and trailing whitespaces 2. Remove first and last char because they are the "-char
    # https://stackoverflow.com/questions/36816810/cleaning-headers-in-imported-pandas-dataframe
    # https://reactgo.com/python-remove-first-last-character-string/
    df.columns = [c.strip()[1:-1] for c in df.columns.values.tolist()]
    
    num_splits = 3 # i.e. num_splits-1 gets the last split. For 2: Add [0:-1] behind "values"
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3,2)

    plotValue(ax1, np.split(df["AvgTemp[1]"].values, num_splits)[num_splits-1], "AvgTemp[1]")
    plotValue(ax3, np.split(df["CD[0]"].values, num_splits)[num_splits-1], "CD[0]")
    plotValue(ax5, np.split(df["CL[0]"].values, num_splits)[num_splits-1], "CL[0]")

    plotFFT(ax2, np.split(df["AvgTemp[1]"].values, num_splits)[num_splits-1],  "AvgTemp[1]")
    plotFFT(ax4, np.split(df["CD[0]"].values, num_splits)[num_splits-1], "CD[0]")
    plotFFT(ax6, np.split(df["CL[0]"].values, num_splits)[num_splits-1], "CL[0]")

    plt.show()