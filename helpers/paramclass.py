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
import multiprocessing as mp
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
    
    for instantiation: needs path to report binary and a list of the directories
    
    self.params has length = number of parameter types. each row in self.params will be one type of parameter, and each value in each
    row will be the value of that parameter type for a given simulation

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

    def _parallel_worker(self, queue, managerlist, worker, *args):
        """
        a wrapper function that wraps all worker-type functions
        """
        while True:
            try:
                i, direc = queue.get(True, 1)
            except:
                break;
            print(f"working on directory {direc}")
            managerlist[i] = worker(direc, *args)

    # ---------------------------------------------EXTRACT PEAKS METHOD FOR ANY STATS THAT DEPEND ON TIME OR STATS THAT DON'T DEPEND ON TIME------------------------------
    def extract_peaks(self, stat, peaktype=0, nproc=1):
        """
        calculates the peak value of a statistic in each sim directory and outputs them in a list
        - stat: the statistic you want to take the peak values of in the form of a string (ex: 'radius')
        - peaktype: the type of peak to calculate
        - nproc: the number of processors to use. nproc=1 is serial
        returns a list of peak data. if time at the peaks is given, the list will be comprised of two elements. the first
        element is the list of the times at which the peaks occur and the second element is the list of peak values
        """
        if nproc > 1:
            # if parallel, create a job for each directory, and run the stat worker in each directory across processors
            nproc = min(nproc, len(self._directories))
            with mp.Manager() as manager:
                queue = mp.Queue()
                for i, direc in enumerate(self._directories):
                    queue.put((i, direc))
                # create a manager to store and transfer the data between processors
                managerlist = manager.list()
                # append an empty list to the manager for each directory
                for _ in range(len(self._directories)):
                    managerlist.append(0)
                # create a list of jobs that run worker with the given args
                jobs = []
                for _ in range(nproc):
                    j = mp.Process(target=self._parallel_worker, args=(queue, managerlist, self._extractpeaks_worker, stat, peaktype))
                    jobs.append(j)
                    j.start()
                for j in jobs:
                    j.join()
                peaks = list(managerlist) 
        else:
            # if serial, then go to each directory, read the data (by calling the stat worker directly), and populate the peak array in serial
            peaks = []
            for direc in self._directories:
                peaks.append(self._extractpeaks_worker(direc, stat, peaktype))

        # if the peaks contain the tdata, zip the times together and the peaks together
        if isinstance(peaks[0], tuple):
            peaks = [list(elem) for elem in zip(*peaks)]
        # change variable
        self.peaks[stat] = peaks
        return peaks

