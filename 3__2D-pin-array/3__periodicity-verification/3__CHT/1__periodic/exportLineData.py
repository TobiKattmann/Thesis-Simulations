# T. Kattmann, 11.01.2022
#
# Script to extract line data and store in files
# Run with pvpython

#### import the simple module from the paraview
from paraview.simple import *

# create a new 'XML MultiBlock Data Reader'
configMastervtm = XMLMultiBlockDataReader(FileName=['FADO_configMaster.vtm'])

# create a new 'Pass Arrays'
passArrays1 = PassArrays(Input=configMastervtm)
passArrays1.PointDataArrays = ['Eddy_Viscosity', 'Pressure', 'Temperature', 'Velocity', 'Recovered_Pressure']

# create a new 'Plot Over Line'
plotOverLine1 = PlotOverLine(Input=passArrays1, Source='High Resolution Line Source')

# Properties modified on plotOverLine1
plotOverLine1.Tolerance = 2.22044604925031e-16

nDomains=1 # number of periodically repeated domains
perVec= [0.0111544, 0.0, 0.0] # vector between periodic interfaces
for i in range(nDomains+1):
  print(str(i) + "-th domain")
  print(0.0 + perVec[0]*i, 0.0     + perVec[1]*i, 0.0 + perVec[2]*i)
  print(0.0 + perVec[0]*i, 0.00122 + perVec[1]*i, 0.0 + perVec[2]*i)
  # Properties modified on plotOverLine1.Source
  plotOverLine1.Source.Point1 = [0.0 + perVec[0]*i, 0.0     + perVec[1]*i, 0.0 + perVec[2]*i]
  plotOverLine1.Source.Point2 = [0.0 + perVec[0]*i, 0.00122 + perVec[1]*i, 0.0 + perVec[2]*i]

  # save data
  SaveData('line_' + str(i) + '.csv', proxy=plotOverLine1, Precision=10)
