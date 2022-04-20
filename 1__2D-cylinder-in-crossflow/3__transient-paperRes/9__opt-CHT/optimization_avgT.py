# FADO script: Finite Differences of unsteady CHT and adjoint run

from FADO import *

# Design variables ----------------------------------------------------- #

nDV = 18
ffd = InputVariable(np.zeros((nDV,)),ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV)/0.3, -0.3,0.3) # 0.2 before

# Parameters ----------------------------------------------------------- #

# The master config `chtMaster.cfg` serves as an SU2 adjoint regression test.
# For a correct gradient validation we need to exchange some options

volume_output_def = Parameter(["OUTPUT_FILES= RESTART, PARAVIEW_MULTIBLOCK"],\
                 LabelReplacer("OUTPUT_FILES= RESTART"))
# 61*15 + 2 restart (primal), 61*5=305 (adjoint) = 10 periods washout 5 periods avg
time_iter_primal = Parameter(["TIME_ITER= 917"],\
                LabelReplacer("TIME_ITER= 305"))
# 200
outer_iter_primal = Parameter(["OUTER_ITER= 500"],\
                 LabelReplacer("OUTER_ITER= 100"))
restart_sol_primal = Parameter(["RESTART_SOL= YES"],\
                  LabelReplacer("RESTART_SOL= NO"))

# 500
outer_iter_adjoint = Parameter(["OUTER_ITER= 500"],\
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

adj_command = "mpirun -n " + ncores + " SU2_CFD_AD " + configMaster + " && " + " mpirun -n " + ncores + " SU2_DOT_AD " + configMaster + " && " + "python averageGrad.py"

max_tries = 1

# mesh deformation
deform = ExternalRun("DEFORM",def_command,True) # True means sym links are used for addData
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addData(configFluid) # zonal cfg's can be symlinked as they are unchanged
deform.addData(configSolid)
deform.addData(meshName)
deform.addParameter(volume_output_def)
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
    adj.addData("averageGrad.py")
    adj.setMaxTries(max_tries)
    adj.addConfig(configMaster)
    adj.addConfig(configFluid)
    adj.addConfig(configSolid)
    adj.addData("DEFORM/mesh_out.su2",destination=meshName)
    # add all primal solution files
    for timeIter in range(917): #
        if timeIter < 10:
            timeIter = "00" + str(timeIter)
        elif timeIter < 100:
            timeIter = "0" + str(timeIter)
        else:
            timeIter = timeIter
        adj.addData("DIRECT/solution_0_00" + str(timeIter) + ".dat")
        adj.addData("DIRECT/solution_1_00" + str(timeIter) + ".dat")
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
tavgT.addInputVariable(ffd,"AVGT_ADJ/avg_of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
tavgT.addValueEvalStep(deform)
tavgT.addValueEvalStep(direct)
tavgT.addGradientEvalStep(avgT_adj)
tavgT.setDefaultValue(1e3)

drag = Function("drag", "DIRECT/"+hist,LabeledTableReader("\"tavg[CD[0]]\""))
drag.addInputVariable(ffd,"DRAG_ADJ/avg_of_grad.csv",TableReader(None,0,(1,0))) # all rows, col 0, don't read the header
#drag.addValueEvalStep(deform)
#drag.addValueEvalStep(direct)
drag.addGradientEvalStep(drag_adj)
drag.setDefaultValue(1e3)

# Driver --------------------------------------------------------------- #

driver = ScipyDriver()
#printDocumentation(driver.addObjective)
# min = minimization of OF
# avgT = function to be optimized
# 1.0 = scale, optimizer will see funcVal*scale, Can be used to scale the gradient from of_grad
driver.addObjective("min", tavgT, 1/360)
driver.addUpperBound(drag, 1.332, 1/1.332)

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

options = {'disp': True, 'ftol': 1e-7, 'maxiter': 20}

optimum = scipy.optimize.minimize(driver.fun, x, method="SLSQP", jac=driver.grad,\
          constraints=driver.getConstraints(), bounds=driver.getBounds(), options=options)

his.close()

