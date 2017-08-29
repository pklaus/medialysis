#!/usr/bin/env python

import argparse
import wave
import sys
import struct
import audioop
import time
import math
from media import PygletAudioPlayer, PyaudioAudioPlayer

from time_converters import parse_time, format_time

def main():

    parser = argparse.ArgumentParser(description='Analyze RMS values and calculate dB of sections in audio files.')
    parser.add_argument('audiofile', help='Audio file to analyse')
    parser.add_argument('--skip', metavar='SECONDS', default=0.0, type=parse_time, help='Seconds to skip in the beginning')
    parser.add_argument('--chunksize', metavar='SAMPLES', default=2**12, type=int, help='Size of the chunks to analyse')
    parser.add_argument('--threshold-on', metavar='dB', default=-30.0, type=float, help='dB value to start marking a section as interesting.')
    parser.add_argument('--threshold-off', metavar='dB', default=-40.0, type=float, help='dB value to stop marking a section as interesting.')
    parser.add_argument('--confirm-continue', action='store_true', help='If active, you must confirm (press enter) to continue after each interesting section.')
    
    player = None
    try:
        player = PyaudioAudioPlayer()
    except:
        try: player = PygletAudioPlayer()
        except: pass
    if not player: parser.error('This tool requires either PyAudio or pyglet for playback.')
    
    args = parser.parse_args()
    
    w = wave.open(args.audiofile, mode='rb')
    player.open(args.audiofile)
    
    chunksize = args.chunksize
    samplewidth = w.getsampwidth()
    framerate = w.getframerate()
    nchannels = w.getnchannels()
    nframes = w.getnframes()
    
    bit_depth = {1: 'i', 2: 'h'}[samplewidth]
    fmt = f"<{nchannels*chunksize:d}{bit_depth:s}"

    def get_dB(samplevalue):
        samplevalue = max(samplevalue, 1)
        return 20*math.log(float(samplevalue) /(2**15-1))/math.log(10)

    print(f"Total duration: {format_time(nframes/framerate)}")
    print(f"Total # of frames: {nframes}")
    
    # convert skip from s to chunks:
    skipchunks = int(args.skip * framerate / chunksize)
    print(f"Skipping {skipchunks} chunks = {skipchunks * chunksize} frames = {format_time(skipchunks*chunksize/framerate)}")
    
    rms = []
    on = False
    loud_sections_duration = []
    w.setpos(skipchunks*chunksize)
    player.seek(float(skipchunks * chunksize) / framerate)
    time.sleep(0.5)
    i = skipchunks
    while True:
        i += 1
        f = w.readframes(chunksize)
        if len(f) != (chunksize * samplewidth * nchannels):
            #import pdb; pdb.set_trace()
            if w.tell() == nframes:
                print("Analysis arrived to end of file... stopping now")
                break
            print('Incorrect number of samples.')
            print(f"len(f) = {len(f)}  !=  (chunksize * samplewidth * nchannels) = {chunksize} * {samplewidth} * {nchannels} = {chunksize * samplewidth * nchannels}")
            sys.exit(1)
        d = struct.unpack(fmt, f)
        left = d[::2]
        right = d[1::2]
        position = float((i-1) * chunksize) / framerate
        value = audioop.rms(f, samplewidth)
        dB = get_dB(value)
        rms.append(value)
        if not on and dB >= args.threshold_on:
            on = True
            player.seek(position)
            player.play()
            print(f"getting loud at {format_time(position)}")
            sys.stdout.flush()
            loud_rms_values = []
        elif on and dB <= args.threshold_off:
            on = False
            max_rms = max(loud_rms_values)
            print(f"Maximum value in loud phase: {max_rms} ({get_dB(max_rms):.1f} dB)")
            avg_rms = int(sum(loud_rms_values)/float(len(loud_rms_values)))
            print(f"Average value in loud phase: {avg_rms} ({get_dB(avg_rms):.1f} dB)")
            print(f"getting silent at {format_time(position)}")
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
            sys.stdout.write(f"Current power: {dB:5.1f} dB         \r")
            sys.stdout.flush()
            # in confirm-continue mode you may also want to have more time to see the current power:
            if args.confirm_continue: time.sleep(0.001)
    
    if len(loud_sections_duration) > 0:
        print(f"Number of loud sections: {len(loud_sections_duration)}")
        average_sections = sum(loud_sections_duration)/float(len(loud_sections_duration))
        print(f"Average number of chunks in loud sections: {average_sections:.1f}")
        print(f"Average duration of loud sections: {average_sections * chunksize / framerate:.3f} s")
    elif on:
        print("Only 'one' big loud section. Try raising your threshold!")
    else:
        print("No loud sections found!")
    print(f"Analyzed {len(rms)} pieces of {chunksize} samples each.")

if __name__ == "__main__":
    main()
