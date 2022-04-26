# FADO script: Finite Differences of unsteady CHT and adjoint run

from FADO import *

# Design variables ----------------------------------------------------- #

nDV = 18
ffd = InputVariable(0.0,PreStringHandler("DV_VALUE="),nDV)

# Parameters ----------------------------------------------------------- #

# The master config `chtMaster.cfg` serves as an SU2 adjoint regression test.
# For a correct gradient validation we need to exchange some options

time_iter_primal = Parameter(["TIME_ITER= 63"],\
                LabelReplacer("TIME_ITER= 61"))
outer_iter_primal = Parameter(["OUTER_ITER= 500"],\
                 LabelReplacer("OUTER_ITER= 100"))
restart_sol_primal = Parameter(["RESTART_SOL= YES"],\
                  LabelReplacer("RESTART_SOL= NO"))

outer_iter_adjoint = Parameter(["OUTER_ITER= 2500"],\
                  LabelReplacer("OUTER_ITER= 100"))

# Switch from direct to adjoint mode.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))

avgT_OF = Parameter([""], LabelReplacer("%__OF_AVGT__"))
drag_OF = Parameter([""], LabelReplacer("%__OF_DRAG__"))

# Evaluations ---------------------------------------------------------- #

# Define a few often used variables
ncores="12"
configMaster="chtMaster.cfg"
configFluid="fluid.cfg"
configSolid="solid.cfg"
meshName="MeshCHT.su2"

# Note that correct SU2 version needs to be in PATH

def_command = "SU2_DEF " + configMaster
cfd_command = "mpirun -n " + ncores + " SU2_CFD " + configMaster

adj_command = "mpirun -n " + ncores + " SU2_CFD_AD " + configMaster + " && " + " mpirun -n " + ncores + " SU2_DOT_AD " + configMaster

max_tries = 1

# mesh deformation
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addData(configFluid) # zonal cfg's can be symlinked as they are unchanged
deform.addData(configSolid)
deform.addData(meshName)
deform.addExpected("mesh_out.su2")

# direct run
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configMaster)
direct.addConfig(configFluid)
direct.addData(configSolid)
direct.addData("DEFORM/mesh_out.su2",destination=meshName)
direct.addData("solution_0_00000.dat")
direct.addData("solution_0_00001.dat")
direct.addData("solution_1_00000.dat")
direct.addData("solution_1_00001.dat")
direct.addExpected("solution_0_00062.dat")
direct.addExpected("solution_1_00062.dat")
direct.addParameter(enable_direct)
direct.addParameter(time_iter_primal)
direct.addParameter(outer_iter_primal)
direct.addParameter(restart_sol_primal)

def makeAdjRun(name, func=None):
    adj = ExternalRun(name,adj_command,True)
    adj.setMaxTries(max_tries)
    adj.addConfig(configMaster)
    adj.addConfig(configFluid)
    adj.addConfig(configSolid)
    adj.addData("DEFORM/mesh_out.su2",destination=meshName)
    # add all primal solution files
    for timeIter in range(63): #
        if timeIter < 10:
            timeIter = "0" + str(timeIter)
        adj.addData("DIRECT/solution_0_000" + str(timeIter) + ".dat")
        adj.addData("DIRECT/solution_1_000" + str(timeIter) + ".dat")
    #end
    adj.addExpected("of_grad.csv")
    adj.addParameter(enable_adjoint)
    adj.addParameter(outer_iter_adjoint)
    if (func is not None) : adj.addParameter(func)
    return adj
#end

avgT_adj = makeAdjRun("AVGT_ADJ", avgT_OF)
drag_adj = makeAdjRun("DRAG_ADJ", drag_OF)

# Functions ------------------------------------------------------------ #

hist=configMaster.split('.')[0] + ".csv"

tavgT = Function("tavgT", "DIRECT/"+hist,LabeledTableReader("\"tavg[AvgTemp[1]]\""))
tavgT.addInputVariable(ffd,"AVGT_ADJ/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
tavgT.addValueEvalStep(deform)
tavgT.addValueEvalStep(direct)
tavgT.addGradientEvalStep(avgT_adj)

drag = Function("drag", "DIRECT/"+hist,LabeledTableReader("\"tavg[CD[0]]\""))
drag.addInputVariable(ffd,"DRAG_ADJ/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
#drag.addValueEvalStep(deform)
#drag.addValueEvalStep(direct)
drag.addGradientEvalStep(drag_adj)

# Driver --------------------------------------------------------------- #

# The input variable is the constraint tolerance which is not used for our purpose of finite differences
driver = ExteriorPenaltyDriver(0.005)
driver.addObjective("min", tavgT)
driver.addObjective("min", drag)

driver.setWorkingDirectory("DOE")
driver.preprocessVariables()
driver.setStorageMode(True,"DSN_")

his = open("doe.csv","w",1)
driver.setHistorian(his)

# Simulation Runs ------------------------------------------------------ #

# Undeformed/initial primal first in order to have the correct solution in
# the WorkindDirectory for the following adjoint
print("Computing baseline primal")
x = driver.getInitial()
driver.fun(x) # baseline evaluation

# Compute discrete adjoint gradient
print("Computing discrete adjoint gradient")
driver.grad(x)

# Primal simulation for each FD step-size and each DV
chosenDV= range(0, nDV, 1)
chosenDV= [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
FDstep= [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10]
for iDV in chosenDV:
  for stepsize in FDstep:
    print("Computing primal of DV ", iDV, "/", nDV-1, " with stepsize ", stepsize)
    x = driver.getInitial()
    x[iDV] = stepsize # DV_VALUE, FD-step
    driver.fun(x)
  #end
#end

his.close()

# For results run `python postprocess.py` to get screen output
# of the differences between primal and adjoint simulation.
