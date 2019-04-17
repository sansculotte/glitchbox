#!/usr/bin/env python
from __future__ import division
import os
import sys
import argparse
import cv2
#from multiprocessing import Pool
import numpy as np
from audiopack import loadwav, audio_chunks
"""
Distort image(s) horizontally by a soundwave.
"""


def save_frame(outdir, number, frame):
    print("writing frame %06d" % number)
    cv2.imwrite(os.path.join(outdir, "frame_%06d.png" % number), frame)

def process_multichannel(frame, block, amount, height, blocksize, channels):
    for channel in block.T:
        shift = np.interp(np.arange(height), np.arange(blocksize), channel)
        for line in range(height):
            frame[line] += np.roll(frame[line], int(shift[line]*amount), 0) / channels
    return frame

def process(frame, block, amount, height, blocksize):
    shift = np.interp(np.arange(height), np.arange(blocksize), b)
    for line in range(height):
        frame[line] = np.roll(frame[line], int(shift[line]*args.amount), 0)
    return frame


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='Image Scrambler' )
    parser.add_argument('imagefile', metavar='imagefile', type=str,
        help='image or directory with images to be scrambled'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frame images to'
    )
    parser.add_argument('-s', '--soundfile', dest='soundfile', action='store',
        help='soundfile'
    )
    parser.add_argument('-m', '--multichannel', dest='multichannel', action='store_true',
        help='multichannel'
    )
    parser.add_argument('-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='video framerate'
    )
    parser.add_argument('-a', '--amount', dest='amount', type=int, action='store', default=9,
        help='fuckup factor, the bigger the more destroyed'
    )
    parser.add_argument('--start-frame', dest='start_frame', type=int, action='store', default=1,
        help='frame to start from, starting at 1'
    )
    parser.add_argument('--length', dest='length', type=int, action='store',
        help='number of frames to glitch'
    )
    args = parser.parse_args()

    try:
        meta, data = loadwav(args.soundfile)
    except Exception as e:
        print("Problem with the Soundfile")
        print(e)
        sys.exit(-1)

    if os.path.isdir(args.imagefile):
        imagefiles = sorted([
            os.path.join(args.imagefile, f)
            for f in os.listdir(args.imagefile)
            if os.path.isfile(os.path.join(args.imagefile, f))
        ])
    else:
        imagefiles = [args.imagefile]

    bitmap = cv2.imread(imagefiles[0])
    if bitmap is None:
        print("Problem with the first Imagefile")
        sys.exit(-1)

    height, width, colors = bitmap.shape
    blocksize             = meta.rate / args.fps
    blocks                = meta.samples / blocksize

    for n, b in enumerate(audio_chunks(data, blocksize), 1):

#        if os.path.exists(os.path.join(args.outdir, "frame_%06d.png"%n)):
#            continue
        if args.length is not None and n-args.start_frame >= args.length:
            continue
        if n < args.start_frame or n > blocks:
            continue
        elif len(imagefiles) > 1:
            bitmap = cv2.imread(imagefiles[n-1 % len(imagefiles)])

        frame = bitmap.copy()
        if args.multichannel and meta.channels > 1:
            frame = process_multichannel(frame, b, args.amount, height,
                                         blocksize, meta.channels)
        else:
            if meta.channels > 1:
                b = b.T[0]
            frame = process(frame, b, args.amount, height, blocksize)

        save_frame(args.outdir, n, frame)
