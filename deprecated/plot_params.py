#!/usr/bin/env python
#
# param_map.py produces a parameter map of peak force, peak contraction rate, peak tension, peak radius, and the integral of the tension 
#
# Copyright  K. Scarbro; 2025--

"""
    Produces parameter map of peak force, peak contraction rate, peak tension, peak radius, and the integral of the tension over time.
    Takes as input directories containing sim data, and outputs five .png images for each of the parameter plots, stored in a param_plots
    directory. Each input directory needs to contain a config file with the parameter values listed at the top of the file and a stats.pkl
    file (as printed by "read_force.py -v").

Required Packages:
    matplotlib (install with pip via 'pip install matplotlib')

Note: 
    This script relies on the config.cym files output by preconfig to begin with the value of the parameters being changed. 
    In config.cym.tpl file, the two parameters that are being varied should be listed with %[[param]] at the beginning of the file.
    If interactive mode is set (with -i), then one needs to have installed IPython (do this via pip with "pip install ipython")

    Example:
        if you're varying the motor and fiber numbers, then the top line of config.cym.tpl should look like this
        [[motor = rand.int(10000)]]%[[motor]]
        [[filament = rand.int(5000)]]%[[filament]]

    There's some leeway with spacing, but keep the general structure like this to ensure preconfig prints the
    parameter values at the right spot. In the config****.cym files printed by preconfig, the top few lines should read
        %####%#### or %####
                      %####   (#### are the values of the parameters like [[motor]] nad [[filament]] in the above example)

    If this isn't the case, adjustment may be needed.

    Also, the stats.pkl files should be a result of read_force.py and plot_force.py acting on the files
    output by report fiber:force

Syntax:
    param_map.py direc [other directories] [name=?] [xname=?] [yname=?] [dotsize=?] [-i]
   
    - direc: the name of the directory containing the config.cym and stats.pkl files; more directories can (and should) be given
    - if name= is set, it changes the default file from force.stats.pkl to whatever filename was given after name=
    - xname and yname are the names of the parameters being altered (the default are motor and fiber number)
    - dotsize changes the size of the dots (1000 is the default value)
    - if -i is set, the program will launch an interactive plot that allows you to change the scale and what's being analyzed

Output:
     param_pics directory containing parameter maps of the peak force, tension, radius, and contraction rate 

Examples:
    param_map.py direc_name1
    param_map.py direc_name1 direc_name2 name=myforce.stats.pkl
    param_map.py direc**** xname='stall force' yname='unloaded speed'

K. Scarbro 01.2025
"""

try:
    import sys, os 
    import pickle
    import matplotlib.pyplot as plt
    import matplotlib.widgets
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit(1)

#------------------------------------------------------------------------------------------
class Data:
    plot_iteration = 0

    def __init__(self, x_data, y_data, z_data, xlabel, ylabel):
        self.x = x_data
        self.y = y_data
        self.z = z_data

        self.x_labels = [xlabel,] 

        # add an array so that new plots can be added later without having to alter the class
        self.data_list = []

    def plot(self):
       pass 

    def iterate(self, i):
        plot_iteration += 1

def run_interactive(x, y, peak_arr):
    fig, ax = plt.subplots()
    fig.subplots_adjust(left = 0.25, bottom=0.25)
    scatter = ax.scatter(x, y, c=peak_arr[1])
    fig.colorbar(scatter, ax=ax, label=r'$\dot{R}$ ($\mu$m/s)')

    button_ax = fig.add_axes([0.025, 0.5, 0.15, 0.05])
    button = matplotlib.widgets.Button(button_ax, 'Change')
    
    def change_plot(event):
        scatter.set_array(peak_arr[i])
        fig.canvas.draw_idle()

    button.on_clicked(change_plot)
    plt.show()

