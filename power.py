#!/usr/bin/env python

import argparse
import wave
import sys
import struct
import audioop
import time
import pyglet
import math

parser = argparse.ArgumentParser(description='Analyze RMS values and calculate dB of sections in audio files.')
parser.add_argument('audiofile', help='Audio file to analyse')
parser.add_argument('--skip', metavar='SECONDS', default=0.0, type=float, help='Seconds to skip in the beginning')
parser.add_argument('--chunksize', metavar='SAMPLES', default=2**12, type=int, help='Size of the chunks to analyse')
parser.add_argument('--threshold-on', metavar='dB', default=-30.0, type=float, help='dB value to start marking a section as interesting.')
parser.add_argument('--threshold-off', metavar='dB', default=-40.0, type=float, help='dB value to stop marking a section as interesting.')
parser.add_argument('--confirm-continue', action='store_true', help='If active, you must confirm (press enter) to continue after each interesting section.')
args = parser.parse_args()

w = wave.open(args.audiofile, mode='rb')
player = pyglet.media.Player()
music = pyglet.media.load(args.audiofile)
player.queue(music)

chunksize = args.chunksize
samplewidth = w.getsampwidth()
framerate = w.getframerate()
nchannels = w.getnchannels()

def get_dB(samplevalue):
    return 20*math.log(float(samplevalue) /(2**15-1))/math.log(10)

# convert skip from s to frames:
skipframes = int(args.skip * framerate / chunksize)
print("Skipping {} frames".format(skipframes))

rms = []
on = False
loud_sections_duration = []
w.setpos(skipframes*chunksize)
player.seek(float(skipframes * chunksize) / framerate)
player.play()
time.sleep(0.5)
i = skipframes
while True:
    f = w.readframes(chunksize)
    if len(f) < (chunksize * samplewidth): break
    d = struct.unpack("<" + str(chunksize) + "h", f)
    position = float(i * chunksize) / framerate
    value = audioop.rms(f, samplewidth)
    dB = get_dB(value)
    rms.append(value)
    if not on and dB >= args.threshold_on:
        on = True
        player.seek(position)
        player.play()
        sys.stdout.write("                                          \r")
        sys.stdout.flush()
        print("getting loud at {:.3f} s".format(position))
        loud_rms_values = []
    elif on and dB <= args.threshold_off:
        on = False
        max_rms = max(loud_rms_values)
        print("Maximum value in loud phase: {} ({:.1f} dB)".format(max_rms, get_dB(max_rms)))
        avg_rms = int(sum(loud_rms_values)/float(len(loud_rms_values)))
        print("Average value in loud phase: {} ({:.1f} dB)".format(avg_rms, get_dB(avg_rms)))
        print("getting silent at {:.3f} s".format(position))
        loud_sections_duration.append(len(loud_rms_values))
        while (position - player.time > -0.2):
            st = position - player.time + 0.2
            if st > 0.0: time.sleep(st)
            else: break
        player.pause()
        if args.confirm_continue:
            input("Please press [Enter] to continue")
    if on:
        loud_rms_values.append(value)
    else:
        sys.stdout.write("Current value: {:5d} ({:.1f} dB)        \r".format(value, dB))
        sys.stdout.flush()
    i += 1

if len(loud_sections_duration) > 0:
    print("Number of loud sections: {}".format(len(loud_sections_duration)))
    average_sections = sum(loud_sections_duration)/float(len(loud_sections_duration))
    print("Average number of pieces in loud section: {:.1f}".format(average_sections))
    print("Average duration of loud section: {:.3f} s".format( average_sections * chunksize / framerate ))
else:
    print("No loud sections found!")
print("Analyzed {} pieces of {} samples each.".format(len(rms), chunksize))

