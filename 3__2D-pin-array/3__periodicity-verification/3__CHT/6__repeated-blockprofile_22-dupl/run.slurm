#! /bin/bash
#
#SBATCH -J PinArray-BlockInlet ### name of job
#SBATCH -N 1
#SBATCH --ntasks-per-node=14     ### optional: min cores(,max_cores)
#SBATCH -t 1:00:00             ### run time of job (hour:)minute
#SBATCH -e err.log           ### name of error file
#SBATCH -o out.log           ### name of output file
##SBATCH --partition=idle

ncores=14
cfg="FADO_configMaster.cfg"

mpirun -n $ncores SU2_CFD $cfg | tee CFD.log
