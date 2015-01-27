#!/usr/bin/python
# vim: sts=4: ts=4: sw=4:
import sys
import argparse
import cv2
import numpy as np
import random

class Glitcher:
    """
    Inject, distort, disturb, intersect, explode an image file with various
    methods of destruction
    """
    def __init__(self, img=None, filename=None):
        """ Run the glitcher """
        self.bitmap = None
        if img:
            self.bitmap = img
        if filename:
            self.bitmap = cv2.imread( filename )

    def glitch(self, amount):
        """ Run the glitcher """
        if not self.bitmap.any():
            raise Exception('No image loaded')
        width, height, colors = self.bitmap.shape

        for i in range(0, amount):
            line = random.randint( 0, height-1 )
            shift = random.randint( 0, amount )
            self.bitmap[ line ] = np.roll( self.bitmap[ line ], shift, 0 )

    def save(self, outfile):
        """ Save the scrambled files """
        cv2.imwrite( outfile, self.bitmap )

if __name__ == '__main__':
    parser = argparse.ArgumentParser( description='Image Scrambler' )
    parser.add_argument('imagefile', metavar='imagefile', type=str,
        help='filename of image to be scrambled')
    parser.add_argument('-o', '--outfile', dest='outfile', action='store', default='output.png',
        help='image file to write output to')
    parser.add_argument('-a', '--amount', dest='amount', type=int, action='store', default='9',
        help='image file to write output to')
    args = parser.parse_args()

    glitcher = Glitcher( filename=args.imagefile )
    try:
        glitcher.glitch( args.amount )
    except Exception, e:
        print e
        sys.exit(-1)

    glitcher.save( args.outfile )
