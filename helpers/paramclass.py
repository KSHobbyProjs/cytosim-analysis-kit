#!/usr/bin/env python
#
# A helper module holding a class to store parameter plot information
#
# Copyright K. Scarbro; 2025--

"""
A helper module to extract parameter information from directories. 

K. Scarbro 2.27.2025
"""

import sys
import helpers.dataclass as dclass
import utils.extracttools as utools
try:
    import matplotlib.pyplot as plt
except ImportError:
    sys.stderr.write("Error: could not load matplotlib\n")
    sys.exit(1)

class Param:
    """
    handles storing of parameter information
    
    self.params has length = number of parameter types. each row in self.params will be one type of parameter, and each value will
    be the value of that parameter type for a given simulation

    self.peaks is a dictionary that contains peak information for various stats. the key is the stat name, and the val is the list of
    peak information and time-at-peak information (if available)
    """
    def __init__(self, report, directories):
        self._report = report
        self._directories = directories

        # initialize parameter arrays to be defined later. 
        self.params = None
        
        # initialize peak dictionary. each peak type will be stored here
        self.peaks = dict()

    def extract_paramvals(self):
        # read parameter values from config file in each directory
        param_list = [utools.readconfig(direc) for direc in self._directories]
        param_list = [list(elem) for elem in zip(*param_list)]
        
        self.params = param_list
        return param_list

    def extract_peaks(self, stat, peaktype=0):
        """
        calculates the peak value of a statistic in each sim directory and outputs them in a list
        - stat: the statistic you want to take the peak values of in the form of a string (ex: 'radius')
        - peaktype: 1, 2, or 3; the type of peak (max, min, or absolute peak) to take data with respect to
        returns a list of peak data. if time is given, the list will be comprised of tuples where the first element
        is the is the time at which the peak occured and the second element of the tuple is the peak value
        """
        # check if stat is mainstats or all since those should be handled differently
        if stat == 'mainstats':
            return self.extract_mainpeaks()
        elif stat == 'all':
            return self.extract_allpeaks()
        
        # if stat is not mainstats or all, continue
        peaks = []
        for direc in self._directories:
            data = dclass.Data(self._report, direc)
            evaltool = 'data.extract_' + stat + '()'
            vals = eval(evaltool)
            
            # check type of output from extract. if a tuple, calculate peak with tdata; if a list, calculate just the peak; if a 
            # float or an integer, don't try to calculate the peak: instead, just append the value (as in the case for tension integral)
            if isinstance(vals, tuple):
                tpeak, peak = utools.extract_peak(vals[1], tdata=vals[0], peaktype=peaktype)
                peaks.append((tpeak, peak))
            elif isinstance(vals, list):
                peak, = utools.extract_peak(vals, peaktype=peaktype)
                peaks.append(peak)
            elif isinstance(vals, float) or isinstance(vals, int):
                peaks.append(vals)
            else:
                raise TypeError("Error: extract output must be of the form tuple, list, float, or int\n")
        
        # change variable
        self.peaks[stat] = peaks
        return peaks

    def extract_mainpeaks(self):
        # grab the peaks of the radius, tension, and force at the same time
        peakradius, peaktension, peakforce = [], [], []
        for direc in self._directories:
            data = dclass.Data(self._report, direc)
            vals = data.extract_mainstats()
            peakradius.append(utools.extract_peak(vals[1], tdata=vals[0], peaktype=2))
            peaktension.append(utools.extract_peak(vals[2], tdata=vals[0], peaktype=0))
            peakforce.append(utools.extract_peak(vals[3], tdata=vals[0], peaktype=1))

        self.peaks['radius'] = peakradius
        self.peaks['tension'] = peaktension
        self.peaks['force'] = peakforce
        return peakradius, peaktension, peakforce

    def extract_allpeaks(self):
        # grab the peaks of radius, tension, force, contraction rate, effective length, and grab the integral of the tension
        peakradius, peaktension, peakforce, peakcrate, peakeelength, tensionintegral = [], [], [], [], [], []
        for direc in self._directories:
            data = dclass.Data(self._report, direc)
            vals = data.extract_all()
            peakradius.append(utools.extract_peak(vals[1], tdata=vals[0], peaktype=2))
            peaktension.append(utools.extract_peak(vals[2], tdata=vals[0], peaktype=0))
            peakforce.append(utools.extract_peak(vals[3], tdata=vals[0], peaktype=1))
            peakcrate.append(utools.extract_peak(vals[4], tdata=vals[0][:-1], peaktype=0))
            peakeelength.append(utools.extract_peak(vals[5], tdata=vals[0], peaktype=2))
            tensionintegral.append(vals[6])
        
        self.peaks['radius'] = peakradius
        self.peaks['tension'] = peaktension
        self.peaks['force'] = peakforce
        self.peaks['contractionrate'] = peakcrate
        self.peaks['effectivelength'] = peakeelength
        self.peaks['tensionintegral'] = tensionintegral
        return peakradius, peaktension, peakforce, peakcrate, peakeelength, tensionintegral 
