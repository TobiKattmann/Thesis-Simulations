# ------------------------------------------------------------------------------------------------ #
# T. Kattmann, 26.01.2022, restart_validation.py
#
# This script validates that the steady restarts work perfectly in SU2.
# For the primal-only restart and the primal restart for the adjoint.
# ------------------------------------------------------------------------------------------------ #

import os # for getenv
import glob # to read filename in current dir
import shutil # to delete complete folders
from subprocess import Popen # to call concurrent processes
import fileinput # for search and replace in-file

from sphinx import subprocess # to delete folders
import pandas as pd
import numpy as np

def createFolders(folder_list):
    """Remove old folders in case they exist and create fresh ones.

    ---------
    return: None
    """
    for folder in folder_list:
        if os.path.exists(folder) and os.path.isdir(folder):
            shutil.rmtree(folder)

    [os.mkdir(folder) for folder in folder_list]

def getListOfConfigs():
    """Get list of *cfg files in current dir.
    And put 'Master'-containing string upfront.

    ---------
    return: list of cfg strings with Master at front position."""
    configs=glob.glob('*.cfg')
    for i,cfg in enumerate(configs):
        if "Master" in cfg:
            configs.insert(0, configs.pop(i))
    return configs

def determineFiletype(config):
    """Check whether ascii or binary files are written.

    config: string with master cfg name
    ---------
    return: string with file ending
    """
    with open(config, 'r') as f:
        if "RESTART_ASCII" in f.read():
            return ".csv"
        else:
            return ".dat"

def getHistoryFilename(configs):
    """Return history filename based on single or multizone case.

    configs: list of str "configFluid.cfg", "configSolid.cfg"ings with cfg names
    ---------
    return: string of history filename
    """
    if (len(configs) == 1):
        return "history.csv"
    elif (len(configs) > 1):
        return configs[0].split('.')[0] + ".csv"

def getMeshFilename(config):
    """Extract mesh filename from cfg.

    config: cfg which contains mesh filename
    ---------
    return: string of mesh filename
    """
    with open(config, 'r') as f:
        for line in f:
            if "MESH_FILENAME" in line:
                return line.split('=')[1].split()[0]

def createLinkData(configs, folder_list, restart_type, mesh_filename):
    """Create list with data to be linked for each folder

    configs: list of strings with configs
    folder_list: list of strings with the folder names
    restart_type: string, ending of the restart files ".csv" or ".dat"
    mesh_filename: string of mesh filename
    ---------
    return: List of lists of tuples of (src, dst)
    """
    link_restart = []
    if (len(configs)==1):
        link_restart.append((folder_list[1] + "/restart" + restart_type, "solution" + restart_type))
    else:
        for i in range(len(configs)-1):
            link_restart.append((folder_list[1] + "/restart_" + str(i) + restart_type, "solution_" + str(i) + restart_type))

    link_data = []
    link_data.append([(mesh_filename, mesh_filename)])
    link_data.append([(mesh_filename, mesh_filename)])
    link_data.append([(mesh_filename, mesh_filename)] + link_restart)
    link_data.append([(mesh_filename, mesh_filename)] + link_restart)

    return link_data

def addDataToFolder(folder_name, configs, cfg_change, link_files):
    """Copy and adapt cfg's and symlink necessary files (mesh and restart). For 1 folder.

    folder_name: single string, target folder
    configs: list of strings with configs
    cfg_changes: tuple list containing (option_string, new_value)
    link_data: tuple list of (source, target)
    ---------
    return: None
    """
    # Copy configs
    [shutil.copy(config, folder_name) for config in configs]

    # Change configs in-place. Apply all changes to all cfgs in all folders
    # https://stackoverflow.com/questions/17140886/how-to-search-and-replace-text-in-a-file
    for config in configs:
       for change in cfg_change:
           with fileinput.FileInput(folder_name + '/' + config, inplace=True) as file:
               for line in file:
                    if line.startswith(change[0]):
                       print(change[0] + "= " + str(change[1]), end='\n')
                    else:
                        print(line, end='')

    # link data, src-data is from base folder, dst-folder has to be added
    for pair in link_files:
        os.symlink("../" + pair[0], folder_name + "/" + pair[1])

