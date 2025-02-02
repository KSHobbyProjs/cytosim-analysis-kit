#!/bin/env bash
#
# master.bash is a script designed to run read_forces.py and plot_forces.py one after another
#
# Copyright K. Scarbro; 2025--

# 
# Takes in "report fiber:force" files and executes read_forces.py and plot_forces.py on these files
#
# Note:
#   master.bash attempts to activate a python environment with matplotlib installed since plot_force.py requires the matplotlib package to run
#   it assumes that the environment is located at '~/Cytosim/.venv/'. Change this path to wherever your python environment is located
#
# Syntax:
#   master.bash file_name1 [file_name2] [...]
#
#   - file_name1: the file name that the program needs to search to find the data
#   - if other file_name are given, it will calculate the values using the data from these files as well
#
# Output: 
#   directories of name file_name1_pics which include pngs of the radius of contraction (radg.png), forces on 
#   the network (force.png), and tension on the network (tension.png)
# 
# Examples: 
#   master.bash force.txt
#   master.bash force.txt force1.txt
#
# K. Scarbro 01.2025

# activate python environment 
source ~/Cytosim/.venv/bin/activate 

# check if at least one arguments is given
if [ $# -lt 1 ]; then
    echo "Usage: $0 <file_name1> <file_name2> <...>"
    exit 1
fi

file_name1="$1"
echo "reading $file_name1"

./read_force.py "$file_name1"

basename=$(basename "$file_name1")
basename=${basename%.*}
extension=".pkl"
basename="${basename}${extension}"

./plot_force.py "$basename"

# deactivate python environment
deactivate


