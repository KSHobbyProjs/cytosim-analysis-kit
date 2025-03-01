#!/usr/bin/env python
#   
# A class to extract and store data information
#
# Copyright K. Scarbro; 2025--

"""
A helper module to handle all types of plotting as it pertains to Cytosim

K. Scarbro 2.28.25
"""

import sys
try:
    import matplotlib as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit()

class Plot():
    pass

def plot(axis, xdata, ydata, **kwargs):
    # plotting wrapper
    ax = axis
    pic_name = 'plot'
    dot_color = 'orange'
    dot_style = 'o-'
    for key, val in kwargs.items():
        if key == 'xlabel': ax.set_xlabel(val)
        elif key == 'ylabel': ax.set_ylabel(val)
        elif key == 'title': ax.set_title(val)
        elif key == 'dot_color': dot_color = val
        elif key == 'dot_style': dot_style = val
        elif key == 'pic_name': pic_name = val
    ax.plot(xdata, ydata, dot_style, color=dot_color)

