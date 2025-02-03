#!/usr/bin/env python
#
# plot_forces.py calculates the total force, radius of gyration, and contraction rate of the network per time
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

#----------------------------------------------------------------------------------
def plot(xdata, ydata, **kwargs):
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

def calc_data(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)

    time_arr = []
    radg_arr = []
    crate_arr = []
    force_arr = []
    tension_arr = []
    for key, val in data.items():
        time_arr.append(float(key))

        mu = (1 / len(val))**2 * ( sum([float(i[0]) for i in val])**2 + sum([float(i[1]) for i in val])**2 )
        radg = (1 / len(val)) * sum([float(i[0])**2 + float(i[1])**2 for i in val])
        radg_arr.append( (radg - mu)**(1 / 2) )
         
        force = sum([(float(i[2])**2 + float(i[3])**2 )**(1 / 2) for i in val])
        force_arr.append(force)

        tension_arr.append(sum([float(i[4]) for i in val]))
    
    # use finite difference to approximate contraction rate
    for i in range(1, len(time_arr)):
        dR = radg_arr[i] - radg_arr[i-1]
        dt = time_arr[i] - time_arr[i-1]
        crate_arr.append(dR / dt)

    # create new directory and cd to it
    directory_name = '/' + os.path.splitext(os.path.basename(path))[0] + '_pics'
    og_directory = os.getcwd()
    if not os.path.exists(og_directory + directory_name): os.mkdir(og_directory + directory_name)
    os.chdir(og_directory + directory_name)

    # plot pictures
    plot(time_arr, radg_arr, pic_name='radg', xlabel='time (s)', ylabel='contraction rate (1/s)', title='System Radius per Time', dot_color='r', dot_style='-o')
    plot(time_arr, force_arr, pic_name='force', xlabel='time (s)', ylabel='total force (pN)', title='Force on Network per Time', dot_color='r', dot_style='-o')
    plot(time_arr, tension_arr, pic_name='tension', xlabel='time (s)', ylabel='tension (pN)', title='Tension on Network per Time', dot_color='r', dot_style='-o')
    plot(time_arr[1:], crate_arr, pic_name='crate', xlabel='time (s)', ylabel='contraction rate (um/s)', title='Contraction Rate per Time', dot_color='r', dot_style='-o')

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
        sys.stdout.write(f"grabbing data from {p}\n")
        calc_data(p)
    
    return 0

#------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])

