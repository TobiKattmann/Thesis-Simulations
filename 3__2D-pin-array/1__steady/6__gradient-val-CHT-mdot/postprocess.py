# Compute and print absolute difference between Discrete Adjoint
# and Finite Difference gradient. Prints also percentage difference.
#
# Run this script after `python gradient_validation.py` successfully finished

import numpy as np
import pandas as pd
import math

def loadData(DV, FDstep, DApath, DAstring, FDpath, FDstring):
  """
  Load DA-grad and primal values to compute FD-grad. Also compute abs/rel-diff.
  All data is put in a pandas dataframe in the following format.

  | #DV  | DA grad | FDgrad(FDstep[0]) | FDgrad(FDstep[1]) | ... | absDiff(FDstep[0]) | ... | relDiff(FDstep[0]) | ... |
  +------+---------+-------------------+-------------------+-----+--------------------+-----+--------------------+-----+
  |    0 | 0.65    | ...               | ...               | ... | ...                | ... | ...                | ... |
  |    1 | 1.5     | ...               | ...               | ... | ...                | ... | ...                | ... |
  |  ... | ...     | ...               | ...               | ... | ...                | ... | ...                | ... |

  Input:
  DV: list containing the DV numbers
  FDstep: list containing the FD steps
  DApath: relative file path to the DA-grad file
  DAstring: string under which the DA-grad is listed in the file
  FDpath: relative file path to the primal FD values
  FDstring: string under which the primal values for FD are listed in the file

  Return:
  Pandas data frame with data as stated above
  """
  # Check inputs
  # DV and FDstep have to be lists
  assert isinstance(DV, list)
  assert isinstance(FDstep, list)
  
  # *path and *string need to be strings
  assert isinstance(DApath, str)
  assert isinstance(DAstring, str)
  assert isinstance(FDpath, str)
  assert isinstance(FDstring, str)

  data = pd.DataFrame() # Create empty dataframe
  # Add DV numbers as first column of the dataframe
  data["DV"] = DV

  # Add DA-grad as second columns of the dataframe
  DAdata = pd.read_csv(DApath, usecols=[DAstring])
  data["DAgrad"] = DAdata.iloc[DV].values

  # Compute and add FD-grads to dataframe
  FDdata =  pd.read_csv(FDpath, usecols=[FDstring]) # load data
  FDbase_idx = 0 # Row-Index of the baseline value
  FDbase = FDdata.iloc[FDbase_idx].values # extract baseline (here at 0th row position) and ...
  FDdata.drop([FDbase_idx], inplace=True) # ... remove row from dataframe

  # create FDstep array, the primal data is the form (DV0/FD0, DV0/FD1, ... , DV1/FD0, ... ) so a FDstep array of the same size is created
  FDstep_array = []
  for i in range(len(DV)):
    for step in FDstep:
      FDstep_array.append(step)
  FDdata["FDstep"] = FDstep_array

  # compute FDgrad and write into data array
  FDgrad = (FDdata[FDstring]-FDbase).div(FDdata["FDstep"]).values
  FDgrad = FDgrad.reshape(len(DV),len(FDstep)).T
  for i,step in enumerate(FDstep):
    data["FDgrad_" + str(step)] = FDgrad[i] 

  # Compute and add absDiff to dataframe
  add_abs_diff = False
  if(add_abs_diff):
    for step in FDstep:
      data["absDiff_" + str(step)] = abs(data["DAgrad"] - data["FDgrad_" + str(step)])

  # Compute and add relDiff to dataframe
  for step in FDstep:
    data["relDiff_" + str(step)] = abs(data["DAgrad"] - data["FDgrad_" + str(step)]) / abs(data["DAgrad"])

  return data
#loadData

if __name__ == "__main__":

  # user input
  nDV=7
  chosenDV= list(range(0, nDV, 1))
  FDstep= [1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11, 1e-12, 1e-13]
  
  # Load data and compute FDgrad, abs/relDiff
  print("\nAVGT")
  data = loadData(chosenDV, FDstep, "DSN_001/AVGT_ADJ/of_grad.csv", "AVG_TEMPERATURE gradient ", "doe.csv", "  avgT")
  data.to_csv("gradient_data_avgt.csv", sep=',', index=False)
  print(data.to_string(index=False))

  print("\nDRAG")
  data = loadData(chosenDV, FDstep, "DSN_001/DRAG_ADJ/of_grad.csv", "DRAG gradient ", "doe.csv", "  drag")
  data.to_csv("gradient_data_drag.csv", sep=',', index=False)
  print(data.to_string(index=False))

  print("\nDP")
  data = loadData(chosenDV, FDstep, "DSN_001/DP_ADJ/of_grad.csv", "SURFACE_PRESSURE_DROP gradient ", "doe.csv", "  dp")
  data.to_csv("gradient_data_dp.csv", sep=',', index=False)
  print(data.to_string(index=False))

  print("\nMDOT")
  data = loadData(chosenDV, FDstep, "DSN_001/MDOT_ADJ/of_grad.csv", "SURFACE_MASSFLOW gradient ", "doe.csv", "  mdot")
  data.to_csv("gradient_data_mdot.csv", sep=',', index=False)
  print(data.to_string(index=False))
