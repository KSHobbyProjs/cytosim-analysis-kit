#!/usr/bin/env python
#
# calculate_forces.py calculates the total force, radius of gyration, and contraction rate of the network per time
#
# Copyright  K. Scarbro; 2025--

"""
    Calculate either the total force per time on the fibers, the radius of gyration
    of the network per time, or the contraction rate of the network per time.

Syntax:
    calculate_forces.py command file_name1 [file_name2] [...]

    - command: either force (measures forces), radg (measures the radius of gyration), crate (measures
    the contraction rate, or all (measures all of these)
    - file_name1: the file name that the program needs to search to find the data
    - if other file_name are given, it will calculate the values using the data from these files as well

Output:
     file_name1_force/radg/crate.txt file. the first column is time, and the second column is either force,
     radius, or contraction rate. 
     the number of .txt files output will equal the number of file_names entered 

Examples:
    calculate_forces.py force myforces.txt
    calculate_forces.py radg mypositions.txt
    calculate_forces.py crate mypositions1.txt mypositions2.txt

K. Scarbro 01.2025
"""

try:
    import sys, os
    import matplotlib.pylab as plt
except ImportError:
    sys.stderr.write("Error: could not load necessary python modules\n")
    sys.exit()
    
#------------------------------------------------------------------------------------------
def execute(tool, path):
    """
    calculate forces, radius of gyration, or rate of contraction from file
    """
    with open(path, 'r') as file:
        lines = file.readlines()
        
        # find number of frames
        for line in lines[::-1]:
            if line.startswith('% frame'):
                totframes = int(line[10:])
                break

        time_arr = []
        radg_arr = []
        force_arr = []
        tension_arr = []
        for line in lines[1:]:
            if line.startswith('% frame'):
                framenum = int(line[10:])
            elif line.startswith('%   fiber'):
                # no data on the first loop, if not line.contains(...) provides buffer
                if not 'f1:0001' in line:
                    force_tot += ( force[0]**2 + force[1]**2 )**(1 / 2)
                # reset forces on individual fibers
                force = [0, 0]
            elif line.startswith('% time'):
                time = float(line[7:])
                time_arr.append(time)
                # everytime we reach a new time point, store radg and force in array
                # the data is found after we read time, so we don't have any data the first time we read % time;
                # if framenum != 0 ensures that we don't try to use data that we don't have yet
                if framenum != 0:
                    radg = ( (1 / N) * (rsqrd[0] + rsqrd[1]) - (1 / N)**2 * (mu[0]**2 + mu[1]**2) )**(1 / 2)
                    radg_arr.append(radg)

                    # the last fiber's info isn't included; include it here
                    force_tot += ( force[0]**2 + force[1]**2)**(1 / 2)
                    force_arr.append(force_tot)
                    
                    tension_arr.append(tension)

                # reset model points, average (mu), radius squared (rsqrd), and total force
                mu = [0, 0]
                rsqrd = [0, 0]
                N = 0
                force_tot = 0
                tension = 0
            elif not line.startswith('%') and not line.startswith('\n'):
                # this means the line's giving information about a model point, so increase count of model points:
                N += 1
                
                # variable delimeter spacing, so split by delimeter ' ', then
                # remove all elements of the split line that are empty (''):
                line_list = list(filter(lambda b: b, line.strip().split(' ')))[1:]
               
                mu[0] = mu[0] + float(line_list[0])
                mu[1] = mu[1] + float(line_list[1])

                rsqrd[0] = rsqrd[0] + float(line_list[0])**2
                rsqrd[1] = rsqrd[1] + float(line_list[1])**2

                force[0] = force[0] + float(line_list[2])
                force[1] = force[1] + float(line_list[3])
                
                tension += float(line_list[4])

        # at the end of the file, we read data but don't hit another time flag.
        # we repeat the lines above to ensure that we include this last bit of data        
        tension_arr.append(tension)

        radg = ( (1 / N) * (rsqrd[0] + rsqrd[1]) - (1 / N)**2 * (mu[0]**2 + mu[1]**2) )**(1 / 2)
        radg_arr.append(radg)     

        force_tot += ( force[0]**2 + force[1]**2)**(1 / 2)
        force_arr.append(force_tot)

        # plot force data, ignoring the first point since the force is extemely large due to filaments at the membrane
        fig, ax = plt.subplots()
        ax.plot(time_arr[1:], force_arr[1:])
        ax.set_xlabel('time (s)')
        ax.set_ylabel('forces (pN)')
        ax.set_title('Total Force on the System')
        plt.show()
        

        fig1, ax1 = plt.subplots()
        ax1.plot(time_arr, radg_arr)
        ax1.set_xlabel('time (s)')
        ax1.set_ylabel('Radius of Gyration (um)')
        ax1.set_title('Radius of Gyration')
        plt.show()
        
        fig2, ax2 = plt.subplots()
        ax2.plot(time_arr, tension_arr)
        ax2.set_xlabel('time (s)')
        ax2.set_ylabel('tension (pN)')
        ax2.set_title('Tension')
        plt.show()


def main(args):
    """
        read command line arguments and process commands
    """
    verbose = False
    tool = args[0]
   
    if tool not in ['force', 'radg', 'crate', 'all']: 
        sys.stdout.write("Invalid command: calculate_forces.py command file_name1 [file_name2] [...]\n")
        return 1

    paths = []
    for arg in args[1:]:
        if os.path.isfile(arg):
            paths.append(os.path.abspath(arg))
        elif arg == '-v':
            verbose = True
        else: 
            sys.stdout.write(f"Unexpected argument: {arg}\n")
            sys.exit()

    if not paths:
        sys.stdout.write("Missing file_names: calculate_forces.py command file_name1 [file_name2] [...]\n")
        return 2
    
    for p in paths:
        if verbose:
            sys.stdout.write(f"calculating {tool} from {p}")
        execute(tool, p)

    return 0

#--------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1].endswith("help"):
        print(__doc__)
    else: 
        main(sys.argv[1:])
