#!/usr/bin/env python
#
# utils class to handle general data collection mechanisms
#
# Copyright  K. Scarbro; 2025--

"""
A helper module containing utility functions. Currently includes a function that acts as a wrapper for 'report'

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

if __name__ == "__main__":
    print(__doc__)
