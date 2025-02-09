#!/usr/bin/env python
#
# param_map.py produces a parameter map of peak force, tension, radius, and contraction rate
# as one changes different parameters
#
# Copyright  K. Scarbro; 2025--

"""
    Reads stats.pkl file produced by read_force.py/plot_force.py  and config.cym files produced by preconfig to produce
    parameter maps on peak force, tension, radius of gyration, and contraction rate. Uses .pkl files 
    to read force, tension, etc. data and uses config.cym files produced by preconfig to read 
    the values of the parameters that are being changed (ex: filament and motor number)

Required Packages:
    matplotlib (install with pip via 'pip install matplotlib')

Note: 
    This script relies on the config.cym files output by preconfig to be structured in a specific way. 
    In config.cym.tpl file, the two parameters that are being varied should be listed with %[[param]].
    
    Example:
        [[motor = rand.int(10000)]]%[[motor]]
        [[filament = rand.int(5000)]]%[[filament]]

    There's some leeway with spacing, but keep the general structure like this to ensure preconfig prints the
    params at the right spot. In the config****.cym files printed by preconfig, the top few lines should read
        %####%#### or %####
                      %####

    If this isn't the case, adjustment may be needed.

    Also, the stats.pkl files should be a result of read_force.py and plot_force.py acting on the files
    output by report fiber:force

Syntax:
    param_map.py direc1 [direc2] [...] [name=file_name]
   
    - direc1: the name of the directories containing the config.cym and .pkl files
    - if name= is set, it changes the default file from force.pkl to whatever filename was given after name=

Output:
     param_pics directory containing parameter maps of the peak force, tension, radius, and contraction rate 

Examples:
    param_map.py direc_name1
    param_map.py direc_name1 direc_name2
    param_map.py direc****

K. Scarbro 01.2025
"""

try:
    import sys, os 
    import pickle
    import matplotlib.pylab as plt
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit(1)

#------------------------------------------------------------------------------------------
def plot(x, y, z, **kwargs):
    fig, ax = plt.subplots()

    pic_name = 'plot'
    clabel = None
    for key, val in kwargs.items():
        if key == 'xlabel': ax.set_xlabel(val)
        elif key == 'ylabel': ax.set_ylabel(val)
        elif key == 'title': ax.set_title(val)
        elif key == 'clabel': clabel = val
        elif key == 'pic_name': pic_name = val
        else: sys.stdout.write(f"{key} is an unknown parameter. Ignored.")


    pos = ax.scatter(x, y, c=z, cmap='viridis', s=1280)
    fig.colorbar(pos, ax=ax, label=clabel)

    plt.savefig(pic_name + '.png')

def read_pkl(path, name):
    """
    read pkl file to grab peak points of data
    """
    file_name = path + '/' + name
    if os.path.exists(file_name):
        with open(file_name, 'rb') as file:
            data = pickle.load(file)
    else:
        sys.stdout.write(f"Warning: could not find .pkl file in {path}\n")
        sys.exit() 
    
    peak_radg = min(data[1])
    peak_crate = min(data[2])
    peak_force = max(data[3])
    peak_tension = max(data[4])
    if len(data[0]) > 1:
        integral_tension = sum(data[4][:-1]) * (data[0][1] - data[0][0])

    return [peak_radg, peak_crate, peak_force, peak_tension, integral_tension]

def read_config(path):
    """
    read config file to grab data on how many motors and filaments
    """
    file_name = path + '/config.cym'
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            params = []
            lines = file.readlines()
            for line in lines:
                if len(params) == 2: 
                    break
                if line.startswith('%'):
                    params.extend(line[1:].strip().split('%'))
                else:
                    sys.stdout.write(f'the first lines of the config file in {path} does not start with parameter numbers\n')
                    sys.exit()
    else:
        sys.stdout.write(f"Warning: could not find config file in {path}\n")
        sys.exit(0)
    return params

def main(args):
    """
    read command line arguments and process commands
    """
    name = 'force.stats.pkl'
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            paths.append(os.path.abspath(arg))
        elif arg.startswith('name='):
            name = arg[5:]
        else:
            sys.stdout.write(f"Warning: unexpected argument {arg}\n")
            sys.exit()
    
    motor_arr = []
    fiber_arr = []
    peak_arr = []
    for p in paths:
        sys.stdout.write(f"reading data from {p}\n")
        motor, fiber = read_config(p)
        motor_arr.append(motor)
        fiber_arr.append(fiber)
        
        peak_arr.append(read_pkl(p, name))


    directory_name = '/' + 'param_pics'
    og_directory = os.getcwd()
    if not os.path.exists(og_directory + directory_name):
        os.mkdir(og_directory + directory_name)
    os.chdir(og_directory + directory_name)

    plot(motor_arr, fiber_arr, [peak[0] for peak in peak_arr], pic_name='peakradg', xlabel='motor number', ylabel='fiber number', clabel=r'$R$ ($\mu$m)', title='Peak Radius for Various Fiber and Motor Numbers')
    plot(motor_arr, fiber_arr, [peak[1] for peak in peak_arr], pic_name='peakcrate', xlabel='motor number', ylabel='fiber number', clabel=r'$\dot{R}$ ($\mu$m/s)', title='Peak Contraction Rate for Various Fiber and Motor Numbers')
    plot(motor_arr, fiber_arr, [peak[2] for peak in peak_arr], pic_name='peakforce', xlabel='motor number', ylabel='fiber number', clabel=r'F (pN)',  title='Peak Force for Various Fiber and Motor Numbers')
    plot(motor_arr, fiber_arr, [peak[3] for peak in peak_arr], pic_name='peaktension', xlabel='motor number', ylabel='fiber number', clabel=r'T (pN)',  title='Peak Tension for Various Fiber and Motor Numbers')
    plot(motor_arr, fiber_arr, [peak[4] for peak in peak_arr], pic_name = 'inttension', xlabel='motor number', ylabel='fiber number', clabel=r'$\delta$p (pNs)', title='Time Integral of Tension for Various Fiber & Motor #s')

#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])
