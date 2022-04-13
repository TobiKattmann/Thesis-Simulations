# 06.04.2022 T. Kattmann
#
# Create an FFT of the unsteady quantities like avgT, CD, etc

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plotFFT(vals, ts, name, showPlot=True):
    """Compute and plot FFT of one scalar time-series

    vals: numpy.ndarray that contains the data
    ts: double timesteps-size [s], time-array goes from 0-iter*ts
    name: string with the fieldname
    showPlot: If False no plots are shown, only the dominant freq
    -------
    return: nothing
    """
    # First plot the original signal
    sr = len(vals)
    t = np.arange(0, sr*ts, ts)
    plt.plot(t, vals)
    plt.ylabel(name)
    plt.xlabel("Time [s]")
    if (showPlot): plt.show()

    # Following https://pythonnumericalmethods.berkeley.edu/notebooks/chapter24.04-FFT-in-Python.html
    # there are 54 ts in a period with dt=500s => T = 54*500 = 27000s => f = 1/T = 1/27000 = 0.00003704
    # Note that the above is true for the full shedding cycle, but Temperature and Drag exhibit double the frequency i.e. 7.407e-5 [Hz]
    # sampling rate
    from scipy.fftpack import fft, ifft

    X = fft(vals)
    N = len(X)
    n = np.arange(N)
    # get the sampling rate
    sr = 1 / (ts)
    T = N/sr
    freq = n/T

    # Get the one-sided specturm
    n_oneside = N//2
    # get the one side frequency
    f_oneside = freq[:n_oneside]

    # Why do I have to exclude the first entry (which would be the largest freq)?
    index_of_largest_freq= np.argmax(np.abs(X[:n_oneside])[1:])
    print(name, " Dominant Frequency: ", f_oneside[1:][index_of_largest_freq])

    plt.figure(figsize = (12, 6))
    plt.plot(f_oneside[1:], np.abs(X[:n_oneside])[1:], 'b')
    plt.xlabel('Freq (Hz)')
    plt.ylabel('FFT Amplitude |X(freq)|')
    plt.grid()
    if (showPlot): plt.show()
#end

if __name__ == '__main__':
    df = pd.read_csv("DSN_010/DIRECT/chtMaster.csv")
    # 1. Remove heading and trailing whitespaces 2. Remove first and last char because they are the "-char
    # https://stackoverflow.com/questions/36816810/cleaning-headers-in-imported-pandas-dataframe
    # https://reactgo.com/python-remove-first-last-character-string/
    df.columns = [c.strip()[1:-1] for c in df.columns.values.tolist()]

    timestep = 500
    showPlots = True
    num_splits = 2 # i.e. num_splits-1 gets the last split

    plotFFT(np.split(df["AvgTemp[1]"].values, num_splits)[num_splits-1], timestep, "AvgTemp[1]", showPlots)
    plotFFT(np.split(df["CD[0]"].values, num_splits)[num_splits-1], timestep, "CD[0]", showPlots)
    plotFFT(np.split(df["CL[0]"].values, num_splits)[num_splits-1], timestep, "CL[0]", showPlots)
