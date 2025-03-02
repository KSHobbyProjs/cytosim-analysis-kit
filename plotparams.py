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
    plotparams.py directory [...more directories...] [report='~/Cytosim/cytosim/bin/report'] [name=None] [dotsize=200] [-i] [nproc=1]
    - directory: the paths to the directories containing simulation information
    - name: the name of the parameters given separated by a comma (example: name=motors,fibers)
    - dotsize: the size of the parameter dots (default is 200)
    - -i: this sets the plotting environment into interactive mode, allowing for plot adjustments in real time
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
        elif arg.startswith("nproc="):
            nproc = int(arg[6:])
        else:
            sys.stdout.write(f"unknown input: {arg}\n")
            sys.exit()

    if not paths:
        sys.stdout.write("no directories were given\n")
        sys.exit()

    # extract parameter information, and populate Param class with parameter information
    params = pclass.Param(report, paths)
    params.extract_paramvals()
    params.extract_allpeaks(nproc=nproc)

    # plot the scatter plots of the peak data. it's possible to generalize this to make it shorter, but it's not very readable
    fig, ax = plt.subplots(3, 3, figsize=(15, 15))
    # put the parameter data and label data in a tuple and dictionary just for readability
    paramtuple = (params.params[0], params.params[1])
    labeldict = {'xlabel':xname, 'ylabel':yname, 'dotsize':dotsize}
    # plot the scatter plots, if the peak data contains the time at the peaks, grab the peaks
    plot.plotscatter(fig, ax[0,0], *paramtuple, params.peaks['radius'][1], **labeldict, title='Radius', clabel='Radius')
    plot.plotscatter(fig, ax[0,1], *paramtuple, params.peaks['tension'][1], **labeldict, title='Tension', clabel='Tension (pN)')
    plot.plotscatter(fig, ax[0,2], *paramtuple, params.peaks['force'][1], **labeldict, title='Force', clabel='Force (pN)')
    plot.plotscatter(fig, ax[1,0], *paramtuple, params.peaks['contractionrate'][1], **labeldict, title='Contraction Rate', clabel=r'$\dot{R}$ ($\mu$m/s)')
    plot.plotscatter(fig, ax[1,1], *paramtuple, params.peaks['effectivelength'][1], **labeldict, title='Effective Length', clabel=r'$ee/l$')
    plot.plotscatter(fig, ax[1,2], *paramtuple, params.peaks['tensionintegral'], **labeldict, title='Tension Integral', clabel=r'$\Delta p$ (pN$\cdot$s)')
    plot.plotscatter(fig, ax[2,0], params.peaks['tension'][0], params.peaks['contractionrate'][0], params.peaks['contractionrate'][1], xlabel='$t_{tension}$ (s)',\
            ylabel=r'$t_{\dot{R}}$ (s)', clabel=r'$\dot{R}$ ($\mu$m/s)', title='time vs time')
    plot.plotscatter(fig, ax[2,1], params.peaks['tension'][0], params.peaks['effectivelength'][0], params.peaks['contractionrate'][1], xlabel='$t_{tension}$ (s)',\
            ylabel=r'$t_{ee/l}$ (s)', clabel=r'$\dot{R}$ ($\mu$m/s)', title='time vs time')
    plot.plotscatter(fig, ax[2,2], params.peaks['tension'][1], params.peaks['contractionrate'][1], params.peaks['effectivelength'][1], xlabel='tension', ylabel=r'$\dot{R}$',\
            title='contraction rate vs tension', clabel='ee/l')
    plot.plotdiagonal(ax[2,0])
    plot.plotdiagonal(ax[2,1])
    plt.tight_layout()
    plt.savefig('paramplots.png')

#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])

