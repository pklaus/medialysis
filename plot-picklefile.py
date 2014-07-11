#!/usr/bin/env python

import pickle
import sys

try:
    picklefile = sys.argv[1]
except:
    print("Specify pickle file and plot like this:")
    print("./plot-picklefile.py datafile.p | gnuplot -persistant")
    sys.exit(2)

values = pickle.load( open( picklefile, "rb" ) )

print("# The output of this tool can directly be fed into gnuplot via the pipe '|'")
print("# number of values: {}".format(len(values))
print("set yrange [0:20 < * < 200]")
print("plot '-' with filledcurves")
for i in range(len(above_thresh)):
    print("{:.3f} {:3d}".format(i, above_thresh[i]))
print("e")
