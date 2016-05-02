#!/usr/bin/env python

import os
import sys
import argparse
import cv2
import numpy as np
from audiopack import loadwav, audio_chunks

"""
Emerge Image from junk-noise backdrop
"""


def save_frame(args, number, frame):
    cv2.imwrite(os.path.join(args.outdir, "frame_%06d.png"%number), frame)


#def process_multichannel(frame, block, amount, height, blocksize, channels):
#    for channel in block.T:
#        shift = np.interp(np.arange(height), np.arange(blocksize), channel)
#        for line in xrange(height):
#            frame[line] += np.roll(frame[line], int(shift[line]*amount), 0) / channels
#    return frame

def junkline(junkchunk):
    return [(px, px, px) for px in junkchunk]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Emerge Image from Noise backdrop')
    parser.add_argument('imagefile', metavar='imagefile', type=str,
        help='image or directory with images to be scrambled'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frames to'
    )
    parser.add_argument('-s', '--soundfile', dest='soundfile', action='store',
        help='soundfile'
    )
    parser.add_argument('-j', '--junkfile', dest='junkfile', action='store',
        help='junkfile'
    )
    parser.add_argument('-m', '--multichannel', dest='multichannel', action='store_true',
        help='multichannel'
    )
    parser.add_argument('-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='video framerate'
    )
    parser.add_argument('-t', '--threshold', dest='threshold', type=float, action='store', default='0.1',
        help='where to split noise and signal'
    )
    parser.add_argument('-O', '--offset', dest='offset', type=int, action='store', default='0',
        help='where to start scraping the junkyard'
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
    except Exception, e:
        print "Problem with the Soundfile"
        print e
        sys.exit(-1)
    print "audiofile loaded"

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
        print "Problem loading the first Imagefile"
        sys.exit(-1)
    print "image loaded"

    junk = np.fromfile(args.junkfile, dtype='u1')
    np.roll(junk, args.offset)
    print "junk loaded"

    height, width, colors = bitmap.shape
    blocksize             = meta.rate // args.fps
    blocks                = meta.samples // blocksize

    juncnt = 0
    for n, b in enumerate(audio_chunks(data.T[0], blocksize), 1):
        #if os.path.exists(os.path.join(args.outdir, "frame_%06d.png"%n)):
        #    continue
        if args.length is not None and n-args.start_frame > args.length:
            continue
        if n < args.start_frame or n > blocks:
            continue
        elif len(imagefiles) > 1:
            bitmap = cv2.imread(imagefiles[n-1 % len(imagefiles)])

        frame = bitmap.copy()
        shift = np.interp(np.arange(height), np.arange(blocksize), b)
        for line in xrange(height):
            if shift[line] * shift[line] > args.threshold:
                frame[line] = frame[line]
            else:
                frame[line] = junkline(junk[juncnt:juncnt+width])
                juncnt = (juncnt + width) % len(junk)
        print n
        save_frame(args, n, frame)
