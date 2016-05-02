from collections import namedtuple
from scipy.io import wavfile
#from drawSVG import Line
import numpy as np

"""
An audio-visualizing library
"""

#
##
### Audio data functions
##
#

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

def loadwav(filename):
    rate, raw = wavfile.read(filename)
    data = pcm2float(raw, 'float64')
    meta = namedtuple('meta', ['rate', 'samples', 'seconds', 'channels'])
    meta.samples = len(data)
    meta.seconds = meta.samples / float(rate)
    meta.rate    = rate
    try:
        meta.channels = data.shape[1]
    except IndexError:
        meta.channels = 1
    return meta, data

def audio_chunks(data, blocksize):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(data), blocksize):
        block = data[i:i+blocksize]
        if len(block) < blocksize:
            pad = blocksize-len(block)
            yield np.lib.pad(block, (0, pad), 'constant')
        yield block

#
##
### Visualization functions ###
##
#
#def scatter(scene, data, width, height, reflect):
#    lastX = width * 0.5
#    lastY = height * 0.5
#    for i in xrange(len(data)/2):
#        px = data[i*2:i*2+2][0]
#        py = data[i*2:i*2+2][1]
#        x  = width * 0.5 + width * px * 0.5 * reflect[0]
#        y  = height * 0.5 + height * py * 0.5 * reflect[1]
#
#        scene.add(Line((lastX, lastY), (x, y)))
#        lastX = x
#        lastY = y
#
#    return scene
#
#def osci(scene, data, width, height, reflect):
#    lastX  = 0.
#    lastY  = height * 0.5
#    points = len(data)
#    for i in xrange(points):
#        x  = i * width / points
#        y  = height * data[i] + height * 0.5
#
#        scene.add(Line((lastX, lastY), (x, y)))
#        lastX = x
#        lastY = y
#
#    return scene
#
#
#
#def render_frame(scene, data, plotter=None, width=600, height=400, reflect=(1,1)):
#    """ Wrap the renderer so different plugin plotters can be used """
#    try:
#        plotter = globals()[plotter]
#    except KeyError:
#        plotter = scatter
#    return plotter(scene, data, width, height, reflect)
