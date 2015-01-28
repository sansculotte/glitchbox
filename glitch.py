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
        self.width, self.height, self.colors = self.bitmap.shape
        self.line_glitch( amount )
        self.block_glitch( amount )

    def line_glitch(self, amount):
        for i in range(0, amount):
            line = random.randint( 0, self.height-1 )
            shift = random.randint( 0, amount ) - amount / 2
            self.bitmap[ line ] = np.roll( self.bitmap[ line ], shift, 0 )

    def block_glitch(self, amount):
        margin = ( self.width/10, self.height/10 )
        for i in range(0, amount):
            block_x = (random.randint( 0, self.width-margin[0] ), random.randint( 1, margin[0] ))
            block_y = (random.randint( 0, self.height-margin[1] ), random.randint( 1, margin[1] ))
            x = max( 0, block_x[0] + random.randint(0, amount) - amount/2 )
            y = max( 0, block_y[0] + random.randint(0, amount) - amount/2 )
            while x+block_x[1] < self.width or random.randint(0, amount) > 0:
                try:
                    if random.randint(0,10)>5:
                        self.bitmap[ y:y+block_y[1], x:x+block_x[1] ] = self.bitmap[ block_y[0]:sum(block_y), block_x[0]:sum(block_x) ]
                    else:
                        self.bitmap[ x:x+block_x[1], y:y+block_y[1] ] = self.bitmap[ block_y[0]:sum(block_y), block_x[0]:sum(block_x) ]
                except:
                    pass
                x += block_x[1] + random.randint(0, 2) - 1
                y += random.randint(0, 2) - 1


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
