#!/usr/bin/env python
#   
# A class to extract and store data information
#
# Copyright K. Scarbro; 2025--

"""
A helper module to handle all types of plotting as it pertains to Cytosim

Dependencies:
    - matplotlib: install with pip via 'pip install matplotlib'
    - PyQt6: install with pip via 'pip install PyQt6'

Plot class only needs to take an instance of the Param class, a list of
K. Scarbro 2.28.25
"""

import sys
try:
    import matplotlib.pylab as plt
    import matplotlib.widgets as widget
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit()

class Plot():
    """
    A class to handle an interactive plotting environment

    initialize with a list of lists for xdata, ydata, zdata, xlabels, ylabels, zlabels, and titles corresponding to all the different plots to cycle from
    """
    def __init__(self, xdata=[None], ydata=[None], zdata=[None], xlabels=[None], ylabels=[None], zlabels=[None], titles=[None]):
        self._fig, self._ax = plt.subplots()
        # xdata, ydata, and zdata need to have the same length:
        if len(xdata) != len(ydata) or len(xdata) != len(zdata):
            raise ValueError("Error: xdata, ydata, and zdata need to have the same length.")
        # the user needs to put xdata, ydata, and zdata, but all labels and titles aren't necessary
        # the labels and titles lists need to be the same length as the xdata, ydata, and zdata lists, 
        # so add None to each label list for each element they're missing
        self.xlabels = xlabels if len(xlabels) >= len(xdata) else xlabels + [None for _ in range(0, len(xdata) - len(xlabels))]
        self.ylabels = ylabels if len(ylabels) >= len(ydata) else ylabels + [None for _ in range(0, len(ydata) - len(ylabels))]
        self.zlabels = zlabels if len(zlabels) >= len(zdata) else zlabels + [None for _ in range(0, len(zdata) - len(zlabels))]
        self.titles = titles if len(titles) >= len(xdata) else titles + [None for _ in range(0, len(xdata) - len(titles))]
        self.xdata = xdata
        self.ydata = ydata
        self.zdata = zdata

        self._index = 0
        # self._scatter and self._cbar is initialized in plot_interactive
        self._scatter = None
        self._cbar = None

    def plot_interactive(self):
        self._fig.subplots_adjust(right=0.75)
        # text that says color scale
        ax_text = self._fig.add_axes([0.85, .85, 0.1, 0.025])
        ax_text.set_axis_off()
        ax_text.text(0, 0, 'color scale', transform=ax_text.transAxes)
        # widget axes
        ax_zscalemin = self._fig.add_axes([0.85, .8, 0.1, 0.025])
        ax_zscalemax = self._fig.add_axes([0.85, .75, 0.1, 0.025]) 
        ax_dotsize = self._fig.add_axes([0.87, .65, 0.1, 0.025])
        ax_prevplot = self._fig.add_axes([0.82, .60, 0.05, 0.025])
        ax_nextplot = self._fig.add_axes([0.87, .60, 0.05, 0.025])
        # widgets
        textbox_zscalemin = widget.TextBox(ax_zscalemin, 'min', textalignment='center')
        textbox_zscalemax = widget.TextBox(ax_zscalemax, 'max', textalignment='center')
        textbox_dotsize = widget.TextBox(ax_dotsize, 'dotsize', textalignment='center')
        button_prevplot = widget.Button(ax_prevplot, 'prev')
        button_nextplot = widget.Button(ax_nextplot, 'next')
        
        # scatter plot and colorbar
        self._scatter, self._cbar = plotscatter(self._fig, self._ax, self.xdata[0], self.ydata[0], self.zdata[0], \
                xlabel=self.xlabels[0], ylabel=self.ylabels[0], title=self.titles[0], \
                clabel=self.zlabels[0])
        
        # widget actions 
        button_nextplot.on_clicked(self._nextplot)
        button_prevplot.on_clicked(self._prevplot)
        textbox_zscalemin.on_submit(self._changeminscale)
        textbox_zscalemax.on_submit(self._changemaxscale)
        textbox_dotsize.on_submit(self._changedotsize)

        plt.show()

    def _nextplot(self, event):
        self._index += 1
        if self._index >= len(self.xdata):
            self._index -= 1
            return
        self._cbar.remove()
        self._ax.clear()
        self._scatter, self._cbar = plotscatter(self._fig, self._ax, self.xdata[self._index], self.ydata[self._index], self.zdata[self._index], \
                xlabel=self.xlabels[self._index], ylabel=self.ylabels[self._index], title=self.titles[self._index], \
                clabel = self.zlabels[self._index])

    def _prevplot(self, event):
        self._index -= 1
        if self._index < 0:
            self._index += 1
            return
        self._cbar.remove()
        self._ax.clear()
        self._scatter, self._cbar = plotscatter(self._fig, self._ax, self.xdata[self._index], self.ydata[self._index], self.zdata[self._index], \
                xlabel=self.xlabels[self._index], ylabel=self.ylabels[self._index], title=self.titles[self._index], \
                clabel = self.zlabels[self._index])

    def _changedotsize(self, dotsize):
        self._scatter.set_sizes([int(dotsize)])

    def _changemaxscale(self, maxscale):
        current_min = self._cbar.vmin
        self._scatter.set_clim(current_min, float(maxscale)) 

    def _changeminscale(self, minscale):
        current_max = self._cbar.vmax
        self._scatter.set_clim(float(minscale), current_max)

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
    cbar = fig.colorbar(pos, ax=ax, label=clabel)
    return pos, cbar

def plotdiagonal(ax):
    xlims, ylims = ax.get_xlim(), ax.get_ylim()
    ax.plot([xlims[0], xlims[1]], [xlims[0], xlims[1]], color='red', linestyle='--')
