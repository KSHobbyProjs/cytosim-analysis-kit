#!/bin/env bash
#
# master.bash is a script designed to run read_force.py, plot_force.py, and param_map.py one after another
#
# Copyright K. Scarbro; 2025--

# 
# Takes as input a series of directories containing sim information. Outputs a force_pics directory in each input directory containing pictures
# of force, tension, contraction rate, radius of gyration per time. Also outputs a param_pics directory in the cwd that includes parameter maps
# of peak force, peak tension, peak contraction rate, peak radius, and integral of tension. Each input directory is assumed to have a force.txt file
# (as a result of "report fiber:force > force.txt")
#
# Note:
#   master.bash attempts to activate a python environment with matplotlib installed since plot_force.py requires the matplotlib package to run
#   it assumes that the environment is located at '~/Cytosim/.venv/'. Change this path to wherever your python environment is located
#
# Syntax:
#   master.bash directory [...]
#
#   - directory: the file name that the program needs to search to find the data
#   - if other directories are given, it will calculate the values using the data from these directories as well
#
# Output: 
#   - force_pics directory in each input directory containing pictures of force, tension, contraction rate, radius of gyration per time
#   - param_pics directory in the cwd that includes parameter maps of peak force, peak tension, peak contraction rate, peak radius, and integral of tension.
# 
# Examples: 
#   master.bash param0001
#   master.bash param****
#
# K. Scarbro 01.2025

# activate python environment 
source ~/Cytosim/.venv/bin/activate 

# check if at least one arguments is given
if [ $# -lt 1 ]; then
    echo "Usage: $0 <directory> <...>"
    exit 0
fi

~/Cytosim/scan/scan.py "~/Cytosim/python/read_force.py force.txt" ${@:1}

~/Cytosim/scan/scan.py "~/Cytosim/python/plot_force.py -v force.pkl" ${@:1}

~/Cytosim/python/param_map.py ${@:1} "dotsize=800" "xname=Motor #" "yname=Fiber #"

# deactivate python environment
deactivate
