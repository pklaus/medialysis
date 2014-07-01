#!/usr/bin/env python

import wave
import sys
import struct
import audioop
import time
import pyglet



try:
    wavefile = sys.argv[1]
except:
    print("specify wave file!"); sys.exit(2)

try:
    skip = float(sys.argv[2])
except:
    skip = 0.0

w = wave.open(wavefile, mode='rb')
player = pyglet.media.Player()
music = pyglet.media.load(wavefile)
player.queue(music)

nframes = 2**12
samplewidth = w.getsampwidth()
framerate = w.getframerate()


thresh_on  = 1500
thresh_off = 800

# convert skip from s to frames:
skipframes = int(skip * framerate / nframes)
print("Skipping {} frames".format(skipframes))

rms = []
on = False
loud_sections_duration = []
#for i in range(skipframes):
#    w.readframes(nframes)
w.setpos(skipframes*nframes)
player.seek(float(skipframes * nframes) / framerate)
player.play()
time.sleep(4.5)
i = skipframes
while True:
    f = w.readframes(nframes)
    if len(f) < (nframes * samplewidth): break
    d = struct.unpack("<" + str(nframes) + "h", f)
    position = float(i * nframes) / framerate
    value = audioop.rms(f, samplewidth)
    #print(value)
    rms.append(value)
    if not on and value >= thresh_on:
        on = True
        player.seek(position)
        player.play()
        print("getting loud at {:.3f} s".format(position))
        loud_rms_values = []
    elif on and value <= thresh_off:
        on = False
        while (position - player.time > -0.2):
            st = position - player.time + 0.2
            if st > 0.0: time.sleep(st)
            else: break
        player.pause()
        print("Maximum value in loud phase: {}".format(max(loud_rms_values)))
        print("Average value in loud phase: {}".format(int(sum(loud_rms_values)/float(len(loud_rms_values)))))
        print("getting silent at {:.3f} s".format(position))
        loud_sections_duration.append(len(loud_rms_values))
    if on: loud_rms_values.append(value)
    i += 1

if len(loud_sections_duration) > 0:
    print("Number of loud sections: {}".format(len(loud_sections_duration)))
    average_sections = sum(loud_sections_duration)/float(len(loud_sections_duration))
    print("Average number of pieces in loud section: {:.1f}".format(average_sections))
    print("Average duration of loud section: {:.3f} s".format( average_sections * nframes / framerate ))
else:
    print("No loud sections found!")
print("Analyzed {} pieces of {} samples each.".format(len(rms), nframes))

