#!/usr/bin/env python
#   
# A class to extract and store data information
#
# Copyright K. Scarbro; 2025--

"""
A helper module to extract and store data information in the form of a class. Currently extracts time, radius, contraction rate, force,
tension, integral of tension, and effective length (along with peak values). Equipped with plot wrapper.

K. Scarbro 2.26.25
"""

import sys, os
import utils.extracttools as utools
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit(1)

class Data:
    """
    handles statistics of a simulation. needs what type of report to use and what directory the sim is in
    init method has all stats that can be extracted. they start unpopulated. 
    
    each variable has an associated extract method that redefines that variable (and only that variable;
    e.g. calling extract_contractionrate will only redefine contraction rate, even though it extracts the
    radius to calculate it). the extract methods also return the output 
    """
    def __init__(self, report, directory):
        self._report = report
        self._directory = directory
        
        # initialize all data variables as None, so they can be set later
        self.times = None
        self.radius = None
        self.tension = None
        self.force = None
        self.effective_length = None 
        self.contraction_rate = None
        self.tension_integral = None

        # because of the varying types of peaks you can take, initialize peak
        # data as an empty dictionary and allow user to populate it how they wish
        self.peaks = dict()
    
    def extract_time(self):
        # extract the list of times
        data = utools.readreport(self._report, "fiber:force", self._directory)
        times = []
        for key, _ in data.items():
            times.append(key)

        #redefine variables
        self.times = times
        return times

    def extract_radius(self):
        # extract the times and radius at each time from the sim
        data = utools.readreport(self._report, "fiber:force", self._directory)
        radius, times = [], []
        for key, val in data.items():
            times.append(key)
            
            x, y, _, _, _ = val[1:]
            xx, yy = [xi * xi for xi in x], [yi * yi for yi in y]
            RR = (1 / len(x)) * (sum(xx) + sum(yy)) - (( (1 / len(x)) * sum(x) )**2 + ( (1 / len(y)) * sum(y) )**2)
            radius.append(RR**.5)
        
        # redefine variables
        self.radius = radius
        return times, radius

    def extract_force(self):
        # extract times and force at each time from the sim
        data = utools.readreport(self._report, "fiber:force", self._directory)
        times, force = [], []
        for key, val in data.items():
            times.append(key)

            _, _, fx, fy, _ = val[1:]
            force.append((sum(fx)**2 + sum(fy)**2)**.5 / len(fx))
        
        # redefine variables
        self.force = force
        return times, force

    def extract_tension(self):
        # extract times and tension at each time from the sim
        data = utools.readreport(self._report, "fiber:force", self._directory)
        times, tension = [], []
        for key, val in data.items():
            times.append(key)

            _, _, _, _, t = val[1:]
            tension.append(sum(t) / len(t))
        
        # redefine variables
        self.tension = tension
        return times, tension
    
    def extract_mainstats(self):
        # extract times and radii, force, and tension at each time
        data = utools.readreport(self._report, "fiber:force", self._directory)
        times, radius, tension, force = [], [], [], []
        for key, val in data.items():
            times.append(key)

            x, y, fx, fy, t = val[1:]
            # radius
            xx, yy = [xi * xi for xi in x], [yi * yi for yi in y]
            RR = (1 / len(x)) * (sum(xx) + sum(yy)) - (( (1 / len(x)) * sum(x) )**2 + ( (1 / len(y)) * sum(y) )**2)
            radius.append(RR**.5)
            
            # force
            force.append((sum(fx)**2 + sum(fy)**2)**.5 / len(fx))
            
            # tension
            tension.append(sum(t) / len(t))
        
        # redefine the variables
        self.times, self.radius, self.tension, self.force = times, radius, tension, force
        return times, radius, tension, force    

    def extract_effectivelength(self):
        # extract the effective length (end to end length over real length) of the fibers from 'report fiber'
        data = utools.readreport(self._report, 'fiber', self._directory)
        effective_length, times = [], []
        
        for key, val in data.items():
            times.append(key)

            l, ee = val[2], val[7]
            effective_length.append((1 / len(l)) * sum([eei / li for eei, li in zip(ee, l)]))
       
        # redefine variables
        self.effective_length = effective_length
        return times, effective_length
    
    def extract_contractionrate(self, use_old=False):
        # use finite difference to approximate contraction rate
        # if use_old is set to false, recalculate the radius
        if use_old:
            rads, times = self.radius, self.times
        else:
            # grab radii from extract_radius and reset self.radius
            temp = self.radius
            times, rads = self.extract_radius()
            self.radius = temp

        crate_arr = []
        for i in range(1, len(times)):
            dR = rads[i] - rads[i-1]
            dt = times[i] - times[i-1]
            crate_arr.append(dR / dt)
        
        # redefine variables
        self.contraction_rate = crate_arr
        return times, crate_arr
    
    def extract_tensionintegral(self, use_old=False):
        # use quadrature to compute the integral of tension
        # if use_old is set to false, recalculate the tension
        if use_old:
            tension, times = self.tension, self.times
        else:
            temp = self.tension
            times, tension = self.extract_tension()
            self.tension = temp
        
        tension_integral = sum(tension[:-1]) * (times[1] - times[0])
        
        self.tension_integral = tension_integral
        return tension_integral

    def extract_peak(self, peakname, xdata, tdata=None, peaktype=0):
        # a wrapper for utools.extract_peak
        # populates dictionary with peak data as you extract them
        # the key of the entry added to the dicionary is given by peakname
        peak = utools.extract_peak(xdata, tdata, peaktype)
        self.peaks[peakname] = peak

    def extract_all(self):
        self.extract_mainstats()
        self.extract_effectivelength()
        self.extract_contractionrate(use_old=True)
        self.extract_tensionintegral(use_old=True)

        self.extract_peak('peak_tension', self.tension, self.times)
        self.extract_peak('peak_force', self.force, self.times, 1)
        self.extract_peak('peak_radius', self.radius, self.times, 2)
        self.extract_peak('peak_contractionrate', self.contraction_rate, self.times[1:])
        self.extract_peak('peak_effectivelength', self.effective_length, self.times, 2)

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
