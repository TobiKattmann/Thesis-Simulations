# FADO script: Finite Differences of unsteady CHT and adjoint run

from FADO import *

# Design variables ----------------------------------------------------- #

nDV = 45
#printDocumentation(InputVariable)
# np.zeros = initial TK:: Why did pedro use ((nDV,)) in his example and not just (nDV)?
# ArrayLabelReplacer("__FFD_PTS__") = parser that specifies how var is written to file
# 0 = vector-size (zero means it is deduced from x0)
# np.ones = scale, optimizer scales x0/lb/ub with that quantitiy
# -0.3,0.3 = lower and upper bound for the DesignVar (Pin-diameter is 1m)
ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV)/0.0008, -0.0008,0.0008)
#ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV)/0.0004, -0.0004,0.0004)

# Parameters ----------------------------------------------------------- #

# The master config `configMaster.cfg` serves as an SU2 adjoint regression test.
# For a correct gradient validation we need to exchange some options

# switch from direct to adjoint mode and adapt settings.
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))
enable_def = Parameter([""], LabelReplacer("%__DEF__"))

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
deform.addParameter(enable_def)

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

# Surface AvgT OF
avgT = Function("avgT", "DIRECT/FADO_configMaster.csv",LabeledTableReader("\"AvgTemp[1]\""))
#avgT.addInputVariable(ffd,"AVGT_ADJ/of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
#avgT.addValueEvalStep(deform)
#avgT.addValueEvalStep(direct)
#avgT.addGradientEvalStep(avgT_adj)
avgT.setDefaultValue(1e4)

# Pressure Drop
dp = Function("dp", "DIRECT/FADO_configMaster.csv",LabeledTableReader("\"Pressure_Drop[0]\""))
dp.addInputVariable(ffd,"DP_ADJ/of_grad.csv",TableReader(None,0,(1,0)))
dp.addValueEvalStep(deform)
dp.addValueEvalStep(direct)
dp.addGradientEvalStep(dp_adj)
dp.setDefaultValue(1e4)

# Massflow
mdot = Function("mdot", "DIRECT/FADO_configMaster.csv",LabeledTableReader("\"Avg_Massflow[0](fluid_inlet)\""))
#mdot.addInputVariable(ffd,"MDOT_ADJ/of_grad.csv",TableReader(None,0,(1,0)))
#mdot.addValueEvalStep(deform)
#mdot.addValueEvalStep(direct)
#mdot.addGradientEvalStep(mdot_adj)
mdot.setDefaultValue(1e1)

# Drag
drag = Function("drag", "DIRECT/FADO_configMaster.csv",LabeledTableReader("\"CD[0]\""))
#drag.addInputVariable(ffd,"DRAG_ADJ/of_grad.csv",TableReader(None,0,(1,0))) 
#drag.addValueEvalStep(deform)
#drag.addValueEvalStep(direct)
#drag.addGradientEvalStep(drag_adj)
drag.setDefaultValue(1e1)

# Driver --------------------------------------------------------------- #

driver = ScipyDriver()
#printDocumentation(driver.addObjective)
# min = minimization of OF
# avgT = function to be optimized
# 1.0 = scale, optimizer will see funcVal*scale, Can be used to scale the gradient from of_grad
# 1e-7 because grad is 1e3 and a good incremental deformation would be 1e-5 -> scale with 1e-8
driver.addObjective("min", dp, 1/200)
driver.addObjective("min", avgT, 1e-100)
driver.addObjective("min", mdot, 1e-100)
driver.addObjective("min", drag, 1e-100)

driver.setWorkingDirectory("OPTIM")
#printDocumentation(driver.setEvaluationMode)
# True = parallel evaluation mode
# 2.0 = driver will check every 2sec whether it can start a new eval
driver.setEvaluationMode(False,2.0)
#printDocumentation(driver.setStorageMode)
# True = keep all designs
# DSN_ = folder prefix
driver.setStorageMode(True,"DSN_")
#printDocumentation(driver.setFailureMode)
# SOFT = if func eval fails, just the default val will be taken
driver.setFailureMode("SOFT")

his = open("optim.csv","w",1)
driver.setHistorian(his)

# Optimization, SciPy -------------------------------------------------- #

import scipy.optimize

driver.preprocess()
x = driver.getInitial()

options = {'disp': True, 'ftol': 1e-12, 'maxiter': 100}

optimum = scipy.optimize.minimize(driver.fun, x, method="SLSQP", jac=driver.grad,\
          constraints=driver.getConstraints(), bounds=driver.getBounds(), options=options)

his.close()

