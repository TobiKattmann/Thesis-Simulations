#!/bin/bash
#
#SBATCH -J PinArray-BlockInlet-10 ### name of job
#SBATCH -N 1
#SBATCH --ntasks-per-node=10     ### optional: min cores(,max_cores)
#SBATCH -t 2:00:00             ### run time of job (hour:)minute
#SBATCH -e err.log           ### name of error file
#SBATCH -o out.log           ### name of output file
#SBATCH --partition=idle

ncores=10
cfg="configFluid.cfg"

mpirun -n $ncores SU2_CFD $cfg | tee CFD.log
