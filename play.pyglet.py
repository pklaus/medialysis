#!/usr/bin/env python

import sys
import pyglet

try:
    wavefile = sys.argv[1]
except:
    print("specify wave file!"); sys.exit(2)

player = pyglet.media.Player()
music = pyglet.media.load(wavefile)
player.queue(music)
player.play()
pyglet.app.run()

