#!/usr/bin/env python
import os
import sys
import argparse
import cv2
import numpy as np
import scipy.io.wavfile as wavfile


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
    length = {}
    rate, data = wavfile.read(args.soundfile)
    normalized = pcm2float(data, 'float64')
    print "Samplerate: %d"%rate
    length['samples'] = len(normalized)
    length['seconds'] = length['samples']/float(rate)
    try:
        channels = data.shape[1]
        print "Channels: %d"%(channels)
    except IndexError:
        channels = 1
        print "Channels: 1"
    print "Length: %d samples, %f seconds"%(length['samples'], length['seconds'])
    return {'rate':rate, 'length':length, 'channels':channels}, normalized


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def save_frame(args, number, frame):
    cv2.imwrite(os.path.join(args.outdir, "frame_%06d.png"%number), frame)


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='Image Scrambler' )
    parser.add_argument('imagefile', metavar='imagefile', type=str,
        help='filename of image to be scrambled'
    )
    parser.add_argument('-o', '--outdir', dest='outdir', action='store', default='/tmp',
        help='directory to write frame images to'
    )
    parser.add_argument('-s', '--soundfile', dest='soundfile', action='store',
        help='soundfile'
    )
    parser.add_argument('-f', '--fps', dest='fps', type=int, action='store', default=25,
        help='video framerate'
    )
    parser.add_argument('-a', '--amount', dest='amount', type=int, action='store', default='9',
        help='fuckup factor, the bigger the more destroyed'
    )
    parser.add_argument('-t', '--tremble', dest='tremble', type=int, action='store',
        help='additional randomness'
    )
    args = parser.parse_args()

    try:
        meta, data = load_soundfile(args)
    except Exception, e:
        print "Problem with the Soundfile"
        print e
        sys.exit(-1)


    bitmap = cv2.imread(args.imagefile)
    if bitmap is None:
        print "Problem with the Imagefile"
        sys.exit(-1)

    height, width, colors = bitmap.shape
    blocksize             = meta['rate'] // args.fps
    blocks                = meta['length']['samples'] // blocksize
    # reduce audio samples to image height, scrolling
    # image height 1080, audio samples 1764

    for n, b in enumerate(chunks(data, blocksize)):
        frame = bitmap.copy()
        if meta['channels'] > 1:
            b = b.T[0]
        if len(b) < blocksize:
            b = np.lib.pad(b, ((blocksize-len(b)) // 2), 'constant')
        shift = np.interp(np.arange(height), np.arange(blocksize), b)
        for line in xrange(height):
            frame[line] = np.roll(frame[line], int(shift[line]*args.amount), 0)

        save_frame(args, n, frame)

# ignore channels for the time being
#    for i, channel in enumerate(data.T):
#        pass
