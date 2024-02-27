#!/bin/bash
## The first line has to say this, as a bash script

## Job Name
#SBATCH --job-name=test_python

## Partition and Allocation
#SBATCH -p stf
#SBATCH -A stf

## Resources
#SBATCH --nodes=1
#SBATCH --time=0:01:00
#SBATCH --ntasks=1
#SBATCH --mem=100G

## Specifiy the working directory for this job, keep '.' for current
#SBATCH --chdir=.

## Import modules if needed to run the job
module load contrib/anaconda/anaconda4.4.0

## Scripts to be executed here

## Clean up
exit 0