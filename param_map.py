#!/usr/bin/env python
#
# param_map.py produces a parameter map 
#
# Copyright  K. Scarbro; 2025--

"""
    Reads .pkl files and saves plots of the radius of gyration, the rate of contraction, the forces on the
    fibers, and the tension on the fibers

Required Packages:
    matplotlib (install with pip via 'pip install matplotlib')

Syntax:
    plot_force.py file_name [file_name2] [...]
    
    - file_name1: the pickle file that the program needs to read
    - if other file_name are given, it will calculate the values using the data from these files as well

Output:
     file_name directory with plots of the radius of gyration, the contraction rate, the forces on the fibers, and 
     the tension on the fibers per time
     the number of directories formed  will equal the number of file_names entered 

Examples:
    plot_force.py file_name 
    plot_force.py file_name file_name2

K. Scarbro 01.2025
"""

try:
    import sys, os
    import pickle
    import matplotlib.pylab as plt
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit()

#------------------------------------------------------------------------------------------
def plot():
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 30, 40, 50]
    z = [.1, .2, .3, .4, .5]
    fig, ax = plt.subplots()
    pos = ax.scatter(x, y, c=z, cmap='viridis')
    fig.colorbar(pos, ax=ax)
    plt.show()

def read_config(path):
    """
    read config file to grab data on how many motors and filaments
    """
    file_name = path + '/config.cym'
    try: 
        with open(file_name, 'r') as file:
            line = file.readlines()[0]
            if line.startswith('%'):
                b = line[1:].strip().split('%')
            else:
                sys.stdout.write(f'the first line of the config file in {path} does not start with parameter numbers\n')
                sys.exit()
    except FileNotFoundError: 
        sys.stdout.write(f"Warning: could not find config file in {path}\n")
    print(b)

def main(args):
    """
    read command line arguments and process commands
    """
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            paths.append(os.path.abspath(arg))
        else:
            sys.stdout.write(f"Warning: unexpected argument {arg}\n")
            sys.exit()

    for p in paths:
        sys.stdout.write(f"reading data from {p}\n")
        read_config(p)

#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])
