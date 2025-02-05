#!/usr/bin/env python
#
# calculate_forces.py calculates the total force, radius of gyration, and contraction rate of the network per time
#
# Copyright  K. Scarbro; 2025--

"""
    Reads "report fiber:force" files and places time, force, and tension in a pickled data file

Syntax:
    read_force.py file_name1 [file_name2] [...]
    
    - file_name1: the file name that the program needs to search to find the data
    - if other file_name are given, it will calculate the values using the data from these files as well

Output:
     file_name1.pkl file. *.pkl files are pickled data streams. the pickled data is a dictionary.
     the keys are time slices, and the values are numpy arrays. the numpy arrays have columns of
     position x, position y, force x, force y, and tension, and the rows indicate the model point number 
     the number of .data files  output will equal the number of file_names entered 

Examples:
    read_force.py force.txt
    read_force.py myforce.txt myforcenum2.txt 

K. Scarbro 01.2025
"""


try:
    import sys, os
    import pickle
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit(1)

#----------------------------------------------------------------------------------
def read(path):
    """
    read positions, forces, and tensions from file
    """
    with open(path, 'r') as file:
        lines = file.readlines()

        data_dict = dict()
        for line in lines[1:]:
            if line.startswith('% time'):
                time = line[7:].strip()
                data_dict[time] = []
            elif not line.startswith('%') and not line.startswith('\n'):
                # inconsistent delimeter spacing, so split by delimeter ' ', and remove all '' elements:
                line_list = list(filter(lambda b: b, line.strip().split(' ')))[1:]
                data_dict[time].append([val for val in line_list])
    
    # write data to pkl file
    file_name = os.path.splitext(os.path.basename(path))[0] + '.pkl'
    with open(file_name, 'wb') as file:
        pickle.dump(data_dict, file)

def main(args):
    """
    read command line arguments and process commands
    """
    paths = []
    for arg in args:
        if os.path.isfile(arg):
            paths.append(os.path.abspath(arg))
        else:
            sys.stdout.write(f"{arg} isn't a filename\n")
            sys.exit()

    for p in paths:
        sys.stdout.write(f"reading data from {p}\n")
        data = read(p)

    return 0

#----------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])
