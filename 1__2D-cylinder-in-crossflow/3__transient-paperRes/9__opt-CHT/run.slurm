#!/bin/bash
#
#SBATCH -J CHT-trans-gv ### name of job
#SBATCH -N 1
#SBATCH --ntasks-per-node=12     ### optional: min cores(,max_cores)
#SBATCH -t 336:00:00             ### run time of job (hour:)minute
#SBATCH -e err.log           ### name of error file
#SBATCH -o out.log           ### name of output file
ncores="                  12"

# set up the environment
module   load anaconda3/latest && export LD_LIBRARY_PATH=/software/gcc/11.2.0/lib:/software/gcc/11.2.0/lib64:$LD_LIBRARY_PATH

rm -r OPTIM/ DSN_*

# Run SU2 make
SU2_RUN="/home/kat7rng/1__SU2/1__code/bin"
export PATH=$SU2_RUN:$PATH
echo $(which SU2_CFD)

python optimization_avgT.py
python create_Visu_symlinks.py
python gradient_norm.py
