#!/usr/bin/env python
import os
import sys
import argparse
from collections import namedtuple
import cv2
import numpy as np
import scipy.io.wavfile as wavfile

"""
Distort image(s) with a soundwave.
TODO: multichannel distortion
      the problem here is, that just dividing by number of channels
      and summing it up, does not add up to the correct brightness
      and everything gets horribly slow
      distorting the same data twice looks interesting
"""

def pcm2float(sig, dtype='float64'):
    """Convert PCM signal to floating point with a range from -1 to 1.
    Use dtype='float32' for single precision.
    Parameters
    ----------
    sig : array_like
        Input array, must have integral type.
    dtype : data type, optional
        Desired (floating point) data type.
    Returns
    -------
    numpy.ndarray
        Normalized floating point data.
    See Also
    --------
    float2pcm, dtype
    """
    sig = np.asarray(sig)
    if sig.dtype.kind not in 'iu':
        raise TypeError("'sig' must be an array of integers")
    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("'dtype' must be a floating point type")

    i = np.iinfo(sig.dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig.astype(dtype) - offset) / abs_max


def load_soundfile(args):
    rate, data = wavfile.read(args.soundfile)
    normalized = pcm2float(data, 'float64')
    print "Samplerate: %d"%rate
    samples = len(normalized)
    length  = samples/float(rate)
    try:
        channels = data.shape[1]
        print "Channels: %d"%(channels)
    except IndexError:
        channels = 1
        print "Channels: 1"
    print "Length: %d samples, %f seconds"%(samples, length)
    meta = namedtuple('meta', ['rate', 'samples', 'length', 'channels'])
    return meta(rate, samples, length, channels), normalized


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


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
    parser = argparse.ArgumentParser(description='Image Scrambler')
    parser.add_argument('imagefile', metavar='imagefile', type=str,
        help='image or directory with images to be scrambled'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frame images to'
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
    args = parser.parse_args()

    try:
        meta, data = load_soundfile(args)
    except Exception, e:
        print "Problem with the Soundfile"
        print e
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
        print "Problem loading the first Imagefile"
        sys.exit(-1)

    junk = np.fromfile(args.junkfile, dtype='u1')

    height, width, colors = bitmap.shape
    blocksize             = meta.rate // args.fps
    blocks                = meta.samples // blocksize

    juncnt = 0
    for n, b in enumerate(chunks(data, blocksize)):
        if n > 0 and len(imagefiles) > 1:
            bitmap = cv2.imread(imagefiles[n % len(imagefiles)])
        frame = bitmap.copy()
        if len(b) < blocksize:
            b = np.lib.pad(b, ((blocksize-len(b)) // 2), 'constant')
        shift = np.interp(np.arange(height), np.arange(blocksize), b.T[0])
        for line in xrange(height):
            if shift[line] * shift[line] > args.threshold:
                frame[line] = frame[line]
            else:
                frame[line] = junkline(junk[juncnt:juncnt+width])
                juncnt = (juncnt + width) % len(junk)

        save_frame(args, n, frame)
