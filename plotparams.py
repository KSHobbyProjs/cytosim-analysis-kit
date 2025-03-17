#!/usr/bin/env python
#
# produces parameter plots of stats given a list of directories
#
# Copyright K. Scarbro; 2025--

"""
A module to handle plotting of parameter maps. Currently outputs a png of the peak radius, peak force, 
peak tension, peak effective length, peak contraction rate, the integral of tension, and time at peak
contraction rate vs time at peak tension plots given a list of directories where sims are located

Required Packages:
    matplotlib (install with 'pip install matplotlib')

Syntax:
    plotparams.py directory [...more directories...] [report='~/Cytosim/cytosim/bin/report'] [useold=None] [nproc=1] [name=None] [dotsize=200] [-i] [-v]
    - directory: the paths to the directories containing simulation information
    - name: the name of the parameters given separated by a comma (example: name=motors,fibers)
    - dotsize: the size of the parameter dots (default is 200)
    - -i: this sets the plotting environment into interactive mode, allowing for plot adjustments in real time
    - -v: output the pickle file of the param class so you won't have to calculate the peaks again
    - useold: use an old pickle file rather than computing the peaks again. useold=None of useold=[path to pickle file]
    - report: the path to the report binary. default is '~/Cytosim/cytosim/bin/report'
    - nproc: the number of processors. nproc=1 (serial) is the default
Output:
    - Outputs a png image of all parameter plots in the directory where the module was called
    - if -i is set, an interactive plotting window is opened that allows you to alter plots in real time 

Note:
    This module assumes that you've configured the config files so that the system parameters that are
    being varied are listed at the top of the config.cym page. See utils.extracttools.readconfig() for more information

K. Scarbro 3.1.2025
"""

import sys, os
import pickle
import helpers.paramclass as pclass
import helpers.plotclass as plot
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit(1)

#----------------------------------------------------------------------------------------------------
def main(args):
    """
    read directories of simulations and run plotting environment
    """
    paths = []
    report = '~/Cytosim/cytosim/bin/report'
    xname, yname = None, None
    dotsize = 200
    interactive = False
    verbose = False
    useold = None
    nproc = 1
    for arg in args:
        if os.path.isdir(arg):
            paths.append(os.path.abspath(arg))
        elif arg.startswith('report='):
            report = arg[7:] 
        elif arg.startswith('name='):
            xname, yname = arg[5:].split(',')
        elif arg.startswith('dotsize='):
            dotsize = int(arg[8:])
        elif arg == "-i":
            interactive = True
        elif arg == "-v":
            verbose = True
        elif arg.startswith("useold="):
            useold = arg[7:]
        elif arg.startswith("nproc="):
            nproc = int(arg[6:])
        else:
            sys.stdout.write(f"unknown input: {arg}\n")
            sys.exit()

    if not paths and useold is None:
        sys.stdout.write("no directories were given\n")
        sys.exit()

    # extract parameter information, and populate Param class with parameter information
    if useold is not None:
        with open(useold, 'rb') as f:
            params = pickle.load(f)
    else:
        params = pclass.Param(report, paths)
        params.extract_paramvals()
        params.extract_peaks('all', nproc=nproc)
    if verbose:
        with open('params.pkl', 'wb') as f:
            pickle.dump(params, f)

    # plot the scatter plots of the peak data. it's possible to generalize this to make it shorter, but it's not very readable
    fig, ax = plt.subplots(3, 3, figsize=(15, 15))
    axs = [axij for axi in ax for axij in axi]
    # put the parameter data and label data in a tuple and dictionary just for readability
    paramtuple = (params.params[0], params.params[1])
    xdata = [params.params[0] for _ in range(6)] + [params.peaks['tension'][0] for _ in range(2)] + [params.peaks['tension'][1]]
    ydata = [params.params[1] for _ in range(6)] + [params.peaks['contractionrate'][0], params.peaks['effectivelength'][0], params.peaks['contractionrate'][1]]
    cdata = [params.peaks['radius'][1], params.peaks['tension'][1], params.peaks['force'][1], params.peaks['contractionrate'][1], params.peaks['effectivelength'][1], params.peaks['tensionintegral']] + [params.peaks['contractionrate'][1] for _ in range(2)] + [params.peaks['effectivelength'][1]]
    xlabels = [xname for _ in range(6)] + [r'$t_{tension}$ (s)' for _ in range(2)] + ['tension (pN)']
    ylabels = [yname for _ in range(6)] + [r'$t_{\dot{R}}$ (s)', r'$t_{ee/l}$ (s)', r'$\dot{R}$']
    clabels = [r'Radius ($\mu$m)', 'Tension (pN)', 'Force (pN)', r'$\dot{R}$ ($\mu$m/s)', r'$ee/l$', r'$\Delta p$ (pN$\cdot$s)', r'$\dot{R}$ ($\mu$m/s)', r'$\dot{R}$ ($\mu$m/s)', r'$ee/l$']
    titles = ['Radius', 'Tension', 'Force', 'Contraction Rate', 'Effective Length', 'Tension Integral', 'Time vs Time', 'Time vs Time', 'Contraction Rate vs Tension']
    
    for i, axi in enumerate(axs):
        plot.plotscatter(fig, axi, xdata[i], ydata[i], cdata[i], xlabel=xlabels[i], ylabel=ylabels[i], clabel=clabels[i], title=titles[i], dotsize=dotsize)
        if titles[i] == 'Time vs Time':
            plot.plotdiagonal(axi)
    plt.tight_layout()
    plt.savefig('paramplots.png')

    # if interactive, run interactive plot
    if interactive:
        plt.close()
        plotter = plot.Plot(xdata, ydata, cdata, xlabels, ylabels, clabels, titles)
        plotter.plot_interactive()

#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])

