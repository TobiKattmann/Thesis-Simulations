#!/bin/bash
#
#SBATCH -J CHT-trans-gv ### name of job
#SBATCH -N 1
#SBATCH --ntasks-per-node=12     ### optional: min cores(,max_cores)
#SBATCH -t 96:00:00             ### run time of job (hour:)minute
#SBATCH -e err.log           ### name of error file
#SBATCH -o out.log           ### name of output file
ncores="                  12"

# set up the environment
module   load anaconda3/latest && export LD_LIBRARY_PATH=/software/gcc/11.2.0/lib:/software/gcc/11.2.0/lib64:$LD_LIBRARY_PATH

rm -r DOE/ DSN_*

# Run SU2 make
SU2_RUN="/home/kattmann/1__SU2/1__code/bin"
export PATH=$SU2_RUN:$PATH
echo $(which SU2_CFD)

python gradient_validation.py
python postprocess.py
