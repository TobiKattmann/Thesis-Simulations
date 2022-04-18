# 06.04.2022 T. Kattmann
#
# Average gradients of of_grad.csv in two sections.
# Note that the sign has to be switched between upper and lower half.

import numpy as np
import os
import pandas as pd

def averageGrad(df):
    """
    Average gradiens at half way mark. Considers sign change as well.

    df: pandas dataframe containing the original gradient
    -------
    return: pandas dataframe containing the altered, now averaged, data
    """
    # get string id of the first (and only) column
    string_id = list(df)[0]
    nDV = len(df[string_id])
    nDV_over_2 = int(nDV/2) # split the array in two halfs

    for i in range(nDV_over_2):
        # multiply lower part with -1 to account for upper/lower distinction
        df[string_id].iloc[i] = (df[string_id].iloc[i] + (-1)*df[string_id].iloc[i + nDV_over_2]) / 2
        df[string_id].iloc[i + nDV_over_2] = -df[string_id].iloc[i]
    #end

    return df
#end

if __name__ == '__main__':
  df = pd.read_csv("of_grad.csv")
  df = averageGrad(df)

  # Written of_grad must retain the same structure as the original one
  df.to_csv("avg_of_grad.csv", index=False, na_rep='NaN', sep=',')
  print(df.to_string(index=False))

