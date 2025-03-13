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
   
    for instantiation: needs path to the report binary and a list of the directories

    each variable has an associated extract method that redefines that variable (and only that variable;
    e.g. calling extract_contractionrate will only redefine contraction rate, even though it extracts the
    radius to calculate it). the class methods are split into three sections: the first section extracts stats
    that depend on time; these methods return a tuple of the time list along with the extracted statistic (the self.times
    variable is not changed). the second section is for statistics that don't depend on time; these methods output
    just the statistic. the third section is for extract methods that calculate multiple statistics at a time; these
    methods output a tuple of all asked for statistics, along with time, if available.
    """
    def __init__(self, report, directory):
        self._report = report
        self._directory = directory
        
        # all variables possible to be extracted listed below
        # initialize all data variables as None, so they can be set later
        self.times = None
        self.radius = None
        self.tension = None
        self.force = None
        self.effectivelength = None 
        self.contractionrate = None
        self.tensionintegral = None

    def extract_times(self):
        # extract the list of times
        data = utools.readreport(self._report, "fiber:force", self._directory)
        times = []
        for key, _ in data.items():
            times.append(key)

        #redefine variables
        self.times = times
        return times

    # ------------------------------------------------------- EXTRACT METHODS FOR STATISTICS THAT DEPEND ON TIME ------------------------------------------
    def extract_radius(self):
        # extract the times and radius at each time from the sim
        data = utools.readreport(self._report, "fiber:force", self._directory)
        radius, times = [], []
        for key, val in data.items():
            times.append(key)
            
            x, y = val[1:3]
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

            fx, fy = val[3:5]
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

            t = val[-1]
            tension.append(sum(t) / len(t))
        
        # redefine variables
        self.tension = tension
        return times, tension
    
    def extract_effectivelength(self):
        # extract the effective length (end to end length over real length) of the fibers from 'report fiber'
        data = utools.readreport(self._report, 'fiber', self._directory)
        effectivelength, times = [], []
        
        for key, val in data.items():
            times.append(key)

            l, ee = val[2], val[7]
            effectivelength.append((1 / len(l)) * sum([eei / li for eei, li in zip(ee, l)]))
       
        # redefine variables
        self.effectivelength = effectivelength
        return times, effectivelength
    
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
        for i in range(len(times) - 1):
            dR = rads[i+1] - rads[i]
            dt = times[i+1] - times[i]
            crate_arr.append(dR / dt)
        
        # redefine variables
        self.contractionrate = crate_arr
        # return times[:-1] instead of times since the contraction rate ignores the first time point
        return times[:-1], crate_arr
    
    # ---------------------------------------------------------------------EXTRACT METHODS FOR STATISTICS THAT DON'T DEPEND ON TIME--------------------------------------
    def extract_tensionintegral(self, use_old=False):
        # use quadrature to compute the integral of tension
        # if use_old is set to false, recalculate the tension
        if use_old:
            tension, times = self.tension, self.times
        else:
            temp = self.tension
            times, tension = self.extract_tension()
            self.tension = temp
        
        tensionintegral = sum(tension[:-1]) * (times[1] - times[0])
        
        self.tensionintegral = tensionintegral
        return tensionintegral

    # ----------------------------------------------------------------------EXTRACT METHODS THAT EXTRACT MORE THAN ONE VARIABLE AT A TIME---------------------------------
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
    
    def extract_all(self):
        # extract every listed statistic at one time
        # returns all stats and instantiates every variable in the init method
        output = ()
        output += self.extract_mainstats()
        output += (self.extract_contractionrate(use_old=True)[1],)
        output += (self.extract_effectivelength()[1],) 
        output += (self.extract_tensionintegral(use_old=True),)
        return output
