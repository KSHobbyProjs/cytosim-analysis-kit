#!/usr/bin/env python
#
# extracts stats from a simulation and outputs a plot of those stats against time
#
# Copyright K. Scarbro; 2025--

"""
Extracts the radius, contraction rate, tension on the fibers, and force on the fibers for a simulation, and produces plots of these against time. 

Required Packages:
    matplotlib (install with pip via 'pip install matplotlib')

Syntax:
    plot_stats.py directory [...more directories...] [report='~/Cytosim/cytosim/bin/report']
    
    - directory: path to the directory where the simulation files are located
    - report: the path to the report binary. Default is '~/Cytosim/cytosim/bin/report'
    
Output: 
    An png of plots of the radius, contraction rate, tension, and force against time

K. Scarbro 2.26.2025
"""

import os, sys
import helpers.dataclass as dclass
import helpers.plotting as plotting
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit(1)

#--------------------------------------------------------------------------------------------
def main(args):
    # read directories from command line and plot data
    paths = []
    report = '~/Cytosim/cytosim/bin/report'
    for arg in args:
        if os.path.isdir(arg):
            paths.append(os.path.abspath(arg))
        elif arg.startswith('report='):
            report = arg[7:]
        else:
            sys.stdout.write(f"unknown input: {arg}\n")
            sys.exit()

    if not paths:
        sys.stdout.write("no directories were given \n")
        sys.exit()

    # for every path, extract the data and plot it
    for p in paths:
        sys.stdout.write(f"grabbing data from {p}\n")
        data = dclass.Data(report, p)
        data.extract_all()

        fig, ax = plt.subplots(3, 2, figsize=(15, 10))
        fig.delaxes(ax[2][1])

        plotting.plot(ax[0][0], data.times, data.radius, xlabel='Time(s)', ylabel=r'$R$ ($\mu$m)', title='Radius')
        plotting.plot(ax[0][1], data.times[:-1], data.contraction_rate, xlabel='Time(s)', ylabel=r'$\dot{R}$ ($\mu$m/s)', title='Contraction Rate')
        plotting.plot(ax[1][0], data.times, data.tension, xlabel='Time(s)', ylabel=r'$T$ (pN)', title='Tension')
        plotting.plot(ax[1][1], data.times, data.force, xlabel='Time(s)', ylabel=r'$F$ (pN)', title='Force')
        plotting.plot(ax[2][0], data.times, data.effective_length, xlabel='Time(s)', ylabel=r'$ee/l$', title='Effective Length')
        
        plt.tight_layout()
        # cd into directory, save picture, then cd back to cwd
        cwd = os.getcwd()
        os.chdir(p)
        plt.savefig('stats.png')
        os.chdir(cwd)

#---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])
