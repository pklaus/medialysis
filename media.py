#!/usr/bin/env python

import wave

class Player(object):

    def play(self):
        raise NotImplemented

    def pause(self):
        raise NotImplemented

    def seek(self, seconds = 0.0):
        raise NotImplemented

class PygletAudioPlayer(Player):

    def __init__(self):
        import pyglet

    def open(self, filename):
        import pyglet
        self.filename = filename
        self.player = pyglet.media.Player()
        music = pyglet.media.load(filename)
        self.player.queue(music)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def seek(self, seconds = 0.0):
        self.player.seek(seconds)

    @property
    def time(self):
        return self.player.time

class PyaudioAudioPlayer(Player):

    """
    Player implemented with PyAudio
     
    http://people.csail.mit.edu/hubert/pyaudio/
     
    Mac OS X:
     
      brew install portaudio
      pip install http://people.csail.mit.edu/hubert/pyaudio/packages/pyaudio-0.2.8.tar.gz
    """
    def __init__(self):
        import pyaudio

    def open(self, filename):
        import pyaudio
        wf = wave.open(filename, 'rb')
        self.p = pyaudio.PyAudio()
        self.pos = 0
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            self.pos += frame_count
            return (data, pyaudio.paContinue)
        self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)
        self.pause()
        self.wf = wf

    def play(self):
        self.stream.start_stream()

    def pause(self):
        self.stream.stop_stream()

    def seek(self, seconds = 0.0):
        self.pos = int(seconds * self.wf.getframerate())
        self.wf.setpos( int(seconds * self.wf.getframerate()) )

    @property
    def time(self):
        return float(self.pos)/self.wf.getframerate()

    @property
    def playing():
        return self.stream.is_active()

    def close():
        self.stream.close()
        self.wf.close()
        self.p.terminate()

