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
    plotparams.py directory [...] [-i] [name=None] [dotsize=200]
    - directory: the paths to the directories containing simulation information
    - name: the name of the parameters given as a list of strings (example: name=['motors','fibers']
    - dotsize: the size of the parameter dots (default is 200)
    - -i: this sets the plotting environment into interactive mode, allowing for plot adjustments in real time

Output:
    - Outputs a png image of all parameter plots in the directory where the module was called
    - if -i is set, an interactive plotting window is opened that allows you to alter plots in real time 

Note:
    This module assumes that you've configured the config files so that the system parameters that are
    being varied are listed at the top of the config.cym page. See utils.extracttools.readconfig()

K. Scarbro 3.1.2025
"""

import sys
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit(1)

#----------------------------------------------------------------------------------------------------
def main(args):
    pass

#--------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].endswith("help"):
        print(__doc__)
    else:
        main(sys.argv[1:])

