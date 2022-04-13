# 02.02.2022 T. Kattmann
#
# Compute gradient norms for each design iteration and each gradient
# and save the gradient norm into a csv file.

import numpy as np
import os
import pandas as pd

def getGradientNorms(gradFolderNames, identifiers):
  """Read gradient data for one OF, return a dataframe and write to file

  gradientFolderNames: list of strings with the last folder name before the of_grad file
  identifier: list of strings for dataframe header
  --------------------
  return: Dataframe with the gradient data
  """
  # Check if gradFolderNames and identifiers have the same length
  if not (len(gradFolderNames) == len(identifiers)):
    raise AssertionError("List must have the same length!")

  # Create list with folder names
  baseFolder = "./"
  sub_folders = [name for name in os.listdir(baseFolder) if os.path.isdir(os.path.join(baseFolder, name))]
  DSN_folders = [folder for folder in sub_folders if 'DSN' in folder]

  # create dataframe with the ITER column, thus the correct column length
  df_gradNorm = pd.DataFrame({"ITER" : range(len(DSN_folders))})

  for gradFolderName,identifier in zip(gradFolderNames,identifiers):

    # Initialize array of gradient Norms
    gradientNormVector = np.zeros(len(DSN_folders))

    # loop through all Design folder
    for i,folder in enumerate(DSN_folders):
      # check if gradient file exists
      gradFilename = baseFolder + folder + "/" + gradFolderName + "/of_grad.csv"
      if os.path.exists(gradFilename):
        # Read the gradient file and store gradient norm
        df_grad = pd.read_csv(gradFilename)
        gradient = df_grad.values
        gradientNormVector[i] = np.linalg.norm(gradient)
      else:
        # Write a NaN as in Paraview these values are omitted
        gradientNormVector[i] = np.nan

    df_gradNorm[identifier + "-gradNorm"] = gradientNormVector
  #end

  return df_gradNorm

if __name__ == '__main__':
  df = getGradientNorms(["AVGT_ADJ","DP_ADJ"],["avgT","dp"])
  df.to_csv("gradient_norm.csv", index=False, na_rep='NaN', sep=',')
  print(df.to_string(index=False))
