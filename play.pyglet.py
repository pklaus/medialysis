#!/usr/bin/env python

import sys

try:
    wavefile = sys.argv[1]
except:
    print("specify wave file!"); sys.exit(2)

import pyglet

player = pyglet.media.Player()


music = pyglet.media.load(wavefile)

player.queue(music)
player.play()
import time

while True:
    time.sleep(2)
    player.seek(12.0)

pyglet.app.run()

