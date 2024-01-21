#!/bin/bash

# Activate the Python environment
eval "$(conda shell.bash hook)"
conda activate analytics_env

# Run the command on each file in parallel
ls subset_*.sdf | parallel 'python refactor_Torsion_Strain.py -i {} -o {.}.csv'