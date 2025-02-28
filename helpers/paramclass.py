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
    """
    iteration = 0

    def __init__(self, report, directories):
        self._report = report
        self._directories = directories

        # initialize parameter arrays to be defined later. 
        self.params = None
        self.xparams = None
        self.yparams = None
        self.params = [list(elem) for elem in zip(*[utools.readconfig(direc) for direc in self._directories]))]
        self.xparams = self.params[0]
        self.yparams = self.params[1]
        
        # initialize variables of peak values for each parameter
        self.peak_radii = None
        self.peak_contractionrates = None
        self.peak_tensions = None
        self.peak_forces = None
        self.tension_integrals = None

        self.peaks = dict()

    def extract_peakradii(self):
        pass

    def extract_peakcontractionrate(self):
        pass

    def extract_peaktensions(self):
        pass

    def extract_peakforces(self):
        pass

    def extract_tensionintegrals(self):
        pass
    
    def _readpeaks(self, peak_type):
        peaks = []
        for directory in self._directories:
            data = dclass.Data(self._report, directory)
            data.extract_all()
        

    
