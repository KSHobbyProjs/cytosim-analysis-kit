#!/usr/bin/env python
#
# utils class to handle general data collection mechanisms
#
# Copyright  K. Scarbro; 2025--

"""
A helper module containing utility functions. Currently includes a function that acts as a wrapper for 'report',
a function that extracts the peak value from a list, and a function that reads the parameter values from config files.

K. Scarbro 2.26.25
"""

import os

def readreport(report, command, directory):
    """
    - report: path to report binary
    - command: command to feed report (like 'fiber:force')
    - directory: path to directory where simulation is stored
    reads the output of 'report command directory' to extract data from a simulation.
    the data is given in a dictionary. the keys are the time, and the vals are arrays of the
    data at that time. each row of the array corresponds to a column of the output from report
    """
    # cd into new directory and run report
    cwd = os.getcwd()
    os.chdir(directory)
    os.system(report + ' ' + command + ' > tmp.txt')
    
    # extract all columns into an array
    with open('tmp.txt', 'r') as file:
        lines = file.readlines()

        data_dict = dict()
        for line in lines[1:]:
            if line.startswith('% time'):
                time = float(line[7:].strip())
                data_dict[time] = []
            elif not line.startswith('%') and not line.startswith('\n'):
                # inconsistent delimeter spacing, so split by delimeter ' ', and remove all '' elements:
                line_list = list(filter(lambda b: b, line.strip().split(' ')))
                data_dict[time].append([float(val) for val in line_list])
    
    # transpose the matrix so columns of data are rows in the array
    for key, val in data_dict.items():
        data_dict[key] = [list(row) for row in zip(*val)]

    # delete temporary txt file and cd back to cwd
    os.remove('tmp.txt')
    os.chdir(cwd)
    return data_dict

def extract_peak(xdata, tdata=None, peaktype=0):
    """
    - xdata: list of numbers
    - tdata: list of numbers of the same length as xdata
    - peaktype: 1, 2, or 3; gives the type of peak (max, min or absolute peak) to take from xdata
    extract the peak value of a list xdata
    if tdata is given, it gives the value of tdata at the same index where the peak value of xdata is
    if peaktype is given, take absolute peak (peaktype=0), max (peaktype=1), or min (peaktype=2)
    """
    output = ()
    if peaktype == 0:
        peak = max(xdata) if abs(max(xdata)) > abs(min(xdata)) else min(xdata)
    elif peaktype == 1:
        peak = max(xdata)
    elif peaktype == 2:
        peak = min(xdata)
    else: 
        raise ValueError("you tried to use extract_peak with a peaktype value that isn't 0, 1, or 2\n") 
        
    if tdata is not None:
        if len(tdata) != len(xdata):
            raise IndexError("xdata and tdata need to have equal lengths\n")
        else:
            peakt = tdata[xdata.index(peak)]
            output += (peakt,)
    output += (peak,)

    return output

def readconfig(directory, numparams=2):
    """
    helper function to help create parameter maps. reads parameter values from a config file
    and outputs them in a list
    - directory: path to simulation directory with config file in it
    - numparams: the number of parameters listed at the top of the config file
    assumes that the values the parameters are listed at the top of the config file
    in either the form %####%####... or %#### (or even of some form  %####%####...n times )
                                        %####                        %####%####...m times
                                        ...                          ...

    example: multiple config files are created with preconfig.py such that each config
    file creates a sim with a different number of motors or fibers. the top of the config file
    representing the sim with 1000 motors and 5000 fibers could look like %1000%5000 or %1000;
    readconfig reads these numbers and outputs them as the list [1000,5000].            %5000 
    """
    # cd into directory path to find config file
    cwd = os.getcwd()
    os.chdir(directory)
    file_name = 'config.cym'
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            params = []
            lines = file.readlines()
            for line in lines:
                if len(params) == numparams: 
                    # break if the params has collected all parameters
                    break
                if line.startswith('%'):
                    params.extend(line[1:].strip().split('%'))
                else:
                    raise ValueError(f"the first lines of the config file at {file_name} contain less than {numparams} parameters\n")
    else:
        raise FileNotFoundError(f"config file at {file_name} not found\n")
  
    params = [float(param) for param in params]
    # cd back into cwd
    os.chdir(cwd)
    return params


if __name__ == "__main__":
    print(__doc__)
