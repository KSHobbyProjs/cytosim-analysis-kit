#!/usr/bin/env python
#   
# A class to extract and store data information
#
# Copyright K. Scarbro; 2025--

"""
A helper module to handle all types of plotting as it pertains to Cytosim

Plot class only needs to take an instance of the Param class, a list of
K. Scarbro 2.28.25
"""

import sys
try:
    import matplotlib as plt
    import matplotlib.widgets as widget
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit()

class Plot():
    def __init__(self, data):
        self._fig, self._ax = fig, ax
        self.xlabel = None
        self.ylabel = None
        self.title = None

    def initialize_interactive(self):
        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0.25, bottom=0.25)
        scatter = plotscatter(fig, ax)

    def iterate(self):
        pass


def plot(ax, xdata, ydata, **kwargs):
    # plotting wrapper
    dotcolor = 'orange'
    dotstyle = 'o-'
    for key, val in kwargs.items():
        if key == 'xlabel': ax.set_xlabel(val)
        elif key == 'ylabel': ax.set_ylabel(val)
        elif key == 'title': ax.set_title(val)
        elif key == 'dotcolor': dotcolor = val
        elif key == 'dotstyle': dotstyle = val
        else: sys.stdout.write(f"{key} is an unknown parameter. Ignored.")
    ax.plot(xdata, ydata, dotstyle, color=dotcolor)

def plotscatter(fig, ax, xdata, ydata, cdata, **kwargs):
    clabel = None
    dotsize = 200
    for key, val in kwargs.items():
        if key == 'xlabel': ax.set_xlabel(val)
        elif key == 'ylabel': ax.set_ylabel(val)
        elif key == 'title': ax.set_title(val)
        elif key == 'clabel': clabel = val
        elif key == 'dotsize': dotsize = val
        else: sys.stdout.write(f"{key} is an unknown parameter. Ignored.")

    pos = ax.scatter(xdata, ydata, c=cdata, cmap='viridis', s=dotsize)
    fig.colorbar(pos, ax=ax, label=clabel)

def plotdiagonal(ax):
    xlims, ylims = ax.get_xlim(), ax.get_ylim()
    ax.plot([xlims[0], xlims[1]], [xlims[0], xlims[1]], color='red', linestyle='--')
