#!/usr/bin/env python
#
# A helper module holding a class to store parameter plot information
#
# Copyright K. Scarbro; 2025--

"""
A helper module to extract parameter information from directories.

extract_paramvals() will read the config file in each directory to grab the values of the parameters
extract_peaks(stat, peaktype, nproc) will use the dataclass module to extract a statistic and find its
    peak (peaktype tells the function what type of peak to take). stat is a string of one of the statistics
    from the dataclass module (ex: 'radius'). all statistics from dataclass are covered. if it's one of the 
    dataclass statistics that output multiple statistics (like 'all' or 'mainstats'), extract_peaks will
    output a dictionary where the keys are the stats output, and the vals are the peak data

each call of extract_peaks updates the self.peaks variable with the stat and its peak info

K. Scarbro 3.15.2025
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

    # ---------------------------------------------EXTRACT PEAKS METHOD FOR ANY STATS THAT DEPEND ON TIME OR STATS THAT DON'T DEPEND ON TIME------------------------------
    def extract_peaks(self, stat, peaktype=0, nproc=1):
        """
        calculates the peak value of a statistic in each sim directory and outputs them in a list
        - stat: the statistic you want to take the peak values of in the form of a string (ex: 'radius')
        - peaktype: the type of peak to calculate; this is only necessary if stat != mainstats and stat != all
        - nproc: the number of processors to use. nproc=1 is serial
        returns a list of peak data. if time at the peaks is given, the list will be comprised of two elements. the first
        element is the list of the times at which the peaks occur and the second element is the list of peak values
        if stat == mainstats or stat == all, the output will be a dictionary where the keys are the type of stat, and the values
        are the lists of peak data
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


        # if the peaks come from a worker that returns many stats at once (extractall_worker or extractmainstats_worker),
        # the worker outputs a list of dictionaries where the key is a stat name and the value is the result; unpack
        # the dictionary and use it to update self.peaks; then, return a dictionary zipping the list of dictionaries
        if isinstance(peaks[0], dict):
            keys = list(peaks[0].keys())
            vals = [list(elem) for elem in zip(*[peak.values() for peak in peaks])]
            for i, val in enumerate(vals):
                if isinstance(val[0], tuple):
                    vals[i] = [list(vali) for vali in zip(*val)]
            for key, val in zip(keys, vals):
                self.peaks[key] = val
            return dict(zip(keys, vals))
        # otherwise, the output of the worker should be a list of floats / ints or a list
        # of 2d tuples (the first index being the time of the peak, and the second element 
        # being the peak). if the output is a 2d tuple, zip the times together and the peaks together
        elif isinstance(peaks[0], tuple):
            peaks = [list(peak) for peak in zip(*peaks)]
            self.peaks[stat] = peaks
        # change variable
        self.peaks[stat] = peaks
        return peaks


    # ----------------------------------------------------------------------------WORKERS----------------------------------------------------------------------------
    def _extractpeaks_worker(self, direc, stat, peaktype):
        """
        worker for all stats
        """
        # if the stat is mainstats or all, then redirect to a different worker since these need to be handled differently
        # than all other stat types
        if stat == 'mainstats':
            return self._extractmainstats_worker(direc)
        if stat == 'all':
            return self._extractall_worker(direc)

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

    def _extractmainstats_worker(self, direc):
        """
        worker function for the stats output by extract_mainstats
        """
        data = dclass.Data(self._report, direc)
        vals = data.extract_mainstats()
        peak = dict()
        peak['radius'] = utools.extract_peak(vals[1], tdata=vals[0], peaktype=2)
        peak['tension'] = utools.extract_peak(vals[2], tdata=vals[0], peaktype=0)
        peak['force'] = utools.extract_peak(vals[3], tdata=vals[0], peaktype=1)
        return peak

    def _extractall_worker(self, direc):
        """
        worker function for the stats output by extract_all
        """
        data = dclass.Data(self._report, direc)
        vals = data.extract_all()
        peak = dict()
        peak['radius'] = utools.extract_peak(vals[1], tdata=vals[0], peaktype=2)
        peak['tension'] = utools.extract_peak(vals[2], tdata=vals[0], peaktype=0)
        peak['force'] = utools.extract_peak(vals[3], tdata=vals[0], peaktype=1)
        peak['contractionrate'] = utools.extract_peak(vals[4], tdata=vals[0][:-1], peaktype=0)
        peak['effectivelength'] = utools.extract_peak(vals[5], tdata=vals[0], peaktype=2)
        peak['tensionintegral'] = vals[6]
        return peak
    
    def _parallel_worker(self, queue, managerlist, worker, *args):
        """
        a wrapper function that wraps all worker-type functions when using parallel
        """
        while True:
            try:
                i, direc = queue.get(True, 1)
            except:
                break;
            print(f"working on directory {direc}")
            managerlist[i] = worker(direc, *args)

