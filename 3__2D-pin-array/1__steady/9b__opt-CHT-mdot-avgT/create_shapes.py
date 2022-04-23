# ------------------------------------------------------------------------------------- #
# 19.04.2022 T. Kattmann
#
# Extract interface data for all Designs.
# Data of half pin is written to file and postprocesses in a separate step.
# ------------------------------------------------------------------------------------- #

#### import the simple module from the paraview
from paraview.simple import *
import os

# ------------------------------------------------------------------------------------- #

# create list with folder names
baseFolder = "./"
sub_folders = [name for name in os.listdir(baseFolder) if os.path.isdir(os.path.join(baseFolder, name))]
DSN_folders = [folder for folder in sub_folders if 'DSN' in folder]
# sort alphabetically as there were minor problems
DSN_folders = sorted(DSN_folders)
print(DSN_folders)

for i,folder in enumerate(DSN_folders):
    # create a new 'XML MultiBlock Data Reader'
    fADO_configMastervtm = XMLMultiBlockDataReader(FileName=['./' + folder + '/DIRECT/FADO_configMaster.vtm'])
    # create a new 'Extract Block'
    extractBlock1 = ExtractBlock(Input=fADO_configMastervtm)
    # Properties modified on extractBlock1
    extractBlock1.BlockIndices = [10]
    # save data
    SaveData('./' + folder + '/DIRECT/shape.csv', proxy=extractBlock1)
    print(folder + ' done')