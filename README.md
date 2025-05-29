# cytosim-analysis-kit

This repository holds all of the data analysis tools that I created for [Cytosim](https://gitlab.com/f-nedelec/cytosim) (a cytoskeleton simulation suite designed by Francois Nedelec, Julio Belmonte, et al).

All the files are python scripts meant to read, analyze, and plot data output by the Cytosim simulation suite.

## Installation
Download in any directory with `git clone https://github.com/KSHobbyProjs/cytosim.git`

## How to Use
running `plotstats.py [directories]`
running `plotparams.py [directories]`

## Utils
The utils directory contains utility modules. extracttools.py contains extraction tools that read stat information from a simulation (wrapping report). collectpics.py collects all images in a directory into a master image

## Helpers

### Data Class
The helper directory contains helper modules to aid in data collection. dataclass.py provides a class that can store all of the data for a simulation. create a class with helpers.dataclass.Data(report, directory) (where report is the path to the report binary, and directory is the path where the simulation files are stored). the data class starts off empty, but every stat has an "extract" command associated with it (if you need one that's not provided, it's very easy to add one to the class by just using creating a function `def extract_[your stat name]():`). Each extract method returns the stat you're looking forplus a time array (if the stat you're looking for is in time). It also populates variables in the class name, so that once you use extract, that data is stored in the class forever. This allows one to picklethe class if it's needed everywhere.

Extract methods that output multiple stats at a time should really only be used for efficiency. For instance, there are two of these method types in `dataclass.Data` simply because it's more efficient to compute multiple stats at one call of `report`.

### Param Class


### Plot Class
