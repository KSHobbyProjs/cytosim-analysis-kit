#!/usr/bin/env python
#
# plot_forces.py calculates the total force, total tension, radius of gyration, and contraction rate of the network per time
#
# Copyright  K. Scarbro; 2025--

"""
    Reads .pkl files output from read_force.py and saves plots of the radius of gyration, the rate of contraction,
    the forces on the fibers, and the tension on the fibers per time stored in a force_pics directory. If -v is set,
    it also outputs a stats.pkl file containing the data output in a binary format.

Required Packages:
    matplotlib (install with pip via 'pip install matplotlib')
 
Syntax:
    plot_force.py file_name [file_name2] [...] [-v]
    
    - file_name1: the pickle file that the program needs to read
    - if other file_name are given, it will calculate the values using the data from these files as well
    - if -v is put, another .pkl file, file_name.stats.pkl will be output that contains the 
      time, radius, contraction rate, force, and tension in an array format

Note:   
    This script assumes that the .pkl file was output by read_force.py and that the data read by read_force.py
    was the output of 'report fiber:force'

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
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit(1)

#-----------------------------------PLOTTING-----------------------------------------------
def plot(xdata, ydata, **kwargs):
    """
    produce plots of tension, crate, force, and radius in time
    """
    fig, ax = plt.subplots()

    pic_name = 'plot'
    dot_color = 'orange'
    dot_style = 'o'
    for key, val in kwargs.items():
        if key == 'xlabel': ax.set_xlabel(val)
        elif key == 'ylabel': ax.set_ylabel(val)
        elif key == 'title': ax.set_title(val)
        elif key == 'dot_color': dot_color = val
        elif key == 'dot_style': dot_style = val
        elif key ==  'pic_name': pic_name = val
        else: sys.stdout.write(f"{key} is an unknown parameter. Ignored")

    ax.plot(xdata, ydata, dot_style, color=dot_color)
    plt.savefig(pic_name + '.png')

#-------------------------DATA GRABBING-------------------------------------------------------------------------------------------------------------------------------------------------------------
def grab_ee(path):
    """
    computes the average effective length of the fibers in time from the pkl file output by read_force.py acting on 'report fiber'
    """

    with open(path, 'rb') as file:
        data = pickle.load(file)

    for key, val in data.items()
        if len(val[0]) != 10:
            sys.stdout.write(f"{path} file does not contain the correct amount of columns of data. does this pkl file come from read_force.py acting on a file printed from 'report fiber'?\n")
            sys.exit()

def calc_data(path):
    """
    computes radius, contraction rate, force, and tension in time from pkl file output by read_force.py acting on 'report fiber:force'
    """
    with open(path, 'rb') as file:
        data = pickle.load(file)

    time_arr = []
    radg_arr = []
    crate_arr = []
    force_arr = []
    tension_arr = []
    for key, val in data.items():
        if len(val[0]) != 5:
            sys.stdout.write(f"{path} file does not contain the correct amount of columns of data. does this .pkl file come from read_force.py acting on a file printed from 'report force:fiber'?\n")
            sys.exit()

        time_arr.append(key)

        mu = (1 / len(val))**2 * ( sum([i[0] for i in val])**2 + sum([i[1] for i in val])**2 )
        radg = (1 / len(val)) * sum([i[0]**2 + i[1]**2 for i in val])
        radg_arr.append( (radg - mu)**(1 / 2) )
         
        force = sum([(i[2]**2 + i[3]**2 )**(1 / 2) for i in val])
        force_arr.append(force)

        tension_arr.append(sum([i[4] for i in val]))
    
    # use finite difference to approximate contraction rate
    for i in range(1, len(time_arr)):
        dR = radg_arr[i] - radg_arr[i-1]
        dt = time_arr[i] - time_arr[i-1]
        crate_arr.append(dR / dt)

    return [time_arr, radg_arr, crate_arr, force_arr, tension_arr]

#----------------------------------------------------------------------------MAIN---------------------------------------------------------------------------------------------------------------
def main(args):
    """
    read command line arguments and process commands
    """
    paths = []
    v = False
    ee_files = None
    for arg in args:
        if os.path.isfile(arg):
            paths.append(os.path.abspath(arg))
        elif arg == '-v':
            v = True
        elif arg.startswith('-ee:'):
            ee_files = arg[9:]
        else:
            sys.stdout.write(f"{arg} isn't a filename\n")
            sys.exit()

    if not paths:
        sys.stdout.write("No directories were given \n")
        sys.exit()

    for p in paths:
        sys.stdout.write(f"grabbing data from {p}\n")
        time_arr, radg_arr, crate_arr, force_arr, tension_arr = calc_data(p)
     
        # if verbose, also output .pkl file including calculated stats
        if v:
            data = [time_arr, radg_arr, crate_arr, force_arr, tension_arr]
            file_name = os.path.splitext(os.path.basename(p))[0] + '.stats.pkl'
            with open(file_name, 'wb') as file:
                pickle.dump(data, file)

        # create new directory and cd to it
        directory_name = '/' + os.path.splitext(os.path.basename(p))[0] + '_pics'
        og_directory = os.getcwd()
        if not os.path.exists(og_directory + directory_name):
            os.mkdir(og_directory + directory_name)
        os.chdir(og_directory + directory_name)

        # plot pictures
        plot(time_arr, radg_arr, pic_name='radg', xlabel='time (s)', ylabel='contraction rate (1/s)', title='System Radius per Time', dot_color='r', dot_style='-o')
        plot(time_arr, force_arr, pic_name='force', xlabel='time (s)', ylabel='total force (pN)', title='Force on Network per Time', dot_color='r', dot_style='-o')
        plot(time_arr, tension_arr, pic_name='tension', xlabel='time (s)', ylabel='tension (pN)', title='Tension on Network per Time', dot_color='r', dot_style='-o')
        plot(time_arr[1:], crate_arr, pic_name='crate', xlabel='time (s)', ylabel='radius of gyration (um/s)', title='Contraction Rate per Time', dot_color='r', dot_style='-o')
        
    return 0

#-------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])

