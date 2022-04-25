# FADO script: Finite Differences of unsteady CHT and adjoint run

from FADO import *

# Design variables ----------------------------------------------------- #

nDV = 7
ffd = InputVariable(0.0,PreStringHandler("DV_VALUE="),nDV)

# Parameters ----------------------------------------------------------- #

# The master config `configMaster.cfg` serves as an SU2 adjoint regression test.
# For a correct gradient validation we need to exchange some options

# switch from direct to adjoint mode and adapt settings.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))

avgT_OF = Parameter([""], LabelReplacer("%__OF_AVGT__"))
dp_OF = Parameter([""], LabelReplacer("%__OF_DP__"))
mdot_OF = Parameter([""], LabelReplacer("%__OF_MDOT__"))
drag_OF = Parameter([""], LabelReplacer("%__OF_DRAG__"))

# Evaluations ---------------------------------------------------------- #

# Define a few often used variables
ncores="14"
configMaster="FADO_configMaster.cfg"
configFluid="configFluid.cfg"
configSolid="configSolid.cfg"
meshName="2D-PinArray.su2"

# Note that correct SU2 version needs to be in PATH

def_command = "SU2_DEF " + configMaster
cfd_command = "mpirun -n " + ncores + " SU2_CFD " + configMaster

adj_command = "mpirun -n " + ncores + " SU2_CFD_AD " + configMaster + " && mpirun -n " + ncores + " SU2_DOT_AD " + configMaster

max_tries = 1

# mesh deformation
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addConfig(configFluid)
deform.addConfig(configSolid)
deform.addData(meshName)
deform.addExpected("mesh_out.su2")

# direct run
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configMaster)
direct.addConfig(configFluid)
direct.addConfig(configSolid)
direct.addData("DEFORM/mesh_out.su2",destination=meshName)
direct.addExpected("restart_0.dat")
direct.addExpected("restart_1.dat")
direct.addParameter(enable_direct)

def makeAdjRun(name, func=None) :
    adj = ExternalRun(name,adj_command,True)
    adj.setMaxTries(max_tries)
    adj.addConfig(configMaster)
    adj.addConfig(configFluid)
    adj.addConfig(configSolid)
    adj.addData("DEFORM/mesh_out.su2",destination=meshName)
    adj.addData("DIRECT/restart_0.dat")
    adj.addData("DIRECT/restart_1.dat")
    adj.addData("DIRECT/flow_0.meta")
    adj.addExpected("of_grad.csv")
    adj.addParameter(enable_adjoint)
    if (func is not None) : adj.addParameter(func)
    return adj
#end

avgT_adj = makeAdjRun("AVGT_ADJ", avgT_OF)
drag_adj = makeAdjRun("DRAG_ADJ", drag_OF)
dp_adj   = makeAdjRun("DP_ADJ",   dp_OF)
mdot_adj = makeAdjRun("MDOT_ADJ", mdot_OF)

# Functions ------------------------------------------------------------ #

hist=configMaster.split('.')[0] + ".csv"
# Surface AvgT OF
avgT = Function("avgT", "DIRECT/"+hist,LabeledTableReader("\"AvgTemp[1]\""))
avgT.addInputVariable(ffd,"AVGT_ADJ/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
avgT.addValueEvalStep(deform)
avgT.addValueEvalStep(direct)
avgT.addGradientEvalStep(avgT_adj)

# Pressure Drop
dp = Function("dp", "DIRECT/"+hist,LabeledTableReader("\"Pressure_Drop[0]\""))
dp.addInputVariable(ffd,"DP_ADJ/of_grad.csv",TableReader(None,0,(1,0)))
#dp.addValueEvalStep(deform)
#dp.addValueEvalStep(direct)
dp.addGradientEvalStep(dp_adj)

# Massflow
mdot = Function("mdot", "DIRECT/"+hist,LabeledTableReader("\"Avg_Massflow[0](fluid_inlet)\""))
mdot.addInputVariable(ffd,"MDOT_ADJ/of_grad.csv",TableReader(None,0,(1,0)))
#mdot.addValueEvalStep(deform)
#mdot.addValueEvalStep(direct)
mdot.addGradientEvalStep(mdot_adj)

# Drag
drag = Function("drag", "DIRECT/"+hist,LabeledTableReader("\"CD[0]\""))
drag.addInputVariable(ffd,"DRAG_ADJ/of_grad.csv",TableReader(None,0,(1,0))) 
#drag.addValueEvalStep(deform)
#drag.addValueEvalStep(direct)
drag.addGradientEvalStep(drag_adj)

# Driver --------------------------------------------------------------- #

# The input variable is the constraint tolerance which is not used for our purpose of finite differences
driver = ExteriorPenaltyDriver(0.005)
driver.addObjective("min", avgT)
driver.addObjective("min", dp)
driver.addObjective("min", mdot)
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
FDstep= [1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11, 1e-12, 1e-13, 1e-14]
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
