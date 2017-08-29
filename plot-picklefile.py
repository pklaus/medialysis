#!/usr/bin/env python

import pickle
import sys

import matplotlib as mpl
mpl.rcParams['agg.path.chunksize'] = 10000
from matplotlib import pyplot as plt
from datetime import datetime as dt, timedelta as td
import numpy as np

def myFormatter(in_value_in_seconds, pos=None):
    hours = int(in_value_in_seconds//(3600))
    in_value_in_seconds -= hours * 3600
    mins = int(in_value_in_seconds//(60))
    in_value_in_seconds -= mins * 60
    secs = int(in_value_in_seconds)

    return f"{hours:02d}:{mins:02d}:{secs:02d}"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('picklefile')
    args = parser.parse_args()

    with open(args.picklefile, "rb") as f:
        above_thresh = pickle.load(f)

    above_thresh = np.log(above_thresh)

    #x_td = [td(seconds=i) for i in range(len(above_thresh))]
    x = [i/30. for i in range(len(above_thresh))]

    ax = plt.gca()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(myFormatter))
    #ax.xaxis.set_major_formatter(myFormatter)
    #plt.plot_date(x_td, above_thresh)
    plt.plot(x, above_thresh)
    #ax.set_yscale("log", nonposy='clip')
    #plt.semilogy(x, above_thresh)
    plt.show()

if __name__ == "__main__": main()
