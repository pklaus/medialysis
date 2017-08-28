#!/usr/bin/env python

"""
Modeled after
https://gist.github.com/pklaus/c4fe6a12c6c8e2ff3c16
"""

import sys
import cv2
import numpy as np
import time

settings = {
    'downscale':  2,
    'skipframes': 0,
    'threshold':  20,
    'numthresh':  30,
    'fps':        30.,
}

def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)


def video_analysis(videofile, **kwargs):
    cap = cv2.VideoCapture(videofile)

    winName = "Movement Indicator"
    cv2.namedWindow(winName)

    # Read three images first:
    t_minus = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
    t = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
    t_plus = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)

    wait_to_continue=False
    minisize = (t.shape[1]//kwargs['downscale'], t.shape[0]//kwargs['downscale'])

    above_thresh = []

    framenum = 0
    while framenum < kwargs['skipframes']:
        sys.stdout.write("Frame #: {:8d} ({:.3f} s)    \r".format(framenum, framenum/kwargs['fps']))
        sys.stdout.flush()
        cap.read()
        framenum += 1

    while(cap.isOpened()):
        ret, frame = cap.read()
        if (type(frame) == type(None)):
            break

        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dimg = diffImg(t_minus, t, t_plus)
        diffsum = dimg.sum()
        diffmax = dimg.max()
        npixabovethresh = cv2.threshold(dimg, kwargs['threshold'], 1, cv2.THRESH_BINARY)[1].sum()
        status_output = "Frame #: {:8d} ({:.3f} s)    diff sum: {:4d}    diff max: {:3d}    npix above: {:3d} \r"
        sys.stdout.write(status_output.format(framenum, framenum/kwargs['fps'], diffsum, diffmax, npixabovethresh))
        sys.stdout.flush()

        above_thresh.append(npixabovethresh)

        if npixabovethresh > kwargs['numthresh']:
            #import pdb; pdb.set_trace()
            cv2.imshow('frame',cv2.resize(frame, minisize))
            cv2.imshow( winName, cv2.resize(dimg, minisize) )
            keypress = cv2.waitKey(1) & 0xFF
            while wait_to_continue and keypress != ord('q') and keypress != ord(' '):
                keypress = cv2.waitKey(1000) & 0xFF
            if keypress == ord('q'): break

        t_minus = t
        t = t_plus
        t_plus = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        framenum += 1

    # Save the list containing the number of pixels above threshold for each frame to a pickle file
    import pickle
    pickle.dump( above_thresh, open( videofile + ".p", "wb" ) )

    cap.release()
    cv2.destroyAllWindows()

    print("Goodbye")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('videofile')
    parser.add_argument('--downscale', default=settings['downscale'],  type=int, choices=(1, 2, 3, 4) )
    parser.add_argument('--skipframes',default=settings['skipframes'], type=int)
    parser.add_argument('--threshold', default=settings['threshold'],  type=int)
    parser.add_argument('--numthresh', default=settings['numthresh'],  type=int)
    parser.add_argument('--fps',       default=settings['fps'],        type=float)
    args = parser.parse_args()
    settings.update(vars(args))

    video_analysis(**settings)

if __name__ == "__main__": main()
