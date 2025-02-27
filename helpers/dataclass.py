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
import utils.readreport
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit(1)

class Data:
    """
    handles statistics of a simulation. needs what type of report to use and what directory the sim is in
    """
    def __init__(self, report, directory):
        self._report = report
        self._directory = directory
        
        self.times, self.radius, self.tension, self.force = self._extract_mainstats()
        self.effective_length = self._extract_effectivelength() 
        self.contraction_rate = self._compute_contractionrate()
        self.tension_integral = self._compute_tensionintegral()

        self.peak_tension = max(self.tension) if abs(max(self.tension)) > abs(min(self.tension)) else min(self.tension)
        self.peak_contractionrate = max(self.contraction_rate) if abs(max(self.contraction_rate)) > abs(min(self.contraction_rate)) else min(self.contraction_rate)
        self.peak_force = max(self.force) if abs(max(self.force)) > abs(min(self.force)) else min(self.force)
        self.min_radius = min(self.radius)

    def _extract_mainstats(self):
        # extract times, radii, force, and tension
        data = utils.readreport.readreport(self._report, "fiber:force", self._directory)
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
            
        return times, radius, tension, force    

    def _extract_effectivelength(self):
        # extract the effective length (end to end length over real length) of the fibers from 'report fiber'
        data = utils.readreport.readreport(self._report, 'fiber', self._directory)
        effective_length = []
        
        for _, val in data.items():
            l, ee = val[2], val[7]
            effective_length.append((1 / len(l)) * sum([eei / li for eei, li in zip(ee, l)]))
        
        return effective_length

    def _compute_contractionrate(self):
        # use finite difference to approximate contraction rate
        crate_arr = []
        for i in range(1, len(self.times)):
            dR = self.radius[i] - self.radius[i-1]
            dt = self.times[i] - self.times[i-1]
            crate_arr.append(dR / dt)
        return crate_arr
    
    def _compute_tensionintegral(self):
        # use quadrature to compute the integral of tension
        return sum(self.tension[:-1]) * (self.times[1] - self.times[0])
    
    def plot(self, axis, xdata, ydata, **kwargs):
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