def plot(x, y, z, **kwargs):
    fig, ax = plt.subplots()

    pic_name = 'plot'
    clabel = None
    dot_size = 400
    add_line = False
    for key, val in kwargs.items():
        if key == 'xlabel': ax.set_xlabel(val)
        elif key == 'ylabel': ax.set_ylabel(val)
        elif key == 'title': ax.set_title(val)
        elif key == 'clabel': clabel = val
        elif key == 'pic_name': pic_name = val
        elif key == 'dotsize': dot_size = val
        elif key == 'add_line': add_line = val
        else: sys.stdout.write(f"{key} is an unknown parameter. Ignored.")

    pos = ax.scatter(x, y, c=z, cmap='viridis', s=dot_size)
    if add_line:
        xlims, ylims = ax.get_xlim(), ax.get_ylim()
        ax.plot([xlims[0], xlims[1]], [ylims[0], ylims[1]], color='red', linestyle='--')
    fig.colorbar(pos, ax=ax, label=clabel)

    plt.savefig(pic_name + '.png')
    plt.close()

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
    t_crate = data[2].index(peak_crate)
    peak_force = max(data[3]) if abs(max(data[4])) > abs(min(data[4])) else min(data[4])
    peak_tension = max(data[4]) if abs(max(data[4])) > abs(min(data[4])) else min(data[4])
    t_tension = data[4].index(peak_tension)
    if len(data[0]) > 1:
        integral_tension = sum(data[4][:-1]) * (data[0][1] - data[0][0])

    return [peak_radg, peak_crate, peak_force, peak_tension, integral_tension, t_crate, t_tension]

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
    x_name = 'Motor Number'
    y_name = 'Fiber Number'
    dot_size = 200
    interactive = False
    for arg in args:
        if os.path.isdir(arg):
            paths.append(os.path.abspath(arg))
        elif arg.startswith('name='):
            name = arg[5:]
        elif arg.startswith('xname='):
            x_name = arg[6:]
        elif arg.startswith('yname='):
            y_name = arg[6:]
        elif arg.startswith('dotsize='):
            dot_size = int(arg[8:])
        elif arg == "-i":
           interactive = True 
        else:
            sys.stdout.write(f"Warning: unexpected argument {arg}\n")
            sys.exit()

    if not paths:
        sys.stdout.write("No directories were given\n")
        sys.exit()

    x_arr  = []
    y_arr  = []
    peak_arr = []
    for p in paths:
        sys.stdout.write(f"reading data from {p}\n")
        x, y = read_config(p)
        x_arr.append(float(x))
        y_arr.append(float(y))
        
        peak_arr.append(read_pkl(p, name))


    directory_name = '/' + 'param_pics'
    og_directory = os.getcwd()
    if not os.path.exists(og_directory + directory_name):
        os.mkdir(og_directory + directory_name)
    os.chdir(og_directory + directory_name)

    # create tuple and dictionary for better readability (no functionality otherwise)
    data_tup = (x_arr, y_arr)
    label_dic = {'xlabel':x_name, 'ylabel':y_name, 'dotsize':dot_size}
    peak_arr = [list(row) for row in zip(*peak_arr)]

    plot(*data_tup, peak_arr[0], **label_dic, pic_name='peakradg', clabel=r'$R$ ($\mu$m)', title=f'Peak Radius')
    plot(*data_tup, peak_arr[1], **label_dic, pic_name='peakcrate', clabel=r'$\dot{R}$ ($\mu$m/s)', title=f'Peak Contraction Rate')
    plot(*data_tup, peak_arr[2], **label_dic, pic_name='peakforce', clabel=r'F (pN)',  title=f'Peak Force')
    plot(*data_tup, peak_arr[3], **label_dic, pic_name='peaktension', clabel=r'T (pN)',  title=f'Peak Tension')
    plot(*data_tup, peak_arr[4], **label_dic, pic_name = 'inttension', clabel=r'$\Delta$p (pNs)', title=f'Time Integral of Tension')
    plot(*data_tup, [peak / y for peak, y in zip(peak_arr[3], y_arr)], **label_dic, pic_name='normpeaktension', clabel=r'T (pN)',  title=f'Normed Peak Tension')
    plot(*data_tup, [peak / y for peak, y in zip(peak_arr[4], y_arr)], **label_dic, pic_name = 'norminttension', clabel=r'$\Delta$p (pNs)', title=f'Normed Integral of Tension')

    plot(peak_arr[5], peak_arr[6], x_arr, xlabel=r"Time at Contraction Rate Minimum ($\mu$m/s)", ylabel=r"Time at Tension Maximum ($\mu$m/s)", \
            title="Time vs Time", clabel=f"{x_name}", pic_name=f'timevtime_{"".join(x_name.split())}', dotsize=dot_size, add_line=True)
    plot(peak_arr[5], peak_arr[6], y_arr, xlabel=r"Time at Contraction Rate Minimum ($\mu$m/s)", ylabel=r"Time at Tension Maximum ($\mu$m/s)", \
            title="Time vs Time", clabel=f"{y_name}", pic_name=f'timevtime_{"".join(y_name.split())}', dotsize=dot_size, add_line=True)
    plot(peak_arr[5], peak_arr[6], peak_arr[1], xlabel=r"Time at Contraction Rate Minimum ($\mu$m/s)", ylabel=r"Time at Tension Maximum ($\mu$m/s)", \
            title="Time vs Time", clabel=r"$\dot{R}$ ($\mu$m/s)", pic_name='timevtime_crate', dotsize=dot_size, add_line=True)

    # if -i is set: pop up an interactive plot
    if interactive:
        run_interactive(*data_tup, peak_arr)

#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])
