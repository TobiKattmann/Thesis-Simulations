# T. Kattamnn 09.01.2022
#
# This script reads a tecplot surface ascii file and outputs a numpy array containing just
# the prescribed fields.
#
# The purpose is for periodic verification. Prescribing an inlet profile to a non-periodic
# simulation.

import numpy as np
import pandas as pd
import math

def parseFields(filename):
  '''
  filename : string containing the tecplot ascii filename
  ---
  return: list containing all field names as strings
  '''
  with open(filename, 'r') as f:
    for line in f:
      # detect line with starting string in it
      if 'VARIABLES' in line:                
        # Make a list of strings with fields from that line
        line = line.split('=')[1]
        line = line.split(',')
        # remove all blanks and "-chars from strings
        for i,word in enumerate(line): 
          line[i] = word.replace(' ', '')
          line[i] = word.replace('"', '')
        # for some stupid reason this has to be its own loop
        for i,word in enumerate(line):
          line[i] = word.lstrip()
          line[i] = word.rstrip('\n')
        print(line)
        return line

def parseNPoints(filename):
  '''
  filename : string containing the tecplot ascii filename
  ---
  return: number of points in the file
  '''
  with open(filename, 'r') as f:
    for line in f:
      # detect line with starting string in it
      if "ZONE NODES" in line:                
        # Make a list of strings with fields from that line
        line = line.split('=')[1]
        line = line.split(',')[0]
        npoints= int(line)
  
        print(npoints)
        return npoints

def tecplotASCII_2_df(filename, fields):
  '''
  filename : string containing the tecplot ascii filename
  fields   : list of strings containing the fields to be read
  ---
  return: numpy array containing only the specified fields
  '''
  # Parse field names from line that starts with the string 'VARIABLES ='
  available_fields= parseFields(filename)
  # Parse number of points from the number behind the string 'ZONE NODES=' in line 3
  npoints= parseNPoints(filename)
  data= pd.read_csv(filename, nrows=npoints, skiprows=3, sep='\t', header=None)
  data.columns = available_fields + ['']
  return data[fields]

if __name__=='__main__':
  print('Hallo')

  # inputs
  filename= "surface.dat"
  fields= [" x", "y", "Velocity_x", "Velocity_y", "Temperature", "Turb_Kin_Energy", "Omega"]
  output_fields= ["y", "Temperature", "VELOCITY", "NORMAL-X", "NORMAL-Y", "Turb_Kin_Energy", "Omega"]

  # Parse file
  data= tecplotASCII_2_df(filename, fields)

  # Now compute vel mag and introduce normalized direction vector
  # Introduce column with sqrt(vel-x^2 + vel-y^2)
  #data["VELOCITY"] = math.sqrt( data("Velocity_x")^2 + data("Velocity_y")^2)
  data["VELOCITY"] = ( data["Velocity_x"]**2 + data["Velocity_y"]**2 )**(1/2)
  data["NORMAL-X"] = data["Velocity_x"] / data["VELOCITY"]
  data["NORMAL-Y"] = data["Velocity_y"] / data["VELOCITY"]
  data["ThisShouldBeOne"] = ( data["NORMAL-X"]**2 + data["NORMAL-Y"]**2 )**(1/2)

  with pd.option_context('display.float_format', '{:0.12f}'.format):
    print(data[output_fields].to_string(index=False))
