#!/usr/bin/env python

import wave
import sys
import struct
import audioop
import time
import pyglet
import math


try:
    wavefile = sys.argv[1]
except:
    print("specify wave file!"); sys.exit(2)

try:
    skipseconds = float(sys.argv[2])
except:
    skipseconds = 0.0

w = wave.open(wavefile, mode='rb')
player = pyglet.media.Player()
music = pyglet.media.load(wavefile)
player.queue(music)

nframes = 2**12
samplewidth = w.getsampwidth()
framerate = w.getframerate()
nchannels = w.getnchannels()

confirm_continue = True
thresh_on_dB  = -42.
thresh_off_dB = -52.
#thresh_on_dB  = -39.
#thresh_off_dB = -44.
#thresh_on_dB  = -35.
#thresh_off_dB = -39.

def get_dB(samplevalue):
    return 20*math.log(float(samplevalue) /(2**15-1))/math.log(10)

# convert skip from s to frames:
skipframes = int(skipseconds * framerate / nframes)
print("Skipping {} frames".format(skipframes))

rms = []
on = False
loud_sections_duration = []
#for i in range(skipframes):
#    w.readframes(nframes)
w.setpos(skipframes*nframes)
player.seek(float(skipframes * nframes) / framerate)
player.play()
time.sleep(0.5)
i = skipframes
while True:
    f = w.readframes(nframes)
    if len(f) < (nframes * samplewidth): break
    #import pdb; pdb.set_trace()
    d = struct.unpack("<" + str(nframes) + "h", f)
    position = float(i * nframes) / framerate
    value = audioop.rms(f, samplewidth)
    dB = get_dB(value)
    #print(value)
    rms.append(value)
    #if not on and value >= thresh_on:
    if not on and dB >= thresh_on_dB:
        on = True
        player.seek(position)
        player.play()
        sys.stdout.write("                                          \r")
        sys.stdout.flush()
        print("getting loud at {:.3f} s".format(position))
        loud_rms_values = []
    #elif on and value <= thresh_off:
    elif on and dB <= thresh_off_dB:
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
        if confirm_continue:
            input("Please press [Enter] to continue")
    if on: loud_rms_values.append(value)
    else:
        sys.stdout.write("Current value: {:5d} ({:.1f} dB)        \r".format(value, dB))
        sys.stdout.flush()
    i += 1

if len(loud_sections_duration) > 0:
    print("Number of loud sections: {}".format(len(loud_sections_duration)))
    average_sections = sum(loud_sections_duration)/float(len(loud_sections_duration))
    print("Average number of pieces in loud section: {:.1f}".format(average_sections))
    print("Average duration of loud section: {:.3f} s".format( average_sections * nframes / framerate ))
else:
    print("No loud sections found!")
print("Analyzed {} pieces of {} samples each.".format(len(rms), nframes))

