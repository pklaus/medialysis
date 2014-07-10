#!/usr/bin/env python

import sys
import time
import wave
import pymedia.audio.sound as sound

try:
    wavefile = sys.argv[1]
except:
    print("specify wave file!"); sys.exit(2)

f= wave.open(wavefile, 'rb')

snd = sound.Output( f.getframerate(), f.getnchannels(), format=sound.AFMT_S16_LE)
s = f.readframes( 300000 )
snd.play( s )
while snd.isPlaying():
    time.sleep( 0.05 )