def runSimulations(num_cores, code_dir, config, folder_list):
    """Run all 4 simulations, 2 concurrently

    num_cores: number of cores to be used
    code_dir: path to the SU2 excecutable
    config: master config to be called
    folder_list: list of strings with the folder names
    ---------
    return: None
    """
    # Create run commands
    commands = []
    commands.append("mpirun -n " + str(num_cores) + ' ' + code_dir + "/SU2_CFD " + config + " > CFD.log")
    commands.append("mpirun -n " + str(num_cores) + ' ' + code_dir + "/SU2_CFD " + config + " > CFD.log")
    commands.append("mpirun -n " + str(num_cores) + ' ' + code_dir + "/SU2_CFD " + config + " > CFD.log")
    commands.append("mpirun -n " + str(num_cores) + ' ' + code_dir + "/SU2_CFD_AD " + config + " > CFD_AD.log")

    # Run Full Iter and Full Iter Minus One concurrently (https://stackoverflow.com/questions/30686295/how-do-i-run-multiple-subprocesses-in-parallel-and-wait-for-them-to-finish-in-py)
    procs = [Popen(command, shell=True, cwd=folder, stderr=subprocess.DEVNULL) for command, folder in zip(commands[:2],folder_list[:2])]
    for proc in procs:
        proc.wait()

    # additional link flow.meta if present
    flowmeta = "/flow.meta"
    if os.path.isfile(folder_list[1] + flowmeta):
        for folder in folder_list[2:]:
            os.symlink("../" + folder_list[1] + flowmeta, folder + flowmeta)

    # Run primal restarted for 1 Iteration and Run Adjoint concurrently
    procs = [Popen(command, shell=True, cwd=folder, stderr=subprocess.DEVNULL) for command, folder in zip(commands[2:],folder_list[2:])]
    for proc in procs:
        proc.wait()

def postprocess(folder_list, hist):
    """Extract Residuals from the history files, print to screen and to file.
    For the Adjoint extract from screen output.

    folder_list: list of strings with the folder names
    hist: string of the history filename
    ---------
    return: None
    """
    # Read baseline and restarted RMS-Residual
    df_baseline = pd.read_csv(folder_list[0] + '/' + hist)
    df_restarted = pd.read_csv(folder_list[2] + '/' + hist)
    rms_fields = [column for column in list(df_baseline) if "rms" in column]
    rms_baseline = df_baseline.tail(1)[rms_fields].values
    rms_restarted = df_restarted.tail(1)[rms_fields].values

    # Read adjoint restart from screen output
    with open(folder_list[3] + "/CFD_AD.log", 'r') as f:
        for line in f:
            if any(word in line for word in ["rms_Flow", "rms_Heat"]):
                next(f); line = next(f) # Skip two lines to get to the residuals
                rms_adjoint = [float(number) for number in line.split('|')[1:-1]]
                break

    # Create new dataframe to write all data into
    residuals = np.array([rms_baseline.flatten(), rms_restarted.flatten(), rms_adjoint])
    df_res = pd.DataFrame(data=residuals, index=["baseline","restarted","adjoint"], columns=rms_fields)
    df_res.to_csv("rms.csv", index=False)
    print(df_res.to_string(float_format="%.11f"))

if __name__=='__main__':
    num_cores=1
    compare_iter=100
    # 1st is the baseline, 2nd is one less and to be restarted from, 3rd is restarted primal and  4th is the adjoint.
    iter_list=[compare_iter+1, compare_iter, 1, 1]

    folder_list=["1__FullIter", "2__FullMinus1Iter", "3__PrimalRestart", "4__AdjointRestart"]
    createFolders(folder_list)
    # Define variables
    code_dir=os.getenv("SU2_RUN")
    # First in the list has to the one called with the executable
    configs=getListOfConfigs()
    restart_type=determineFiletype(configs[0]) # ".csv" or ".dat"
    # history file name depends on number of entries of configs.
    history_filename=getHistoryFilename(configs)
    mesh_filename=getMeshFilename(configs[0])
    iter_string= "ITER" if len(configs)==1 else "OUTER_ITER"

    cfg_changes = []
    cfg_changes.append([(iter_string, iter_list[0]), ("RESTART_SOL", "NO")])
    cfg_changes.append([(iter_string, iter_list[1]), ("RESTART_SOL", "NO")])
    cfg_changes.append([(iter_string, iter_list[2]), ("RESTART_SOL", "YES")])
    cfg_changes.append([(iter_string, iter_list[3]), ("RESTART_SOL", "NO")])

    # files to be symlinked, mesh will always be linked and restart files for the last two.
    link_data = createLinkData(configs, folder_list, restart_type, mesh_filename)

    for folder, cfg_change, link_files in zip(folder_list, cfg_changes, link_data):
        addDataToFolder(folder, configs, cfg_change, link_files)

    runSimulations(num_cores, code_dir, configs[0], folder_list)

    postprocess(folder_list, history_filename)