# ------------------------------ EXTRACT PEAK METHODS FOR EXTRACT METHODS IN DATA CLASS THAT OUTPUT MORE THAN ONE STATISTIC AT A TIME -------------------
    def extract_mainpeaks(self, nproc=1):
        # grab the peaks of the radius, tension, and force at the same time
        
        if nproc > 1:
            # if parallel, create a separate job for each directory
            nproc = min(len(self._directories), nproc)
            with mp.Manager() as manager:
                queue = mp.Queue()
                for i, direc in enumerate(self._directories):
                    queue.put((i, direc))
                manradius = manager.list()
                mantension = manager.list()
                manforce = manager.list()
                for i in range(len(self._directories)):
                    manradius.append(0)
                    mantension.append(0)
                    manforce.append(0)
                jobs = []
                for n in range(nproc):
                    j = mp.Process(target=self._extractmainpeaks_worker, args=(queue, manradius, mantension, manforce))
                    jobs.append(j)
                    j.start()
                for j in jobs:
                    j.join()
                peakradius = list(manradius)
                peaktension = list(mantension)
                peakforce = list(manforce)
        else:
            # serial
            peakradius, peaktension, peakforce = [], [], []
            for direc in self._directories:
                data = dclass.Data(self._report, direc)
                vals = data.extract_mainstats()
                peakradius.append(utools.extract_peak(vals[1], tdata=vals[0], peaktype=2))
                peaktension.append(utools.extract_peak(vals[2], tdata=vals[0], peaktype=0))
                peakforce.append(utools.extract_peak(vals[3], tdata=vals[0], peaktype=1))

        # change dictionary variables (these depend on time, so rezip the peak data so that it's a list with time as the first element and peak as the other)
        self.peaks['radius'] = [list(elem) for elem in zip(*peakradius)]
        self.peaks['tension'] = [list(elem) for elem in zip(*peaktension)]
        self.peaks['force'] = [list(elem) for elem in zip(*peakforce)]
        return peakradius, peaktension, peakforce

    def extract_allpeaks(self, nproc=1):
        # grab the peaks of radius, tension, force, contraction rate, effective length, and grab the integral of the tension
        if nproc > 1:
            # if parallel, create a separate job for each directory
            nproc = min(len(self._directories), nproc)
            with mp.Manager() as manager:
                queue = mp.Queue()
                for i, direc in enumerate(self._directories):
                    queue.put((i, direc))
                manradius = manager.list()
                mantension = manager.list()
                manforce = manager.list()
                mancrate = manager.list()
                maneelength = manager.list()
                mantensionintegral = manager.list()
                for i in range(len(self._directories)):
                    manradius.append(0)
                    mantension.append(0)
                    manforce.append(0)
                    mancrate.append(0)
                    maneelength.append(0)
                    mantensionintegral.append(0)
                jobs = []
                for n in range(nproc):
                    j = mp.Process(target=self._extractallpeaks_worker, args=(queue, manradius, mantension, manforce, mancrate, maneelength, mantensionintegral))
                    jobs.append(j)
                    j.start()
                for j in jobs:
                    j.join()
                peakradius = list(manradius)
                peaktension = list(mantension)
                peakforce = list(manforce)
                peakcrate = list(mancrate)
                peakeelength = list(maneelength)
                tensionintegral = list(mantensionintegral)
        else:
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
        
        # change dictionary variables (rezipping the ones that depend on time)
        self.peaks['radius'] = [list(elem) for elem in zip(*peakradius)]
        self.peaks['tension'] = [list(elem) for elem in zip(*peaktension)]
        self.peaks['force'] = [list(elem) for elem in zip(*peakforce)]
        self.peaks['contractionrate'] = [list(elem) for elem in zip(*peakcrate)]
        self.peaks['effectivelength'] = [list(elem) for elem in zip(*peakeelength)]
        self.peaks['tensionintegral'] = tensionintegral
        return peakradius, peaktension, peakforce, peakcrate, peakeelength, tensionintegral 

    # ----------------------------------------------------------------------------WORKERS----------------------------------------------------------------------------
    def _extractpeaks_worker(self, direc, stat, peaktype):
            data = dclass.Data(self._report, direc)
            evaltool = 'data.extract_' + stat + '()'
            vals = eval(evaltool)
     
            if isinstance(vals, tuple):
                tpeak, ppeak = utools.extract_peak(vals[1], tdata=vals[0], peaktype=peaktype)
                peak = (tpeak, ppeak)
            elif isinstance(vals, list):
                peak, = utools.extract_peak(vals, peaktype=peaktype)
            elif isinstance(vals, float) or isinstance(vals, int):
                peak = vals
            else:
                raise TypeError("Error: extract output must be of the form tuple, list, float, or int\n")
            return peak


    def _extractmainpeaks_worker(self, queue, manradius, mantension, manforce):
        while True:
            try:
                i, direc = queue.get(True, 1)
            except:
                break;
            print(f"working on directory {direc}")
            
            data = dclass.Data(self._report, direc)
            vals = data.extract_mainstats()
            manradius[i] = utools.extract_peak(vals[1], tdata=vals[0], peaktype=2)
            mantension[i] = utools.extract_peak(vals[2], tdata=vals[0], peaktype=0)
            manforce[i] = utools.extract_peak(vals[3], tdata=vals[0], peaktype=1)
            

    def _extractallpeaks_worker(self, queue, manradius, mantension, manforce, mancrate, maneelength, mantensionintegral):
        while True:
            try:
                i, direc = queue.get(True, 1)
            except:
                break;
            print(f"working on directory {direc}")

            data = dclass.Data(self._report, direc)
            vals = data.extract_all()
            manradius[i] = utools.extract_peak(vals[1], tdata=vals[0], peaktype=2)
            mantension[i] = utools.extract_peak(vals[2], tdata=vals[0], peaktype=0)
            manforce[i] = utools.extract_peak(vals[3], tdata=vals[0], peaktype=1)
            mancrate[i] = utools.extract_peak(vals[4], tdata=vals[0][:-1], peaktype=0)
            maneelength[i] = utools.extract_peak(vals[5], tdata=vals[0], peaktype=2)
            mantensionintegral[i] = vals[6]
